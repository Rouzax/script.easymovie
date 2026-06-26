"""Tests for JSON-RPC query builders."""
from resources.lib.data.queries import (
    build_add_movie_query,
    build_play_movie_query,
    build_play_playlist_query,
    build_playlist_get_movies_query,
    get_all_movie_sets_query,
    get_all_movies_query,
    get_clear_video_playlist_query,
    get_in_progress_movies_query,
    get_movie_details_with_art_query,
    get_movie_full_details_query,
    get_movie_set_details_query,
    get_playing_item_query,
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


def test_get_movie_details_with_art_query_movieid():
    query = get_movie_details_with_art_query(movie_id=42)
    assert query["method"] == "VideoLibrary.GetMovieDetails"
    assert query["params"]["movieid"] == 42


def test_get_movie_full_details_query():
    """Full-details query feeds the native info pane: needs cast and crew."""
    query = get_movie_full_details_query(movie_id=7)
    assert query["method"] == "VideoLibrary.GetMovieDetails"
    assert query["params"]["movieid"] == 7
    props = query["params"]["properties"]
    # Fields the native DialogVideoInfo renders that the display query lacks
    for field in ("cast", "director", "writer", "studio", "country",
                  "premiered", "plotoutline", "tagline", "originaltitle"):
        assert field in props
    # Plus the basics
    for field in ("title", "genre", "year", "rating", "plot", "art"):
        assert field in props
    # And the file path, so the pane's Play button has something to play
    assert "file" in props


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
    assert "options" not in query["params"]


def test_play_movie_query_with_resume():
    """Resume should embed a Player.Position.Time object in options."""
    # 3266 seconds = 0h 54m 26s
    query = build_play_movie_query(movie_id=99, resume_seconds=3266)
    assert query["params"]["item"]["movieid"] == 99
    assert query["params"]["options"]["resume"] == {
        "hours": 0, "minutes": 54, "seconds": 26,
    }


def test_play_movie_query_resume_zero_omits_options():
    """resume_seconds=0 means no resume; options must be omitted."""
    query = build_play_movie_query(movie_id=99, resume_seconds=0)
    assert "options" not in query["params"]


def test_play_movie_query_resume_over_one_hour():
    """Hours/minutes/seconds split must be correct beyond 1 hour."""
    # 1h 23m 45s = 5025 seconds
    query = build_play_movie_query(movie_id=99, resume_seconds=5025)
    assert query["params"]["options"]["resume"] == {
        "hours": 1, "minutes": 23, "seconds": 45,
    }


def test_in_progress_movies_query():
    query = get_in_progress_movies_query()
    assert query["method"] == "VideoLibrary.GetMovies"
    assert query["params"]["filter"]["field"] == "inprogress"


def test_playing_item_query():
    """Player.GetItem query should request set-related properties."""
    query = get_playing_item_query()
    assert query["method"] == "Player.GetItem"
    assert query["params"]["playerid"] == 1
    props = query["params"]["properties"]
    assert "title" in props
    assert "setid" in props
    assert "set" in props
    assert "type" in props


def test_playlist_get_movies_query():
    """Query should use Files.GetDirectory to read smart playlist contents."""
    query = build_playlist_get_movies_query("special://profile/playlists/video/Movies.xsp")
    assert query["method"] == "Files.GetDirectory"
    assert query["params"]["directory"] == "special://profile/playlists/video/Movies.xsp"
    assert query["params"]["media"] == "video"
