"""
EasyMovie UI entry point.

Orchestrates the full addon flow:
1. Load settings
2. Apply theme
3. Check for in-progress movie (offer resume)
4. Determine mode (Browse/Playlist/Ask)
5. Run filter wizard (if filters need asking)
6. Query movies + apply filters
7. Apply movie set substitutions
8. Show results (browse) or build playlist
9. Handle Re-roll loop

Logging:
    Logger: 'default'
    Key events:
        - launch.start (INFO): Addon launched
        - launch.mode_selected (INFO): Mode determined
        - launch.resume_offered (INFO): In-progress movie found
    See LOGGING.md for full guidelines.
"""
from __future__ import annotations

import os
import random
import sys
from typing import Any, Dict, List, Optional, TYPE_CHECKING

import xbmcvfs

from resources.lib.constants import (
    ADDON_ID,
    MODE_BROWSE, MODE_PLAYLIST, MODE_ASK,
    RESURFACE_WINDOWS,
)
from resources.lib.utils import get_logger, json_query, notify, log_timing
from resources.lib.ui import apply_theme
from resources.lib.ui.settings import load_settings
from resources.lib.ui.wizard import WizardFlow
from resources.lib.ui.dialogs import show_confirm_dialog, show_select_dialog
from resources.lib.ui.browse_window import (
    show_browse_window, RESULT_REROLL, RESULT_SURPRISE,
)
from resources.lib.data.queries import (
    get_all_movies_query,
    get_movies_with_art_query,
    get_movie_set_details_query,
    get_in_progress_movies_query,
)
from resources.lib.data.filters import apply_filters
from resources.lib.data.movie_sets import apply_set_substitutions
from resources.lib.data.results import select_and_sort_results
from resources.lib.data.storage import StorageManager
from resources.lib.playback.player import play_movie, get_resume_info
from resources.lib.playback.playlist_builder import build_and_play_playlist
from resources.lib.playback.playback_monitor import PlaybackMonitor

if TYPE_CHECKING:
    from resources.lib.ui.settings import (
        FilterSettings, BrowseSettings, PlaylistSettings,
        SetSettings, PlaybackSettings, AdvancedSettings,
    )


def main(addon_id: str = ADDON_ID) -> None:
    """Entry point for the EasyMovie addon.

    Args:
        addon_id: Addon ID (different for clones).
    """
    log = get_logger('default')
    log.info("EasyMovie launched", event="launch.start", addon_id=addon_id)

    # 1. Load settings
    (primary_function, theme, filter_settings, browse_settings,
     playlist_settings, set_settings, playback_settings,
     advanced_settings) = load_settings(addon_id if addon_id != ADDON_ID else None)

    # 2. Apply theme
    apply_theme(theme)

    # 3. Check for in-progress movie
    if playback_settings.check_in_progress:
        resumed = _check_in_progress(log, advanced_settings, addon_id)
        if resumed:
            return

    # 4. Determine mode
    mode = primary_function
    if mode == MODE_ASK:
        mode = _ask_mode(log)
        if mode is None:
            return  # User cancelled

    log.info("Mode selected", event="launch.mode_selected",
             mode="browse" if mode == MODE_BROWSE else "playlist")

    # 5. Show processing notification
    if playback_settings.show_processing_notifications:
        notify("Finding movies...")

    # 6. Query all movies (bulk, no art)
    with log_timing(log, "movie_query"):
        result = json_query(get_all_movies_query())
        all_movies = result.get("movies", [])

    if not all_movies:
        show_confirm_dialog("No Movies", "Your library has no movies.",
                            yes_label="OK", no_label="")
        return

    log.debug("Movies loaded", count=len(all_movies))

    # 7. Get storage for history
    storage = _get_storage(addon_id)

    # 8. Run filter wizard
    wizard = WizardFlow(_build_wizard_settings(filter_settings))
    if advanced_settings.remember_filters:
        wizard.load_last_answers(storage.load_last_filters())

    filter_config = _run_wizard(log, wizard, all_movies)
    if filter_config is None:
        return  # User cancelled

    # 9. Apply filters
    filtered = apply_filters(all_movies, filter_config)
    if not filtered:
        show_confirm_dialog("No Results",
                            "No movies match your filters. Try relaxing your criteria.",
                            yes_label="OK", no_label="")
        return

    log.debug("Filtered movies", count=len(filtered), total=len(all_movies))

    # 10. Save wizard answers for next time
    if advanced_settings.remember_filters:
        storage.save_last_filters(wizard.get_answers())

    # 11. Exclude previously suggested
    if advanced_settings.avoid_resurface:
        storage.prune_suggested(RESURFACE_WINDOWS[advanced_settings.resurface_window])
        exclude_ids = storage.get_suggested_ids()
        filtered = [m for m in filtered if m["movieid"] not in exclude_ids]
        if not filtered:
            show_confirm_dialog("No Results",
                                "All matching movies were recently suggested. "
                                "Try again later or adjust your re-suggestion window.",
                                yes_label="OK", no_label="")
            return

    # 12. Execute mode
    if mode == MODE_BROWSE:
        _run_browse_mode(log, filtered, browse_settings, set_settings,
                         playback_settings, advanced_settings, storage, addon_id)
    else:
        _run_playlist_mode(log, filtered, playlist_settings, set_settings,
                           playback_settings, advanced_settings, storage, addon_id)


