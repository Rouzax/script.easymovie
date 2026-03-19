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
from typing import Any, Dict, List, Optional, TYPE_CHECKING, cast

import xbmcvfs

from resources.lib.constants import (
    ADDON_ID,
    MODE_BROWSE, MODE_PLAYLIST, MODE_ASK,
    RESURFACE_WINDOWS,
)
from resources.lib.utils import get_logger, json_query, notify, log_timing, lang
from resources.lib.ui.settings import load_settings
from resources.lib.ui.wizard import WizardFlow
from resources.lib.ui.dialogs import show_confirm_dialog, show_select_dialog
from resources.lib.ui.browse_window import (
    show_browse_window, RESULT_REROLL, RESULT_SURPRISE,
)
from resources.lib.data.queries import (
    get_all_movies_query,
    get_movie_details_with_art_query,
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

_active_monitors = []  # Keep references to prevent GC


def main(addon_id: str = ADDON_ID) -> None:
    """Entry point for the EasyMovie addon.

    Args:
        addon_id: Addon ID (different for clones).
    """
    import xbmc
    import xbmcaddon
    log = get_logger('default')
    addon = xbmcaddon.Addon(addon_id)
    version = addon.getAddonInfo('version')
    kodi_build = xbmc.getInfoLabel('System.BuildVersion')
    kodi_version = kodi_build.split()[0] if kodi_build else 'unknown'
    log.info("EasyMovie launched", event="launch.start",
             addon_id=addon_id, version=version, kodi=kodi_version)

    # 1. Load settings
    (primary_function, _theme, filter_settings, browse_settings,
     playlist_settings, set_settings, playback_settings,
     advanced_settings) = load_settings(addon_id if addon_id != ADDON_ID else None)

    log.debug("Settings", event="launch.settings",
              mode=primary_function,
              avoid_resurface=advanced_settings.avoid_resurface,
              resurface_window=advanced_settings.resurface_window,
              remember_filters=advanced_settings.remember_filters,
              show_counts=advanced_settings.show_counts,
              cumulative_counts=advanced_settings.cumulative_counts,
              set_enabled=set_settings.enabled,
              continuation=set_settings.continuation_enabled,
              pool_enabled=advanced_settings.movie_pool_enabled)

    # 2. Check for in-progress movie
    if playback_settings.check_in_progress:
        resumed = _check_in_progress(log, advanced_settings, addon_id)
        if resumed:
            return

    # 4. Determine mode
    mode = primary_function
    if mode == MODE_ASK:
        mode = _ask_mode(log, addon_id)
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
                            yes_label="OK", no_label="", addon_id=addon_id)
        return

    log.debug("Movies loaded", count=len(all_movies))

    # 7. Get storage for history
    storage = _get_storage(addon_id)

    # 8. Run filter wizard
    wizard = WizardFlow(_build_wizard_settings(filter_settings))
    if advanced_settings.remember_filters:
        wizard.load_last_answers(storage.load_last_filters())

    filter_config = _run_wizard(log, wizard, all_movies, addon_id,
                               show_counts=advanced_settings.show_counts,
                               cumulative_counts=advanced_settings.cumulative_counts)
    if filter_config is None:
        return  # User cancelled

    # 9. Apply filters
    filtered = apply_filters(all_movies, filter_config)
    if not filtered:
        log.info("No movies after filtering", event="filter.no_results", total=len(all_movies))
        show_confirm_dialog("No Results",
                            "No movies match your filters.\nTry relaxing your criteria.",
                            yes_label="OK", no_label="", addon_id=addon_id)
        return

    log.debug("Filtered movies", count=len(filtered), total=len(all_movies))

    # 10. Save wizard answers for next time
    if advanced_settings.remember_filters:
        storage.save_last_filters(wizard.get_answers())

    # 11. Exclude previously suggested (or clear history if disabled)
    if not advanced_settings.avoid_resurface:
        storage.clear_suggested()
    elif advanced_settings.avoid_resurface:
        storage.validate_suggested(all_movies)
        storage.prune_suggested(RESURFACE_WINDOWS.get(advanced_settings.resurface_window, 24))
        exclude_ids = storage.get_suggested_ids()
        pre_exclude = len(filtered)
        filtered = [m for m in filtered if m.get("movieid", 0) not in exclude_ids]
        if not filtered:
            log.info("All movies excluded by resurface window",
                     event="history.exhausted",
                     pre_exclude=pre_exclude, excluded=len(exclude_ids))
            show_confirm_dialog("No Results",
                                "All matching movies were recently suggested. "
                                "Try again later or adjust your re-suggestion window.",
                                yes_label="OK", no_label="", addon_id=addon_id)
            return
        if pre_exclude != len(filtered):
            log.debug("Resurface exclusion applied",
                      before=pre_exclude, after=len(filtered),
                      excluded=pre_exclude - len(filtered))

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
        addon_id=addon_id,
    )

    if confirmed:
        play_movie(movie, resume=True)
        return True
    return False


