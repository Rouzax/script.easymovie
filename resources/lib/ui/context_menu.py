"""
Context menu for the browse window.

Provides additional actions when the user presses the context
menu button on a movie in the browse view.

Logging:
    Logger: 'ui'
    Key events:
        - ui.context (DEBUG): Context menu action selected
    See LOGGING.md for full guidelines.
"""
from __future__ import annotations

from typing import Any, Dict, Optional, TYPE_CHECKING

import xbmcgui

from resources.lib.utils import get_logger, lang

if TYPE_CHECKING:
    from resources.lib.utils import StructuredLogger

# Context menu action constants
CONTEXT_PLAY = 0
CONTEXT_PLAY_SET = 1
CONTEXT_MOVIE_INFO = 2

# Module-level logger
_log: Optional[StructuredLogger] = None


def _get_log() -> StructuredLogger:
    """Get or create the module logger."""
    global _log
    if _log is None:
        _log = get_logger('ui')
    return _log


def show_context_menu(movie: Dict[str, Any]) -> Optional[int]:
    """Show a context menu for a movie.

    Args:
        movie: The movie dict for the focused item.

    Returns:
        Action constant (CONTEXT_PLAY, etc.) or None if cancelled.
    """
    log = _get_log()

    items = [lang(32305)]  # "Play"

    # Add "Play Full Set" if movie is in a set
    set_name = movie.get("set", "")
    if set_name:
        items.append(f"{lang(32306)} ({set_name})")

    items.append(lang(32307))  # "Movie Info"

    dialog = xbmcgui.Dialog()
    result = dialog.contextmenu(items)

    if result < 0:
        return None

    # Map result index to action
    if result == 0:
        log.debug("Context: Play", event="ui.context", action="play")
        return CONTEXT_PLAY
    elif result == 1 and set_name:
        log.debug("Context: Play Set", event="ui.context", action="play_set")
        return CONTEXT_PLAY_SET
    else:
        log.debug("Context: Movie Info", event="ui.context", action="info")
        return CONTEXT_MOVIE_INFO
