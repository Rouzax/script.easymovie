"""
Playback monitor for movie set continuation.

Monitors playback during playlist sessions and prompts
the user when a set-member movie finishes.

Logging:
    Logger: 'playback'
    Key events:
        - continuation.prompt (INFO): Showing continuation dialog
        - continuation.accepted (INFO): User chose to watch next in set
        - continuation.declined (INFO): User declined, continuing playlist
    See LOGGING.md for full guidelines.
"""
from __future__ import annotations

import threading
from typing import Any, Dict, Optional, TYPE_CHECKING, cast

import xbmc
import xbmcgui
import xbmcaddon

from resources.lib.constants import (
    ADDON_ID,
    CONTINUATION_DEFAULT_CONTINUE_SET,
)
from resources.lib.utils import get_logger, json_query, lang
from resources.lib.data.queries import build_add_movie_query
from resources.lib.data.movie_sets import get_next_in_set

if TYPE_CHECKING:
    from resources.lib.utils import StructuredLogger

# Control IDs for the continuation dialog
CONT_HEADING = 1
CONT_MESSAGE = 2
CONT_TIMER = 3
CONT_SUBTITLE = 4
CONT_YES = 10
CONT_NO = 11
CONT_POSTER = 20

# Kodi actions
ACTION_NAV_BACK = 92
ACTION_PREVIOUS_MENU = 10

# Module-level logger
_log: Optional[StructuredLogger] = None


def _get_log() -> StructuredLogger:
    """Get or create the module logger."""
    global _log
    if _log is None:
        _log = get_logger('playback')
    return _log