def _check_in_progress(
    log, advanced_settings: AdvancedSettings, addon_id: str
) -> bool:
    """Check for in-progress movies and offer to resume."""
    result = json_query(get_in_progress_movies_query())
    movies = result.get("movies", [])
    if not movies:
        return False

    movie = movies[0]
    resume = get_resume_info(movie)
    if not resume:
        return False

    title = movie.get("title", "Unknown")
    remaining = resume["remaining_minutes"]

    log.info("In-progress movie found", event="launch.resume_offered",
             title=title, remaining_minutes=remaining)

    confirmed = show_confirm_dialog(
        "Resume Movie?",
        f"{title}\n{remaining} minutes remaining",
        yes_label="Resume",
        no_label="New Selection",
    )

    if confirmed:
        play_movie(movie, resume=True)
        return True
    return False


def _ask_mode(log) -> Optional[int]:
    """Ask the user to choose Browse or Playlist mode."""
    result = show_select_dialog(
        heading="Choose Mode",
        items=["Browse", "Playlist"],
        multi_select=False,
    )
    if result is None:
        return None
    return MODE_BROWSE if result[0] == 0 else MODE_PLAYLIST


def _build_wizard_settings(filter_settings: FilterSettings) -> Dict[str, Any]:
    """Convert FilterSettings to the dict format WizardFlow expects."""
    return {
        "genre_mode": filter_settings.genre_mode,
        "genre_match_and": filter_settings.genre_match_and,
        "preset_genres": filter_settings.preset_genres,
        "watched_mode": filter_settings.watched_mode,
        "watched_preset": filter_settings.watched_preset,
        "mpaa_mode": filter_settings.mpaa_mode,
        "preset_mpaa": filter_settings.preset_mpaa,
        "runtime_mode": filter_settings.runtime_mode,
        "runtime_min": filter_settings.runtime_min,
        "runtime_max": filter_settings.runtime_max,
        "year_mode": filter_settings.year_mode,
        "year_from": filter_settings.year_from,
        "year_to": filter_settings.year_to,
        "score_mode": filter_settings.score_mode,
        "min_score": filter_settings.min_score,
    }