def _ask_mode(log, addon_id: str = ADDON_ID) -> Optional[int]:
    """Ask the user to choose Browse or Playlist mode."""
    result = show_confirm_dialog(
        heading="EasyMovie",
        message="Choose Mode",
        yes_label="Browse",
        no_label="Playlist",
        addon_id=addon_id,
    )
    if result is None:
        return None  # User pressed back/escape
    return MODE_BROWSE if result else MODE_PLAYLIST


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
        "year_filter_type": filter_settings.year_filter_type,
        "year_from": filter_settings.year_from,
        "year_to": filter_settings.year_to,
        "year_recency": filter_settings.year_recency,
        "score_mode": filter_settings.score_mode,
        "min_score": filter_settings.min_score,
    }


def _run_wizard(log, wizard: WizardFlow, all_movies: list,
                addon_id: str = ADDON_ID,
                show_counts: bool = True,
                cumulative_counts: bool = False) -> Optional[Any]:
    """Run the wizard flow, returning a FilterConfig or None if cancelled."""
    from resources.lib.data.filters import (
        extract_unique_genres, extract_unique_mpaa,
    )
    from resources.lib.constants import RUNTIME_RANGES, SCORE_RANGES

    from resources.lib.data.filters import apply_filters as _apply_filters

    def _count_pool() -> list:
        """Get the movie pool for counting — full or cumulative."""
        if not show_counts:
            return []
        if not cumulative_counts:
            return all_movies
        # Build partial filter config from completed steps only
        partial_config = wizard.build_partial_filter_config()
        return _apply_filters(all_movies, partial_config)

    def _fmt(label: str, count: int) -> str:
        """Format a label with optional count."""
        if show_counts:
            return f"{label} ({count})"
        return label

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
            pool = _count_pool()
            if show_counts:
                gcounts = {}
                for m in pool:
                    for g in m.get("genre", []):
                        gcounts[g] = gcounts.get(g, 0) + 1
                genre_labels = [_fmt(g, gcounts.get(g, 0)) for g in genres]
            else:
                genre_labels = genres
            preselected_genres = wizard.get_answers().get("genre", [])
            pre_indices = [i for i, g in enumerate(genres) if g in preselected_genres]
            result = show_select_dialog("Select Genres", genre_labels,
                                        multi_select=True, preselected=pre_indices,
                                        addon_id=addon_id)
            if result is None:
                if not wizard.go_back():
                    return None
                continue
            answer = [genres[i] for i in result]

        elif filter_type == "watched":
            pool = _count_pool()
            if show_counts:
                unwatched = sum(1 for m in pool if m.get("playcount", 0) == 0)
                watched = len(pool) - unwatched
                items = [
                    _fmt("Unwatched only", unwatched),
                    _fmt("Watched only", watched),
                    _fmt("Both", len(pool)),
                ]
            else:
                items = ["Unwatched only", "Watched only", "Both"]
            result = show_select_dialog("Watched Status", items, multi_select=False,
                                        addon_id=addon_id)
            if result is None:
                if not wizard.go_back():
                    return None
                continue
            answer = result[0]  # 0=unwatched, 1=watched, 2=both

        elif filter_type == "mpaa":
            ratings = extract_unique_mpaa(all_movies)
            pool = _count_pool()
            if show_counts:
                mcounts = {}
                for m in pool:
                    r = m.get("mpaa", "")
                    if r:
                        mcounts[r] = mcounts.get(r, 0) + 1
                rating_labels = [_fmt(r, mcounts.get(r, 0)) for r in ratings]
            else:
                rating_labels = list(ratings)
            preselected_mpaa = wizard.get_answers().get("mpaa", [])
            pre_indices = [i for i, r in enumerate(ratings) if r in preselected_mpaa]
            result = show_select_dialog("Select Age Ratings", rating_labels,
                                        multi_select=True, preselected=pre_indices,
                                        addon_id=addon_id)
            if result is None:
                if not wizard.go_back():
                    return None
                continue
            answer = [ratings[i] for i in result]

        elif filter_type == "runtime":
            pool = _count_pool()
            items = []
            for rt_lo, rt_hi, label in RUNTIME_RANGES:
                if show_counts:
                    count = sum(1 for m in pool
                                if (rt_lo == 0 or m.get("runtime", 0) >= rt_lo * 60)
                                and (rt_hi == 0 or m.get("runtime", 0) <= rt_hi * 60))
                    items.append(_fmt(label, count))
                else:
                    items.append(label)
            result = show_select_dialog("Select Runtime", items, multi_select=False,
                                        addon_id=addon_id)
            if result is None:
                if not wizard.go_back():
                    return None
                continue
            idx = result[0]
            rt_min, rt_max, _ = RUNTIME_RANGES[idx]
            answer = {"min": rt_min, "max": rt_max}

        elif filter_type == "year":
            # Combined recency + decade picker
            from resources.lib.data.filters import extract_decade_buckets
            from resources.lib.constants import RECENCY_RANGES
            import datetime

            current_year = datetime.datetime.now().year
            pool = _count_pool()
            buckets = extract_decade_buckets(pool if show_counts else all_movies)

            # Build items: recency first, then decades, then "Any year"
            items = []
            for years_ago, label_id in RECENCY_RANGES:
                if show_counts:
                    cutoff_year = current_year - years_ago
                    rcount = sum(1 for m in pool if m.get("year", 0) >= cutoff_year)
                    items.append(_fmt(lang(label_id), rcount))
                else:
                    items.append(lang(label_id))
            recency_count = len(RECENCY_RANGES)
            for _, count, label in buckets:
                items.append(_fmt(label, count) if show_counts else label)
            items.append(_fmt(lang(32225), len(pool)) if show_counts
                         else lang(32225))

            result = show_select_dialog(lang(32203), items, multi_select=False,
                                        addon_id=addon_id)
            if result is None:
                if not wizard.go_back():
                    return None
                continue
            idx = result[0]
            if idx < recency_count:
                # Recency selection
                years_ago = RECENCY_RANGES[idx][0]
                answer = {"from": current_year - years_ago, "to": 0}
            elif idx < recency_count + len(buckets):
                # Decade selection
                bucket_idx = idx - recency_count
                decade_start, _, _ = buckets[bucket_idx]
                answer = {"from": decade_start, "to": decade_start + 9}
            else:
                answer = {"from": 0, "to": 0}

        elif filter_type == "score":
            pool = _count_pool()
            items = []
            for min_score, label in SCORE_RANGES:
                if show_counts:
                    scount = sum(1 for m in pool
                                 if m.get("rating", 0.0) * 10 >= min_score)
                    items.append(_fmt(label, scount))
                else:
                    items.append(label)
            result = show_select_dialog("Select Score", items, multi_select=False,
                                        addon_id=addon_id)
            if result is None:
                if not wizard.go_back():
                    return None
                continue
            idx = result[0]
            answer = SCORE_RANGES[idx][0]

        wizard.set_answer(filter_type, answer)
        log.debug("Wizard answer", event="wizard.answer",
                  filter_type=filter_type, answer=answer)
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
    _log = get_logger('data')
    set_ids = {m.get("setid", 0) for m in movies if m.get("setid", 0)}
    set_cache: Dict[int, Dict[str, Any]] = {}
    with log_timing(_log, "load_set_details", set_count=len(set_ids)):
        for set_id in set_ids:
            result = json_query(get_movie_set_details_query(set_id))
            if result:
                # Unwrap: json_query returns {"setdetails": {...}}
                set_cache[set_id] = result.get("setdetails", result)
    return set_cache


