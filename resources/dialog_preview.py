#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dialog Preview Script — quickly cycle through all custom dialogs.

Usage from Kodi:
    RunScript(script.easymovie,dialog_preview)

Or from the Kodi debug console / JSON-RPC:
    {"jsonrpc":"2.0","method":"Addons.ExecuteAddon",
     "params":{"addonid":"script.easymovie","params":["dialog_preview"]},"id":1}
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

import xbmcgui
import xbmcaddon

addon = xbmcaddon.Addon()
addon_id = addon.getAddonInfo('id')
script_path = addon.getAddonInfo('path')

dialog = xbmcgui.Dialog()

# Module-level cache so "All Dialogs" doesn't re-query
_cached_movies: Optional[List[Dict[str, Any]]] = None


def _fetch_preview_movies(count: int = 20) -> List[Dict[str, Any]]:
    """Fetch random movies with art from the library.

    Returns cached result on subsequent calls.
    """
    global _cached_movies
    if _cached_movies is not None:
        return _cached_movies

    from resources.lib.utils import json_query

    query = {
        "jsonrpc": "2.0",
        "method": "VideoLibrary.GetMovies",
        "params": {
            "properties": [
                "title", "genre", "year", "rating", "runtime",
                "mpaa", "set", "setid", "playcount", "dateadded",
                "plot", "art", "file", "resume", "lastplayed",
            ],
            "sort": {"method": "random"},
            "limits": {"end": count},
        },
        "id": 1,
    }
    result = json_query(query)
    movies = result.get("movies", [])
    _cached_movies = movies
    return movies


