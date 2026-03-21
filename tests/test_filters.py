"""Tests for the movie filter engine."""
from resources.lib.data.filters import FilterConfig, apply_filters, extract_unique_genres, extract_unique_mpaa, filter_by_playlist_ids

# Sample movie data matching Kodi JSON-RPC response format
SAMPLE_MOVIES = [
    {
        "movieid": 1, "title": "Action Movie",
        "genre": ["Action", "Thriller"], "year": 2024,
        "rating": 7.5, "runtime": 6600,  # 110 min (seconds)
        "mpaa": "Rated R", "set": "Action Collection", "setid": 1,
        "playcount": 0, "dateadded": "2024-01-15",
    },
    {
        "movieid": 2, "title": "Comedy Film",
        "genre": ["Comedy", "Romance"], "year": 2020,
        "rating": 6.2, "runtime": 5400,  # 90 min
        "mpaa": "Rated PG-13", "set": "", "setid": 0,
        "playcount": 1, "dateadded": "2023-06-01",
    },
    {
        "movieid": 3, "title": "Drama Classic",
        "genre": ["Drama"], "year": 1995,
        "rating": 8.5, "runtime": 8400,  # 140 min
        "mpaa": "Rated R", "set": "", "setid": 0,
        "playcount": 0, "dateadded": "2022-03-10",
    },
    {
        "movieid": 4, "title": "Kids Adventure",
        "genre": ["Adventure", "Family"], "year": 2023,
        "rating": 6.8, "runtime": 5700,  # 95 min
        "mpaa": "Rated PG", "set": "", "setid": 0,
        "playcount": 2, "dateadded": "2024-02-20",
    },
]


def test_no_filters_returns_all():
    config = FilterConfig()
    result = apply_filters(SAMPLE_MOVIES, config)
    assert len(result) == 4


def test_ignore_genre_or():
    """Ignore genres OR: exclude movies matching any ignored genre."""
    config = FilterConfig(ignore_genres=["Action"], ignore_genre_match_and=False)
    result = apply_filters(SAMPLE_MOVIES, config)
    assert len(result) == 3
    assert all("Action" not in m["genre"] for m in result)


def test_ignore_genre_or_multiple():
    """Ignore genres OR with multiple: exclude movies matching any."""
    config = FilterConfig(ignore_genres=["Action", "Comedy"], ignore_genre_match_and=False)
    result = apply_filters(SAMPLE_MOVIES, config)
    assert len(result) == 2  # Drama Classic and Kids Adventure


def test_ignore_genre_and():
    """Ignore genres AND: only exclude movies having ALL ignored genres."""
    config = FilterConfig(ignore_genres=["Action", "Thriller"], ignore_genre_match_and=True)
    result = apply_filters(SAMPLE_MOVIES, config)
    assert len(result) == 3  # Only Action Movie has both
    assert all(m["title"] != "Action Movie" for m in result)


def test_ignore_genre_and_no_full_match():
    """Ignore genres AND: no movie has all ignored genres, nothing excluded."""
    config = FilterConfig(ignore_genres=["Action", "Comedy"], ignore_genre_match_and=True)
    result = apply_filters(SAMPLE_MOVIES, config)
    assert len(result) == 4  # No movie has both Action and Comedy


def test_ignore_genre_empty():
    """No ignored genres means no exclusion."""
    config = FilterConfig(ignore_genres=None)
    result = apply_filters(SAMPLE_MOVIES, config)
    assert len(result) == 4


def test_ignore_then_include_genre():
    """Ignore genres are applied before include genres."""
    config = FilterConfig(
        ignore_genres=["Thriller"],
        ignore_genre_match_and=False,
        genres=["Action", "Drama"],
        genre_match_and=False,
    )
    result = apply_filters(SAMPLE_MOVIES, config)
    # Action Movie is excluded by ignore (has Thriller), Drama Classic remains
    assert len(result) == 1
    assert result[0]["title"] == "Drama Classic"


def test_genre_filter_or():
    config = FilterConfig(genres=["Action"], genre_match_and=False)
    result = apply_filters(SAMPLE_MOVIES, config)
    assert len(result) == 1
    assert result[0]["title"] == "Action Movie"


def test_genre_filter_or_multiple():
    config = FilterConfig(genres=["Action", "Comedy"], genre_match_and=False)
    result = apply_filters(SAMPLE_MOVIES, config)
    assert len(result) == 2