def _load_art_for_movies(
    movies: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Load art and plot for a list of movies via individual detail queries."""
    if not movies:
        return movies
    _log = get_logger('data')
    enriched: List[Dict[str, Any]] = []
    with log_timing(_log, "load_art_for_movies", movie_count=len(movies)):
        for movie in movies:
            movie_id = movie.get("movieid", 0)
            if not movie_id:
                enriched.append(movie)
                continue
            result = json_query(get_movie_details_with_art_query(movie_id))
            details = result.get("moviedetails")
            if details:
                enriched.append(details)
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
        # Exclude previously suggested from this session's pool
        if advanced_settings.avoid_resurface:
            suggested_ids = storage.get_suggested_ids()
            available = [m for m in filtered if m.get("movieid", 0) not in suggested_ids]
            if not available:
                log.info("All filtered movies exhausted, resetting pool",
                         event="ui.pool_reset", total=len(filtered))
                available = filtered
        else:
            available = filtered

        # Select and sort
        results = select_and_sort_results(
            available, browse_settings.result_count,
            browse_settings.sort_by, browse_settings.sort_dir,
        )

        # Apply movie set substitutions
        if set_settings.enabled:
            set_cache = _load_set_details(results)
            results = apply_set_substitutions(results, set_cache)

        # Load art for display
        results = _load_art_for_movies(results)

        # Record as suggested (only when resurface avoidance is on)
        if advanced_settings.avoid_resurface:
            for movie in results:
                storage.add_suggested(movie.get("movieid", 0), movie.get("title", ""))

        # Show browse window
        titles = [m.get("title", "") for m in results]
        log.debug("Presenting movies", event="browse.present",
                  count=len(results), pool=len(available), titles=titles)
        result = show_browse_window(results, browse_settings.view_style, addon_id)

        if result == RESULT_REROLL:
            log.info("Re-rolling", event="ui.reroll")
            continue
        elif result == RESULT_SURPRISE:
            if not results:
                continue
            movie = random.choice(results)
            log.info("Surprise Me", event="ui.surprise",
                     title=movie.get("title", ""))
            play_movie(movie)
            break
        elif isinstance(result, dict) and result.get("__play_set__"):
            # Play Full Set from context menu
            movie = result["movie"]
            set_id = movie.get("setid", 0)
            if set_id:
                raw = json_query(get_movie_set_details_query(set_id))
                set_details = raw.get("setdetails", raw) if raw else {}
                set_movies = set_details.get("movies", [])
                if set_movies:
                    log.info("Playing full set", event="playlist.play_set",
                             set_name=movie.get("set", ""),
                             movie_count=len(set_movies))
                    build_and_play_playlist(set_movies)
                    break
        elif result is not None:
            log.info("Playing movie", event="playback.start",
                     title=result.get("title", ""),
                     movieid=result.get("movieid", 0))
            play_movie(result)
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

    # Record as suggested (only when resurface avoidance is on)
    if advanced_settings.avoid_resurface:
        for movie in results:
            storage.add_suggested(movie.get("movieid", 0), movie.get("title", ""))

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
        movies_by_id = {m.get("movieid", 0): m for m in results}
        # Monitor runs as part of xbmc.Player — Kodi calls its callbacks.
        # Must keep reference to prevent GC during playback session.
        monitor = PlaybackMonitor(
            set_cache=set_cache,
            movies=movies_by_id,
            continuation_duration=set_settings.continuation_duration,
            continuation_default=set_settings.continuation_default,
            addon_id=addon_id,
        )
        _active_monitors.append(monitor)


def _reopen_settings(addon_id: str) -> None:
    """Force-close dialogs and reopen settings to show updated values.

    Kodi's settings dialog caches values in memory. After a selector
    changes settings via setSetting(), we must close and reopen to
    pick up the new values.
    """
    import xbmc
    xbmc.executebuiltin('Dialog.Close(all,true)')
    xbmc.executebuiltin(
        f'AlarmClock(EasyMovieSettings,Addon.OpenSettings({addon_id}),00:01,silent)'
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
        _reopen_settings(addon_id)
        return True
    elif action == 'clone':
        from resources.clone import create_clone
        create_clone()
        return True
    elif action == 'set_icon':
        from resources.lib.utils import get_addon
        import xbmcvfs as _xbmcvfs
        import xbmcgui
        log = get_logger('default')
        addon = get_addon(addon_id)
        addon_path = addon.getAddonInfo('path')
        icons_dir = os.path.join(addon_path, 'resources', 'icons')
        icon_names = ["Golden Hour", "Ultraviolet", "Ember", "Nightfall", "Browse..."]
        icon_files = [
            "icon-golden-hour.png", "icon-ultraviolet.png",
            "icon-ember.png", "icon-nightfall.png",
        ]
        result = show_select_dialog(
            heading="Choose Icon",
            items=icon_names,
            multi_select=False,
            addon_id=addon_id,
        )
        if result is not None:
            idx = result[0]
            dst = os.path.join(addon_path, 'icon.png')
            if idx < len(icon_files):
                src = os.path.join(icons_dir, icon_files[idx])
                ok = _xbmcvfs.copy(src, dst)
                log.info("Icon set" if ok else "Icon set failed",
                         event="icon.set", source=src, target=dst, success=ok)
            else:
                dialog = xbmcgui.Dialog()
                image = dialog.browse(2, "Select Icon", 'files', '.png|.jpg|.jpeg')
                if image:
                    ok = _xbmcvfs.copy(cast(str, image), dst)
                    log.info("Custom icon set" if ok else "Custom icon set failed",
                             event="icon.set", source=cast(str, image),
                             target=dst, success=ok)
        _reopen_settings(addon_id)
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
        _reopen_settings(addon_id)
        return True

    return False