class ContinuationDialog(xbmcgui.WindowXMLDialog):
    """Countdown dialog for movie set continuation prompts."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._addon_id: str = ADDON_ID
        self._heading = "EasyMovie"
        self._message = ""
        self._subtitle = ""
        self._yes_label = ""
        self._no_label = ""
        self._poster = ""
        self._duration = 20
        self._default_yes = True
        self._confirmed = False
        self._timer_thread: Optional[threading.Thread] = None
        self._cancel_timer = False

    def configure(
        self,
        message: str,
        subtitle: str,
        yes_label: str,
        no_label: str,
        poster: str = "",
        duration: int = 20,
        default_yes: bool = True,
    ) -> None:
        """Configure the dialog before showing."""
        self._message = message
        self._subtitle = subtitle
        self._yes_label = yes_label
        self._no_label = no_label
        self._poster = poster
        self._duration = duration
        self._default_yes = default_yes

    @property
    def confirmed(self) -> bool:
        """Whether the user chose to watch next."""
        return self._confirmed

    def onInit(self):
        """Set up the dialog."""
        from resources.lib.ui import apply_theme
        apply_theme(self, self._addon_id)

        cast(xbmcgui.ControlLabel, self.getControl(CONT_HEADING)).setLabel(self._heading)
        cast(xbmcgui.ControlLabel, self.getControl(CONT_MESSAGE)).setLabel(self._message)
        cast(xbmcgui.ControlLabel, self.getControl(CONT_SUBTITLE)).setLabel(self._subtitle)
        cast(xbmcgui.ControlButton, self.getControl(CONT_YES)).setLabel(self._yes_label)
        cast(xbmcgui.ControlButton, self.getControl(CONT_NO)).setLabel(self._no_label)

        if self._poster:
            try:
                cast(xbmcgui.ControlImage, self.getControl(CONT_POSTER)).setImage(self._poster)
            except RuntimeError:
                pass

        if self._duration > 0:
            cast(xbmcgui.ControlLabel, self.getControl(CONT_TIMER)).setLabel(
                f"Auto-selecting in {self._duration}s"
            )
            # Focus the non-default button
            if self._default_yes:
                self.setFocus(self.getControl(CONT_NO))
            else:
                self.setFocus(self.getControl(CONT_YES))

            # Start countdown
            self._cancel_timer = False
            self._timer_thread = threading.Thread(target=self._countdown_loop)
            self._timer_thread.daemon = True
            self._timer_thread.start()
        else:
            cast(xbmcgui.ControlLabel, self.getControl(CONT_TIMER)).setLabel('')
            self.setFocus(self.getControl(CONT_YES))

    def _countdown_loop(self) -> None:
        """Countdown timer that auto-closes the dialog."""
        remaining = self._duration
        while remaining > 0 and not self._cancel_timer:
            xbmc.sleep(1000)
            remaining -= 1
            try:
                cast(xbmcgui.ControlLabel, self.getControl(CONT_TIMER)).setLabel(
                    f"Auto-selecting in {remaining}s"
                )
            except RuntimeError:
                break

        if not self._cancel_timer:
            self._confirmed = self._default_yes
            self.close()

    def onClick(self, controlId):
        """Handle button clicks."""
        self._cancel_timer = True
        if controlId == CONT_YES:
            self._confirmed = True
            self.close()
        elif controlId == CONT_NO:
            self._confirmed = False
            self.close()

    def onAction(self, action):
        """Handle back/escape."""
        action_id = action.getId()
        if action_id in (ACTION_NAV_BACK, ACTION_PREVIOUS_MENU):
            self._cancel_timer = True
            self._confirmed = False
            self.close()


class PlaybackMonitor(xbmc.Player):
    """Monitors playback during playlist sessions for set continuation.

    Subclasses xbmc.Player to detect when a movie finishes playing.
    When a set-member movie completes, checks for the next movie in
    the set and shows a continuation prompt.
    """

    def __init__(
        self,
        set_cache: Dict[int, Dict[str, Any]],
        movies: Dict[int, Dict[str, Any]],
        continuation_duration: int = 20,
        continuation_default: int = CONTINUATION_DEFAULT_CONTINUE_SET,
        addon_id: str = ADDON_ID,
    ) -> None:
        super().__init__()
        self._set_cache = set_cache
        self._movies = movies  # movieid -> movie dict
        self._continuation_duration = continuation_duration
        self._continuation_default = continuation_default
        self._addon_id = addon_id
        self._current_movie_id: Optional[int] = None
        self._active = True

    def set_current_movie(self, movie_id: int) -> None:
        """Set the currently playing movie ID."""
        self._current_movie_id = movie_id

    def stop_monitoring(self) -> None:
        """Stop the monitor."""
        self._active = False

    def onPlayBackEnded(self) -> None:
        """Called when playback ends naturally (movie finished)."""
        if not self._active or self._current_movie_id is None:
            return
        self._check_continuation()

    def _check_continuation(self) -> None:
        """Check if we should prompt for set continuation."""
        log = _get_log()
        movie_id = self._current_movie_id
        if movie_id is None:
            return

        movie = self._movies.get(movie_id)
        if not movie:
            return

        set_id = movie.get("setid", 0)
        if not set_id or set_id not in self._set_cache:
            return

        set_details = self._set_cache[set_id]
        next_movie = get_next_in_set(set_details, movie_id)
        if not next_movie:
            return

        log.info("Showing continuation prompt", event="continuation.prompt",
                 finished_title=movie.get("title", ""),
                 next_title=next_movie.get("title", ""),
                 set_name=set_details.get("title", ""))

        # Show continuation dialog
        addon_path = xbmcaddon.Addon(self._addon_id).getAddonInfo('path')

        dialog = ContinuationDialog(
            'script-easymovie-continuation.xml',
            addon_path, 'Default', '1080i'
        )
        dialog._addon_id = self._addon_id

        finished_title = movie.get("title", "")
        next_title = next_movie.get("title", "")
        set_name = set_details.get("title", "")

        # Get poster art for next movie
        next_art = next_movie.get("art", {})
        poster = next_art.get("poster", "") if isinstance(next_art, dict) else ""

        dialog.configure(
            message=f"{lang(32319)} {finished_title}",
            subtitle=f"{next_title} {lang(32318)} {set_name}",
            yes_label=lang(32316),
            no_label=lang(32317),
            poster=poster,
            duration=self._continuation_duration,
            default_yes=(self._continuation_default == CONTINUATION_DEFAULT_CONTINUE_SET),
        )
        dialog.doModal()

        if dialog.confirmed:
            log.info("Continuation accepted", event="continuation.accepted",
                     next_title=next_title)
            # Insert next movie at front of playlist
            query = build_add_movie_query(next_movie.get("movieid", 0), position=0)
            json_query(query, return_result=False)
        else:
            log.info("Continuation declined", event="continuation.declined")
