"""
Persistent storage for EasyMovie data.

Manages suggested movie history, playback tracking, and
last-used filter answers. Data is stored as JSON in the
addon's userdata directory.

Logging:
    Logger: 'data'
    Key events:
        - history.save (DEBUG): Data saved to disk
        - history.prune (DEBUG): Old entries pruned
    See LOGGING.md for full guidelines.
"""
import json
import os
import time
from typing import Any, Dict, List, Set


class StorageManager:
    """Manages persistent JSON storage for EasyMovie.

    Data structure:
        {
            "suggested": [{"movieid": int, "timestamp": float}, ...],
            "started": [{"movieid": int, "timestamp": float}, ...],
            "last_filters": {...}
        }
    """

    def __init__(self, path: str) -> None:
        """Initialize storage, loading existing data if available.

        Args:
            path: Full path to the JSON storage file.
        """
        self._path = path
        self._data: Dict[str, Any] = {
            "suggested": [],
            "started": [],
            "last_filters": {},
        }
        self._load()

    def _load(self) -> None:
        """Load data from disk."""
        if os.path.exists(self._path):
            try:
                with open(self._path, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                if isinstance(loaded, dict):
                    self._data["suggested"] = loaded.get("suggested", [])
                    self._data["started"] = loaded.get("started", [])
                    self._data["last_filters"] = loaded.get("last_filters", {})
            except (json.JSONDecodeError, IOError, OSError):
                try:
                    from resources.lib.utils import get_logger
                    get_logger('data').warning(
                        "Storage file corrupt or unreadable",
                        event="history.load_fail",
                        path=self._path)
                except Exception:
                    pass

    def save(self) -> None:
        """Write data to disk."""
        try:
            dir_path = os.path.dirname(self._path)
            if dir_path and not os.path.exists(dir_path):
                os.makedirs(dir_path, exist_ok=True)
            with open(self._path, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2)
        except (IOError, OSError) as exc:
            try:
                from resources.lib.utils import get_logger
                get_logger('data').warning("Failed to save storage",
                                           event="history.save_fail",
                                           path=self._path, error=str(exc))
            except Exception:
                pass

    def add_suggested(self, movieid: int, title: str = "") -> None:
        """Record a movie as suggested (for re-suggestion avoidance).

        Args:
            movieid: The Kodi movie ID.
            title: Movie title (stored for debugging, not used in logic).
        """
        # Avoid duplicates
        existing_ids = {s.get("movieid", 0) for s in self._data["suggested"]}
        if movieid not in existing_ids:
            self._data["suggested"].append({
                "movieid": movieid,
                "title": title,
                "timestamp": time.time(),
            })
            self.save()

    def get_suggested_ids(self) -> Set[int]:
        """Get all suggested movie IDs."""
        return {s.get("movieid", 0) for s in self._data["suggested"]}

    def clear_suggested(self) -> None:
        """Remove all suggested entries."""
        if self._data["suggested"]:
            self._data["suggested"] = []
            self.save()

    def validate_suggested(self, movies: List[Dict[str, Any]]) -> None:
        """Remove suggested entries where the ID was reused for a different movie.

        Kodi reuses movie IDs after deletion. By comparing stored titles
        against current library titles, we detect and remove stale entries.

        Args:
            movies: Current library movies (must include movieid and title).
        """
        title_by_id = {m.get("movieid", 0): m.get("title", "") for m in movies}
        before = len(self._data["suggested"])
        self._data["suggested"] = [
            s for s in self._data["suggested"]
            if s.get("title") and s.get("movieid", 0) in title_by_id
            and title_by_id[s.get("movieid", 0)] == s.get("title")
        ]
        after = len(self._data["suggested"])
        if before != after:
            self.save()

    def prune_suggested(self, max_age_hours: int) -> None:
        """Remove suggested entries older than max_age_hours.

        Args:
            max_age_hours: Maximum age in hours.
        """
        cutoff = time.time() - (max_age_hours * 3600)
        before = len(self._data["suggested"])
        self._data["suggested"] = [
            s for s in self._data["suggested"]
            if s.get("timestamp", 0) >= cutoff
        ]
        after = len(self._data["suggested"])
        if before != after:
            self.save()

    def add_started(self, movieid: int, title: str = "") -> None:
        """Record a movie as started through EasyMovie.

        Args:
            movieid: The Kodi movie ID.
            title: Movie title (stored for debugging, not used in logic).
        """
        existing_ids = {s.get("movieid", 0) for s in self._data["started"]}
        if movieid not in existing_ids:
            self._data["started"].append({
                "movieid": movieid,
                "title": title,
                "timestamp": time.time(),
            })
            self.save()

    def get_started_ids(self) -> Set[int]:
        """Get all started movie IDs."""
        return {s.get("movieid", 0) for s in self._data["started"]}

    def save_last_filters(self, filters: Dict[str, Any]) -> None:
        """Save wizard filter answers for next session.

        Args:
            filters: Dict of filter answers.
        """
        self._data["last_filters"] = filters
        self.save()

    def load_last_filters(self) -> Dict[str, Any]:
        """Load last wizard filter answers."""
        return self._data.get("last_filters", {})
