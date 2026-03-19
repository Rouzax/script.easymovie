"""Tests for JSON-RPC query builders."""
from resources.lib.data.queries import (
    get_all_movies_query,
    get_movie_details_with_art_query,
    get_movie_details_query,
    get_all_movie_sets_query,
    get_movie_set_details_query,
    get_clear_video_playlist_query,
    build_add_movie_query,
    build_play_playlist_query,
    build_play_movie_query,
    get_in_progress_movies_query,
)


def test_get_all_movies_query_structure():
    """Query should request movie properties needed for filtering."""
    query = get_all_movies_query()
    assert query["method"] == "VideoLibrary.GetMovies"
    params = query["params"]
    assert "title" in params["properties"]
    assert "genre" in params["properties"]
    assert "year" in params["properties"]
    assert "rating" in params["properties"]
    assert "runtime" in params["properties"]
    assert "mpaa" in params["properties"]
    assert "set" in params["properties"]
    assert "setid" in params["properties"]
    assert "playcount" in params["properties"]
    assert "dateadded" in params["properties"]


def test_get_all_movies_query_no_art():
    """Data-only query should not include art (performance)."""
    query = get_all_movies_query()
    assert "art" not in query["params"]["properties"]


def test_get_movie_details_with_art_query():
    """Detail query should include art properties."""
    query = get_movie_details_with_art_query(movie_id=42)
    assert query["method"] == "VideoLibrary.GetMovieDetails"
    assert query["params"]["movieid"] == 42
    assert "art" in query["params"]["properties"]
    assert "plot" in query["params"]["properties"]


def test_get_movie_details_query():
    query = get_movie_details_query(movie_id=42)
    assert query["method"] == "VideoLibrary.GetMovieDetails"
    assert query["params"]["movieid"] == 42


def test_get_movie_set_details_query():
    query = get_movie_set_details_query(set_id=1)
    assert query["method"] == "VideoLibrary.GetMovieSetDetails"
    assert query["params"]["setid"] == 1


def test_get_all_movie_sets_query():
    query = get_all_movie_sets_query()
    assert query["method"] == "VideoLibrary.GetMovieSets"


def test_get_unique_genres_from_all_movies():
    """Genres are extracted client-side from the genre property."""
    query = get_all_movies_query()
    assert "genre" in query["params"]["properties"]


def test_playlist_add_movie_query():
    query = build_add_movie_query(movie_id=123, position=0)
    assert query["method"] == "Playlist.Add"
    assert query["params"]["item"]["movieid"] == 123


def test_playlist_add_movie_no_position():
    query = build_add_movie_query(movie_id=123)
    assert "position" not in query["params"]


def test_playlist_clear_query():
    query = get_clear_video_playlist_query()
    assert query["method"] == "Playlist.Clear"
    assert query["params"]["playlistid"] == 1  # Video playlist


def test_play_playlist_query():
    query = build_play_playlist_query(position=0)
    assert query["method"] == "Player.Open"
    assert query["params"]["item"]["playlistid"] == 1


def test_play_movie_query():
    query = build_play_movie_query(movie_id=99)
    assert query["method"] == "Player.Open"
    assert query["params"]["item"]["movieid"] == 99


def test_in_progress_movies_query():
    query = get_in_progress_movies_query()
    assert query["method"] == "VideoLibrary.GetMovies"
    assert query["params"]["filter"]["field"] == "inprogress"