def _run_wizard(log, wizard: WizardFlow, all_movies: list) -> Optional[Any]:
    """Run the wizard flow, returning a FilterConfig or None if cancelled."""
    from resources.lib.data.filters import (
        extract_unique_genres, extract_unique_mpaa,
    )
    from resources.lib.constants import RUNTIME_RANGES, SCORE_RANGES

    if wizard.is_complete:
        return wizard.build_filter_config()

    while not wizard.is_complete:
        step = wizard.current_step
        if step is None:
            break

        filter_type = step.filter_type
        answer = None

        if filter_type == "genre":
            genres = extract_unique_genres(all_movies)
            preselected_genres = wizard.get_answers().get("genre", [])
            pre_indices = [i for i, g in enumerate(genres) if g in preselected_genres]
            result = show_select_dialog("Select Genres", genres,
                                        multi_select=True, preselected=pre_indices)
            if result is None:
                if not wizard.go_back():
                    return None
                continue
            answer = [genres[i] for i in result]

        elif filter_type == "watched":
            items = ["Unwatched only", "Watched only", "Both"]
            result = show_select_dialog("Watched Status", items, multi_select=False)
            if result is None:
                if not wizard.go_back():
                    return None
                continue
            answer = result[0]  # 0=unwatched, 1=watched, 2=both

        elif filter_type == "mpaa":
            ratings = extract_unique_mpaa(all_movies)
            preselected_mpaa = wizard.get_answers().get("mpaa", [])
            pre_indices = [i for i, r in enumerate(ratings) if r in preselected_mpaa]
            result = show_select_dialog("Select Age Ratings", ratings,
                                        multi_select=True, preselected=pre_indices)
            if result is None:
                if not wizard.go_back():
                    return None
                continue
            answer = [ratings[i] for i in result]

        elif filter_type == "runtime":
            items = [label for _, _, label in RUNTIME_RANGES]
            result = show_select_dialog("Select Runtime", items, multi_select=False)
            if result is None:
                if not wizard.go_back():
                    return None
                continue
            idx = result[0]
            rt_min, rt_max, _ = RUNTIME_RANGES[idx]
            answer = {"min": rt_min, "max": rt_max}

        elif filter_type == "year":
            # Simple decade picker
            from resources.lib.data.filters import extract_decade_buckets
            buckets = extract_decade_buckets(all_movies)
            items = [f"{label} ({count} movies)" for _, count, label in buckets]
            items.append("Any year")
            result = show_select_dialog("Select Decade", items, multi_select=False)
            if result is None:
                if not wizard.go_back():
                    return None
                continue
            idx = result[0]
            if idx < len(buckets):
                decade_start, _, _ = buckets[idx]
                answer = {"from": decade_start, "to": decade_start + 9}
            else:
                answer = {"from": 0, "to": 0}

        elif filter_type == "score":
            items = [label for _, label in SCORE_RANGES]
            result = show_select_dialog("Select Score", items, multi_select=False)
            if result is None:
                if not wizard.go_back():
                    return None
                continue
            idx = result[0]
            answer = SCORE_RANGES[idx][0]

        wizard.set_answer(filter_type, answer)
        if not wizard.advance():
            break  # Wizard complete

    return wizard.build_filter_config()


def _get_storage(addon_id: str) -> StorageManager:
    """Get the storage manager for the addon."""
    storage_dir = xbmcvfs.translatePath(
        f"special://profile/addon_data/{addon_id}/"
    )
    import os
    os.makedirs(storage_dir, exist_ok=True)
    return StorageManager(os.path.join(storage_dir, "easymovie_data.json"))


def _load_set_details(
    movies: List[Dict[str, Any]]
) -> Dict[int, Dict[str, Any]]:
    """Load movie set details for all set-member movies."""
    set_ids = {m.get("setid", 0) for m in movies if m.get("setid", 0)}
    set_cache = {}
    for set_id in set_ids:
        result = json_query(get_movie_set_details_query(set_id))
        if result:
            set_cache[set_id] = result
    return set_cache