def test_genre_filter_and():
    config = FilterConfig(genres=["Action", "Thriller"], genre_match_and=True)
    result = apply_filters(SAMPLE_MOVIES, config)
    assert len(result) == 1
    assert result[0]["title"] == "Action Movie"


def test_genre_filter_and_no_match():
    config = FilterConfig(genres=["Action", "Comedy"], genre_match_and=True)
    result = apply_filters(SAMPLE_MOVIES, config)
    assert len(result) == 0


def test_watched_filter_unwatched():
    config = FilterConfig(watched=0)  # WATCHED_UNWATCHED
    result = apply_filters(SAMPLE_MOVIES, config)
    assert all(m["playcount"] == 0 for m in result)
    assert len(result) == 2


def test_watched_filter_watched():
    config = FilterConfig(watched=1)  # WATCHED_WATCHED
    result = apply_filters(SAMPLE_MOVIES, config)
    assert all(m["playcount"] > 0 for m in result)


def test_watched_filter_both():
    config = FilterConfig(watched=2)  # WATCHED_BOTH
    result = apply_filters(SAMPLE_MOVIES, config)
    assert len(result) == 4


def test_mpaa_filter():
    config = FilterConfig(mpaa_ratings=["Rated PG-13", "Rated PG"])
    result = apply_filters(SAMPLE_MOVIES, config)
    assert len(result) == 2


def test_runtime_filter_min():
    config = FilterConfig(runtime_min=100)  # minutes
    result = apply_filters(SAMPLE_MOVIES, config)
    assert all(m["runtime"] >= 6000 for m in result)


def test_runtime_filter_max():
    config = FilterConfig(runtime_max=100)  # minutes
    result = apply_filters(SAMPLE_MOVIES, config)
    assert all(m["runtime"] <= 6000 for m in result)


def test_runtime_filter_range():
    config = FilterConfig(runtime_min=90, runtime_max=120)
    result = apply_filters(SAMPLE_MOVIES, config)
    assert len(result) == 3  # 90min, 95min, and 110min movies


def test_year_filter_after():
    config = FilterConfig(year_from=2023)
    result = apply_filters(SAMPLE_MOVIES, config)
    assert all(m["year"] >= 2023 for m in result)


def test_year_filter_before():
    config = FilterConfig(year_to=2000)
    result = apply_filters(SAMPLE_MOVIES, config)
    assert all(m["year"] <= 2000 for m in result)


def test_year_filter_between():
    config = FilterConfig(year_from=2020, year_to=2024)
    result = apply_filters(SAMPLE_MOVIES, config)
    assert all(2020 <= m["year"] <= 2024 for m in result)


def test_score_filter():
    config = FilterConfig(min_score=70)  # 7.0
    result = apply_filters(SAMPLE_MOVIES, config)
    assert all(m["rating"] >= 7.0 for m in result)


def test_combined_filters():
    config = FilterConfig(
        genres=["Action", "Drama"],
        genre_match_and=False,
        watched=0,
        min_score=70,
    )
    result = apply_filters(SAMPLE_MOVIES, config)
    # Action Movie (7.5, unwatched) and Drama Classic (8.5, unwatched)
    assert len(result) == 2


def test_exclude_movie_ids():
    config = FilterConfig(exclude_ids=[1, 2])
    result = apply_filters(SAMPLE_MOVIES, config)
    assert len(result) == 2
    assert all(m["movieid"] not in [1, 2] for m in result)


def test_extract_unique_genres():
    genres = extract_unique_genres(SAMPLE_MOVIES)
    assert "Action" in genres
    assert "Comedy" in genres
    assert "Drama" in genres
    assert genres == sorted(genres)


def test_extract_unique_mpaa():
    ratings = extract_unique_mpaa(SAMPLE_MOVIES)
    assert "Rated R" in ratings
    assert "Rated PG" in ratings
    assert len(ratings) == 3


def test_filter_by_playlist_ids():
    """Should keep only movies whose movieid is in the playlist set."""
    playlist_ids = {1, 3}
    result = filter_by_playlist_ids(SAMPLE_MOVIES, playlist_ids)
    assert len(result) == 2
    assert {m["movieid"] for m in result} == {1, 3}


def test_filter_by_playlist_ids_empty():
    """Empty playlist IDs should return empty list."""
    result = filter_by_playlist_ids(SAMPLE_MOVIES, set())
    assert len(result) == 0


def test_filter_by_playlist_ids_no_match():
    """No matching IDs should return empty list."""
    result = filter_by_playlist_ids(SAMPLE_MOVIES, {999, 998})
    assert len(result) == 0
