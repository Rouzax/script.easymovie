"""
EasyMovie custom movie info dialog.

A fullscreen, addon-owned replacement for Kodi's native DialogVideoInfo, which
renders blank on Arctic-family skins because it builds its content from the
active skin's media-window context. This dialog renders from the movie's full
details on every skin, in EasyMovie's theme.

Logging:
    Logger: 'ui'
    Key events:
        - ui.info.open (INFO): Info dialog opened
        - ui.info.play (INFO): User pressed Play in the info dialog
    See LOGGING.md for full guidelines.
"""
from __future__ import annotations

from typing import Any, Dict, List, Tuple

# Language string ids (see strings.po)
STR_GENRE = 32012
STR_PLAY = 32312
STR_YEAR = 32516
STR_RATING = 32517
STR_RUNTIME = 32518
STR_RATED = 32717


def format_runtime(seconds: int) -> str:
    """Format a runtime in seconds as '1h 36m' or '45m' ('' when zero)."""
    minutes = seconds // 60 if seconds else 0
    if minutes <= 0:
        return ""
    if minutes >= 60:
        return "%dh %dm" % (minutes // 60, minutes % 60)
    return "%dm" % minutes


def format_rating(rating: float, votes: str = "") -> str:
    """Format rating as '★ 7.5 (2,558 votes)' ('' when no rating)."""
    if not rating or rating <= 0:
        return ""
    text = "★ %.1f" % rating
    digits = "".join(ch for ch in str(votes) if ch.isdigit())
    if digits:
        text += " (%s votes)" % format(int(digits), ",")
    return text


def format_genres(genres: List[str]) -> str:
    """Join genres with ' / ' (Kodi/browse convention)."""
    return " / ".join(g for g in genres if g) if genres else ""


def format_certification(mpaa: str) -> str:
    """Strip a leading 'Rated ' so 'Rated R' shows as 'R'."""
    text = (mpaa or "").strip()
    if text.lower().startswith("rated "):
        return text[len("rated "):].strip()
    return text


def build_metadata_rows(details: Dict[str, Any]) -> List[Tuple[int, str]]:
    """Build (string_id, value) rows for the metadata column, empties removed."""
    rows: List[Tuple[int, str]] = []
    year = details.get("year", 0)
    if year:
        rows.append((STR_YEAR, str(year)))
    rating = format_rating(details.get("rating", 0.0), details.get("votes", ""))
    if rating:
        rows.append((STR_RATING, rating))
    runtime = format_runtime(details.get("runtime", 0))
    if runtime:
        rows.append((STR_RUNTIME, runtime))
    cert = format_certification(details.get("mpaa", ""))
    if cert:
        rows.append((STR_RATED, cert))
    genres = format_genres(details.get("genre", []))
    if genres:
        rows.append((STR_GENRE, genres))
    return rows


def build_cast_items(cast: List[Dict[str, Any]],
                     limit: int = 10) -> List[Tuple[str, str, str]]:
    """Map cast dicts to (name, role, thumbnail), capped at `limit`."""
    items: List[Tuple[str, str, str]] = []
    for member in cast[:limit]:
        items.append((member.get("name", ""), member.get("role", ""),
                      member.get("thumbnail", "")))
    return items