def _load_art_for_movies(
    movies: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Load art for a list of movies (phase 2 query)."""
    if not movies:
        return movies
    movie_ids = [m["movieid"] for m in movies]
    result = json_query(get_movies_with_art_query(movie_ids))
    art_movies = result.get("movies", [])

    # Build lookup by movieid
    art_lookup = {m["movieid"]: m for m in art_movies}

    # Merge art into original movie dicts
    enriched = []
    for movie in movies:
        art_movie = art_lookup.get(movie["movieid"])
        if art_movie:
            enriched.append(art_movie)
        else:
            enriched.append(movie)
    return enriched


def _run_browse_mode(
    log,
    filtered: List[Dict[str, Any]],
    browse_settings: BrowseSettings,
    set_settings: SetSettings,
    playback_settings: PlaybackSettings,
    advanced_settings: AdvancedSettings,
    storage: StorageManager,
    addon_id: str,
) -> None:
    """Run the browse mode loop with Re-roll support."""
    while True:
        # Select and sort
        results = select_and_sort_results(
            filtered, browse_settings.result_count,
            browse_settings.sort_by, browse_settings.sort_dir,
        )

        # Apply movie set substitutions
        if set_settings.enabled:
            set_cache = _load_set_details(results)
            results = apply_set_substitutions(results, set_cache)

        # Load art for display
        results = _load_art_for_movies(results)

        # Record as suggested
        for movie in results:
            storage.add_suggested(movie["movieid"])

        # Show browse window
        result = show_browse_window(results, browse_settings.view_style, addon_id)

        if result == RESULT_REROLL:
            log.info("Re-rolling", event="ui.reroll")
            continue
        elif result == RESULT_SURPRISE:
            movie = random.choice(results)
            log.info("Surprise Me", event="ui.surprise",
                     title=movie.get("title", ""))
            play_movie(movie)
            if browse_settings.return_to_list:
                continue
            break
        elif result is not None:
            play_movie(result)
            if browse_settings.return_to_list:
                continue
            break
        else:
            break  # User closed


def _run_playlist_mode(
    log,
    filtered: List[Dict[str, Any]],
    playlist_settings: PlaylistSettings,
    set_settings: SetSettings,
    playback_settings: PlaybackSettings,
    advanced_settings: AdvancedSettings,
    storage: StorageManager,
    addon_id: str,
) -> None:
    """Run playlist mode."""
    # Select and sort
    results = select_and_sort_results(
        filtered, playlist_settings.movie_count,
        playlist_settings.sort_by, playlist_settings.sort_dir,
    )

    # Apply movie set substitutions
    if set_settings.enabled:
        set_cache = _load_set_details(results)
        results = apply_set_substitutions(results, set_cache)

    # Record as suggested
    for movie in results:
        storage.add_suggested(movie["movieid"])

    # Build and play playlist
    success = build_and_play_playlist(
        results,
        show_notifications=playback_settings.show_processing_notifications,
        prioritize_in_progress=playlist_settings.prioritize_in_progress,
        resume_from_position=playlist_settings.resume_from_position,
    )

    if not success:
        return

    # Start playback monitor for set continuation
    if set_settings.enabled and set_settings.continuation_enabled:
        set_cache = _load_set_details(results)
        movies_by_id = {m["movieid"]: m for m in results}
        # Monitor runs as part of xbmc.Player — Kodi calls its callbacks.
        # Must keep reference to prevent GC during playback session.
        PlaybackMonitor(
            set_cache=set_cache,
            movies=movies_by_id,
            continuation_duration=set_settings.continuation_duration,
            continuation_default=set_settings.continuation_default,
            addon_id=addon_id,
        )


def _handle_entry_args(addon_id: str) -> bool:
    """Handle command-line arguments for special entry points.

    Returns True if the args were handled (caller should exit).
    """
    if len(sys.argv) < 2:
        return False

    action = sys.argv[1]

    if action == 'selector':
        from resources.selector import main as selector_main
        selector_main()
        return True
    elif action == 'clone':
        from resources.clone import create_clone
        create_clone()
        return True
    elif action == 'set_icon':
        from resources.lib.utils import get_addon
        import xbmcgui
        addon = get_addon(addon_id)
        dialog = xbmcgui.Dialog()
        image = dialog.browse(2, "Select Icon", 'files', '.png|.jpg|.jpeg')
        if image:
            import xbmcvfs as _xbmcvfs
            icon_path = os.path.join(addon.getAddonInfo('path'), 'icon.png')
            _xbmcvfs.copy(image, icon_path)
        return True
    elif action == 'reset_icon':
        from resources.lib.utils import get_addon
        import xbmcvfs as _xbmcvfs
        addon = get_addon(addon_id)
        addon_path = addon.getAddonInfo('path')
        default_icon = os.path.join(addon_path, 'icon_default.png')
        icon_path = os.path.join(addon_path, 'icon.png')
        if _xbmcvfs.exists(default_icon):
            _xbmcvfs.copy(default_icon, icon_path)
        return True

    return False
