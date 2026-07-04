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

from typing import Any, Dict, List, Optional, Tuple, cast

import xbmcgui

from resources.lib.constants import ACTION_NAV_BACK, ACTION_PREVIOUS_MENU, ADDON_ID
from resources.lib.ui.skin_fonts import ensure_generated
from resources.lib.utils import get_logger, lang

# Language string ids (see strings.po)
STR_GENRE = 32012
STR_PLAY = 32312
STR_YEAR = 32516
STR_RATING = 32517
STR_RUNTIME = 32518
STR_RATED = 32717

# Module-level logger
log = get_logger('ui')


def format_runtime(seconds: int) -> str:
    """Format a runtime in seconds as '1h 36m' or '45m' ('' when zero)."""
    minutes = seconds // 60 if seconds else 0
    if minutes <= 0:
        return ""
    if minutes >= 60:
        return "%dh %dm" % (minutes // 60, minutes % 60)
    return "%dm" % minutes


def format_rating(rating: float, votes: str = "") -> str:
    """Format rating as '7.5 (2,558 votes)' ('' when no rating).

    No star glyph: the info dialog shows a "Rating" label beside this value,
    so the star is redundant (and it avoids the Unicode-font dependency).
    """
    if not rating or rating <= 0:
        return ""
    text = "%.1f" % rating
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


def build_cast_items(cast_members: List[Dict[str, Any]],
                     limit: int = 10) -> List[Tuple[str, str, str]]:
    """Map cast dicts to (name, role, thumbnail), capped at `limit`."""
    items: List[Tuple[str, str, str]] = []
    for member in cast_members[:limit]:
        items.append((member.get("name", ""), member.get("role", ""),
                      member.get("thumbnail", "")))
    return items


# Control ids (match script-easymovie-info.xml)
INFO_TITLE = 2
INFO_TAGLINE = 5
INFO_PLOT = 6
INFO_PLAY = 10
INFO_POSTER = 20
INFO_FANART = 40
INFO_CAST_LIST = 100
INFO_META_LIST = 500

INFO_RESULT_PLAY = "__info_play__"


class InfoDialog(xbmcgui.WindowXMLDialog):
    """Fullscreen movie info dialog rendered from full movie details."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._addon_id: str = ADDON_ID
        self.movie: Dict[str, Any] = {}
        self.details: Dict[str, Any] = {}
        self.result: Optional[str] = None

    def onInit(self) -> None:
        from resources.lib.ui import apply_theme
        apply_theme(self, self._addon_id)
        d = self.details
        art = d.get("art", {}) or {}

        fanart = art.get("fanart", "")
        if fanart:
            cast(xbmcgui.ControlImage, self.getControl(INFO_FANART)).setImage(fanart)
        poster = art.get("poster", "") or art.get("thumb", "")
        if poster:
            cast(xbmcgui.ControlImage, self.getControl(INFO_POSTER)).setImage(poster)
        cast(xbmcgui.ControlLabel, self.getControl(INFO_TITLE)).setLabel(
            d.get("title", ""))
        cast(xbmcgui.ControlLabel, self.getControl(INFO_TAGLINE)).setLabel(
            d.get("tagline", ""))
        cast(xbmcgui.ControlTextBox, self.getControl(INFO_PLOT)).setText(
            d.get("plot", ""))

        meta = cast(xbmcgui.ControlList, self.getControl(INFO_META_LIST))
        meta.reset()
        for string_id, value in build_metadata_rows(d):
            li = xbmcgui.ListItem(lang(string_id, self._addon_id))
            li.setLabel2(value)
            meta.addItem(li)

        cast_list = cast(xbmcgui.ControlList, self.getControl(INFO_CAST_LIST))
        cast_list.reset()
        for name, role, thumb in build_cast_items(d.get("cast", [])):
            li = xbmcgui.ListItem(name)
            li.setLabel2(role)
            if thumb:
                li.setArt({"thumb": thumb})
            cast_list.addItem(li)

        cast(xbmcgui.ControlButton, self.getControl(INFO_PLAY)).setLabel(
            lang(STR_PLAY, self._addon_id))

        log.info("Info dialog opened", event="ui.info.open",
                 title=d.get("title", ""), movieid=self.movie.get("movieid", 0))
        self.setFocus(self.getControl(INFO_PLAY))

    def onClick(self, controlId: int) -> None:
        if controlId == INFO_PLAY:
            self.result = INFO_RESULT_PLAY
            log.info("Play from info dialog", event="ui.info.play",
                     movieid=self.movie.get("movieid", 0))
            self.close()

    def onAction(self, action) -> None:
        if action.getId() in (ACTION_NAV_BACK, ACTION_PREVIOUS_MENU):
            self.result = None
            self.close()


def show_info_dialog(movie: Dict[str, Any], details: Dict[str, Any],
                     addon_id: str = ADDON_ID) -> Optional[str]:
    """Show the info dialog. Returns INFO_RESULT_PLAY if Play was pressed."""
    path = ensure_generated(addon_id)
    dialog = InfoDialog('script-easymovie-info.xml', path, 'Default', '1080i')
    dialog._addon_id = addon_id
    dialog.movie = movie
    dialog.details = details
    dialog.doModal()
    return dialog.result
