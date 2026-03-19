"""
Movie playback controller.

Handles single movie playback, resume points, and
now-playing info display.

Logging:
    Logger: 'playback'
    Key events:
        - playback.start (INFO): Movie playback started
        - playback.resume (INFO): Resumed from position
    See LOGGING.md for full guidelines.
"""
from __future__ import annotations

from typing import Any, Dict, Optional, TYPE_CHECKING

import xbmc

from resources.lib.utils import get_logger, json_query
from resources.lib.data.queries import build_play_movie_query

if TYPE_CHECKING:
    from resources.lib.utils import StructuredLogger

# Module-level logger
_log: Optional[StructuredLogger] = None


def _get_log() -> StructuredLogger:
    """Get or create the module logger."""
    global _log
    if _log is None:
        _log = get_logger('playback')
    return _log


def play_movie(movie: Dict[str, Any], resume: bool = False) -> None:
    """Play a single movie.

    Args:
        movie: Movie dict with at minimum 'movieid' and 'title'.
        resume: If True, resume from the last position.
    """
    log = _get_log()
    movie_id = movie.get("movieid", 0)
    title = movie.get("title", "Unknown")
    position = 0.0

    if resume:
        resume_info = movie.get("resume", {})
        position = resume_info.get("position", 0) if isinstance(resume_info, dict) else 0
        if position > 0:
            log.info("Resuming movie", event="playback.resume",
                     title=title, movieid=movie_id,
                     position_seconds=int(position))
        else:
            resume = False

    if not resume:
        log.info("Playing movie", event="playback.start",
                 title=title, movieid=movie_id)

    # Start playback via JSON-RPC
    query = build_play_movie_query(movie_id)
    json_query(query, return_result=False)

    # If resuming, seek to the saved position after playback starts
    if resume:
        # Wait briefly for the player to initialize
        xbmc.sleep(500)
        player = xbmc.Player()
        if player.isPlaying():
            player.seekTime(position)


def get_resume_info(movie: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Get resume information for a movie.

    Args:
        movie: Movie dict with resume data.

    Returns:
        Dict with 'position' and 'total' keys, or None if no resume point.
    """
    resume = movie.get("resume", {})
    if not isinstance(resume, dict):
        return None

    position = resume.get("position", 0)
    total = resume.get("total", 0)

    if position > 0 and total > 0:
        remaining_seconds = int(total - position)
        remaining_minutes = remaining_seconds // 60
        return {
            "position": position,
            "total": total,
            "remaining_seconds": remaining_seconds,
            "remaining_minutes": remaining_minutes,
        }
    return None
