"""Tests for smart playlist movie ID extraction."""
import importlib
from unittest.mock import patch

import pytest


@pytest.fixture(autouse=True)
def _fresh_module():
    """Ensure smart_playlists module is freshly imported for each test.

    test_settings.py clears all resources.lib modules from sys.modules,
    which can leave stale references. Re-importing ensures the patch
    targets the same module object that provides the function under test.
    """
    import resources.lib.data.smart_playlists as mod
    importlib.reload(mod)


@patch("resources.lib.data.smart_playlists.json_query")
def test_extract_movie_ids_basic(mock_query):
    """Should extract movie IDs from Files.GetDirectory response."""
    from resources.lib.data.smart_playlists import extract_movie_ids_from_playlist

    mock_query.return_value = {
        "files": [
            {"id": 10, "type": "movie", "label": "Movie A"},
            {"id": 20, "type": "movie", "label": "Movie B"},
            {"id": 30, "type": "movie", "label": "Movie C"},
        ]
    }
    ids = extract_movie_ids_from_playlist("special://profile/playlists/video/Test.xsp")
    assert ids == {10, 20, 30}


@patch("resources.lib.data.smart_playlists.json_query")
def test_extract_movie_ids_filters_non_movies(mock_query):
    """Should only return items with type 'movie'."""
    from resources.lib.data.smart_playlists import extract_movie_ids_from_playlist

    mock_query.return_value = {
        "files": [
            {"id": 10, "type": "movie", "label": "Movie A"},
            {"id": 5, "type": "tvshow", "label": "TV Show"},
        ]
    }
    ids = extract_movie_ids_from_playlist("special://profile/playlists/video/Mixed.xsp")
    assert ids == {10}


@patch("resources.lib.data.smart_playlists.json_query")
def test_extract_movie_ids_empty_playlist(mock_query):
    """Empty or missing 'files' key should return empty set."""
    from resources.lib.data.smart_playlists import extract_movie_ids_from_playlist

    mock_query.return_value = {}
    ids = extract_movie_ids_from_playlist("special://profile/playlists/video/Empty.xsp")
    assert ids == set()


@patch("resources.lib.data.smart_playlists.json_query")
def test_extract_movie_ids_no_files_key(mock_query):
    """Response without files key should return empty set."""
    from resources.lib.data.smart_playlists import extract_movie_ids_from_playlist

    mock_query.return_value = {"limits": {"start": 0, "end": 0, "total": 0}}
    ids = extract_movie_ids_from_playlist("special://profile/playlists/video/Bad.xsp")
    assert ids == set()


@patch("resources.lib.data.smart_playlists.json_query")
def test_extract_normalizes_path(mock_query):
    """Should normalize path to special:// format."""
    from resources.lib.data.smart_playlists import extract_movie_ids_from_playlist

    mock_query.return_value = {"files": []}
    extract_movie_ids_from_playlist("/some/absolute/path/Movies.xsp")
    call_args = mock_query.call_args[0][0]
    assert call_args["params"]["directory"] == "special://profile/playlists/video/Movies.xsp"
