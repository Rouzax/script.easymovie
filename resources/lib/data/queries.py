"""
JSON-RPC query builders for movie operations.

All Kodi JSON-RPC queries are constructed here. No other module
should build raw query dicts.

"""
from typing import Dict, Any


def get_all_movies_query() -> Dict[str, Any]:
    """Get all movies with properties needed for filtering (no art)."""
    return {
        "jsonrpc": "2.0",
        "method": "VideoLibrary.GetMovies",
        "params": {
            "properties": [
                "title", "genre", "year", "rating", "runtime",
                "mpaa", "set", "setid", "playcount", "dateadded",
                "file", "resume", "lastplayed",
            ],
            "sort": {"method": "title"},
        },
        "id": 1,
    }


def get_movie_details_with_art_query(movie_id: int) -> Dict[str, Any]:
    """Get a single movie with art and plot for display."""
    return {
        "jsonrpc": "2.0",
        "method": "VideoLibrary.GetMovieDetails",
        "params": {
            "movieid": movie_id,
            "properties": [
                "title", "genre", "year", "rating", "runtime",
                "mpaa", "set", "setid", "playcount", "dateadded",
                "plot", "art", "file", "resume", "lastplayed",
            ],
        },
        "id": 1,
    }


def get_all_movie_sets_query() -> Dict[str, Any]:
    """Get all movie sets."""
    return {
        "jsonrpc": "2.0",
        "method": "VideoLibrary.GetMovieSets",
        "params": {
            "properties": ["title", "playcount"],
            "sort": {"method": "title"},
        },
        "id": 1,
    }


def get_movie_set_details_query(set_id: int) -> Dict[str, Any]:
    """Get movies within a set, sorted by year (release order)."""
    return {
        "jsonrpc": "2.0",
        "method": "VideoLibrary.GetMovieSetDetails",
        "params": {
            "setid": set_id,
            "properties": ["title"],
            "movies": {
                "properties": [
                    "title", "playcount", "year", "runtime",
                    "rating", "genre", "art", "resume",
                ],
                "sort": {"method": "year"},
            },
        },
        "id": 1,
    }


def get_playlist_files_query() -> Dict[str, Any]:
    """Get list of video playlist files from Kodi's playlist directory."""
    return {
        "jsonrpc": "2.0",
        "method": "Files.GetDirectory",
        "params": {
            "directory": "special://profile/playlists/video/",
            "media": "video",
        },
        "id": 1,
    }


def get_clear_video_playlist_query() -> Dict[str, Any]:
    """Clear the video playlist."""
    return {
        "jsonrpc": "2.0",
        "method": "Playlist.Clear",
        "params": {"playlistid": 1},
        "id": 1,
    }


def build_add_movie_query(movie_id: int, position: int = -1) -> Dict[str, Any]:
    """Add a movie to the video playlist."""
    params: Dict[str, Any] = {
        "playlistid": 1,
        "item": {"movieid": movie_id},
    }
    if position >= 0:
        params["position"] = position
    return {
        "jsonrpc": "2.0",
        "method": "Playlist.Add",
        "params": params,
        "id": 1,
    }


def build_play_playlist_query(position: int = 0) -> Dict[str, Any]:
    """Start playing the video playlist."""
    return {
        "jsonrpc": "2.0",
        "method": "Player.Open",
        "params": {"item": {"playlistid": 1, "position": position}},
        "id": 1,
    }


def build_play_movie_query(movie_id: int) -> Dict[str, Any]:
    """Play a single movie directly."""
    return {
        "jsonrpc": "2.0",
        "method": "Player.Open",
        "params": {"item": {"movieid": movie_id}},
        "id": 1,
    }


def get_playing_item_query() -> Dict[str, Any]:
    """Get information about the currently playing video item."""
    return {
        "jsonrpc": "2.0",
        "method": "Player.GetItem",
        "params": {
            "playerid": 1,
            "properties": ["title", "setid", "set", "playcount", "type"],
        },
        "id": 1,
    }


def get_in_progress_movies_query() -> Dict[str, Any]:
    """Get movies with a resume point (partially watched)."""
    return {
        "jsonrpc": "2.0",
        "method": "VideoLibrary.GetMovies",
        "params": {
            "properties": [
                "title", "runtime", "resume", "lastplayed",
                "art", "set", "setid",
            ],
            "filter": {
                "field": "inprogress",
                "operator": "true",
                "value": "",
            },
            "sort": {"method": "lastplayed", "order": "descending"},
            "limits": {"start": 0, "end": 10},
        },
        "id": 1,
    }