def _find_set_movie(movies: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Find a movie that belongs to a set, or fall back to first movie."""
    for m in movies:
        if m.get("set") and m.get("setid", 0) > 0:
            return m
    if movies:
        # Fake set info on first movie
        fake = dict(movies[0])
        fake["set"] = "Preview Collection"
        fake["setid"] = 999
        return fake
    return {
        "movieid": 0, "title": "Preview Movie", "year": 2024,
        "genre": ["Drama"], "rating": 7.5, "runtime": 7200,
        "mpaa": "PG-13", "plot": "A preview movie.",
        "set": "Preview Collection", "setid": 999,
        "art": {}, "playcount": 0,
    }


def preview_confirm() -> None:
    """Show the themed ConfirmDialog."""
    from resources.lib.ui.dialogs import show_confirm_dialog
    result = show_confirm_dialog(
        "Confirm Dialog Preview",
        "This is a test message.\nDo you want to continue?",
        yes_label="Accept",
        no_label="Decline",
        addon_id=addon_id,
    )
    dialog.notification("EasyMovie Preview", "Confirm result: %s" % result)


def preview_confirm_single() -> None:
    """Show the themed ConfirmDialog in OK-only mode."""
    from resources.lib.ui.dialogs import show_confirm_dialog
    result = show_confirm_dialog(
        "Confirm (OK Only) Preview",
        "This is an information message.\nOnly an OK button is shown.",
        yes_label="OK",
        no_label="",
        addon_id=addon_id,
    )
    dialog.notification("EasyMovie Preview", "OK-only result: %s" % result)


def preview_select_single() -> None:
    """Show the themed SelectDialog in single-select mode."""
    from resources.lib.ui.dialogs import show_select_dialog
    items = [
        "First Option",
        "Second Option",
        "Third Option",
        "Fourth Option",
        "Fifth Option",
        "Sixth Option",
        "Seventh Option",
        "Eighth Option",
    ]
    result = show_select_dialog(
        "Single Select Preview", items,
        multi_select=False, addon_id=addon_id,
    )
    dialog.notification("EasyMovie Preview", "Selected: %s" % result)


def preview_select_multi() -> None:
    """Show the themed SelectDialog in multi-select mode."""
    from resources.lib.ui.dialogs import show_select_dialog
    items = [
        "Action",
        "Comedy",
        "Drama",
        "Horror",
        "Sci-Fi",
        "Thriller",
        "Animation",
        "Documentary",
    ]
    result = show_select_dialog(
        "Multi Select Preview", items,
        multi_select=True, preselected=[1, 3, 5],
        addon_id=addon_id,
    )
    dialog.notification("EasyMovie Preview", "Selected: %s" % result)


def preview_browse() -> None:
    """Show the BrowseWindow with real movies from the library."""
    movies = _fetch_preview_movies()
    if not movies:
        dialog.ok("EasyMovie Preview",
                   "No movies found in the library.\n"
                   "Browse preview requires a populated movie library.")
        return

    from resources.lib.ui.browse_window import show_browse_window
    from resources.lib.constants import VIEW_POSTER_GRID

    result = show_browse_window(movies, VIEW_POSTER_GRID, addon_id)
    if result is None:
        dialog.notification("EasyMovie Preview", "Browse: closed")
    elif isinstance(result, dict):
        title = result.get("title", result.get("movie", {}).get("title", ""))
        dialog.notification("EasyMovie Preview", "Browse: %s" % title)
    else:
        dialog.notification("EasyMovie Preview", "Browse: %s" % result)


def preview_context_menu() -> None:
    """Show the ContextMenuWindow with a movie that has a set."""
    movies = _fetch_preview_movies()
    movie = _find_set_movie(movies)

    from resources.lib.ui.context_menu import show_context_menu
    result = show_context_menu(movie, addon_id=addon_id)
    dialog.notification("EasyMovie Preview", "Context: %s" % result)


def preview_continuation() -> None:
    """Show the ContinuationDialog with countdown (playlist continuation)."""
    movies = _fetch_preview_movies()

    from resources.lib.playback.playback_monitor import ContinuationDialog
    from resources.lib.utils import lang

    if len(movies) >= 2:
        finished = movies[0]
        next_movie = movies[1]
        finished_title = finished.get("title", "Preview Movie")
        next_title = next_movie.get("title", "Next Movie")
        set_name = finished.get("set", "") or "Preview Collection"
        art = next_movie.get("art", {})
        poster = art.get("poster", "") if isinstance(art, dict) else ""
    else:
        finished_title = "The Dark Knight"
        next_title = "The Dark Knight Rises"
        set_name = "The Dark Knight Collection"
        poster = ""

    cd = ContinuationDialog(
        'script-easymovie-continuation.xml',
        script_path, 'Default', '1080i'
    )
    cd._addon_id = addon_id
    cd.configure(
        message="%s %s" % (lang(32319), finished_title),
        subtitle="%s %s %s" % (next_title, lang(32318), set_name),
        yes_label=lang(32316),
        no_label=lang(32317),
        poster=poster,
        duration=15,
        default_yes=True,
    )
    cd.doModal()
    dialog.notification(
        "EasyMovie Preview",
        "Continuation: confirmed=%s auto=%s" % (cd.confirmed, cd.auto_selected)
    )
    del cd


def preview_set_warning() -> None:
    """Show the ContinuationDialog as set warning (no countdown)."""
    movies = _fetch_preview_movies()

    from resources.lib.playback.playback_monitor import ContinuationDialog
    from resources.lib.utils import lang

    movie = _find_set_movie(movies)
    title = movie.get("title", "Preview Movie")
    year = str(movie.get("year", 2024))
    set_name = movie.get("set", "Preview Collection")
    art = movie.get("art", {})
    poster = art.get("poster", "") if isinstance(art, dict) else ""

    cd = ContinuationDialog(
        'script-easymovie-continuation.xml',
        script_path, 'Default', '1080i'
    )
    cd._addon_id = addon_id

    # lang(32327) = "%s (%s) from %s is in your library and unwatched."
    message = lang(32327) % (title, year, set_name)

    cd.configure(
        message=message,
        subtitle=lang(32328),  # "Would you like to watch it instead?"
        yes_label=lang(32300),  # "OK"
        no_label=lang(32301),  # "Cancel"
        poster=poster,
        duration=0,
        default_yes=True,
    )
    cd._heading = lang(32326)  # "EasyMovie - earlier movie in set"
    cd.doModal()
    dialog.notification(
        "EasyMovie Preview",
        "Set warning: confirmed=%s" % cd.confirmed
    )
    del cd


def Main() -> None:
    """Show the dialog preview selection menu."""
    options = [
        "1. Confirm Dialog",
        "2. Confirm Dialog (OK only)",
        "3. Select Dialog (single)",
        "4. Select Dialog (multi)",
        "5. Browse Window",
        "6. Context Menu",
        "7. Continuation Dialog (countdown)",
        "8. Set Warning Dialog (no countdown)",
        "9. All Dialogs (cycle through)",
    ]

    choice = dialog.select("EasyMovie Dialog Preview", options)  # type: ignore[arg-type]

    previews = [
        preview_confirm,
        preview_confirm_single,
        preview_select_single,
        preview_select_multi,
        preview_browse,
        preview_context_menu,
        preview_continuation,
        preview_set_warning,
    ]

    if 0 <= choice < len(previews):
        previews[choice]()
    elif choice == len(previews):
        for fn in previews:
            fn()
