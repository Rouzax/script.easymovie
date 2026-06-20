"""Tests for movie set awareness logic."""
from resources.lib.data.movie_sets import (
    find_first_unwatched_before,
    find_first_unwatched_in_set,
    apply_set_substitutions,
    get_next_in_set,
)


# Simulated set data (sorted by year, as Kodi returns)
HP_SET = {
    "setid": 10,
    "title": "Harry Potter Collection",
    "movies": [
        {"movieid": 101, "title": "Philosopher's Stone", "playcount": 1, "year": 2001},
        {"movieid": 102, "title": "Chamber of Secrets", "playcount": 1, "year": 2002},
        {"movieid": 103, "title": "Prisoner of Azkaban", "playcount": 0, "year": 2004},
        {"movieid": 104, "title": "Goblet of Fire", "playcount": 0, "year": 2005},
    ],
}

ALL_UNWATCHED_SET = {
    "setid": 11,
    "title": "LOTR Collection",
    "movies": [
        {"movieid": 201, "title": "Fellowship", "playcount": 0, "year": 2001},
        {"movieid": 202, "title": "Two Towers", "playcount": 0, "year": 2002},
        {"movieid": 203, "title": "Return of the King", "playcount": 0, "year": 2003},
    ],
}

ALL_WATCHED_SET = {
    "setid": 12,
    "title": "Back to the Future",
    "movies": [
        {"movieid": 301, "title": "BTTF 1", "playcount": 2, "year": 1985},
        {"movieid": 302, "title": "BTTF 2", "playcount": 1, "year": 1989},
        {"movieid": 303, "title": "BTTF 3", "playcount": 1, "year": 1990},
    ],
}


def test_first_unwatched_partial_set():
    """Movies 1-2 watched, should return movie 3."""
    result = find_first_unwatched_in_set(HP_SET)
    assert result["movieid"] == 103


def test_first_unwatched_all_unwatched():
    """All unwatched, should return first movie."""
    result = find_first_unwatched_in_set(ALL_UNWATCHED_SET)
    assert result["movieid"] == 201


def test_first_unwatched_all_watched():
    """All watched, returns None."""
    result = find_first_unwatched_in_set(ALL_WATCHED_SET)
    assert result is None


def test_set_substitution():
    """Random picker selected movie 104 (Goblet of Fire), but 103 is first unwatched."""
    movies_picked = [
        {"movieid": 104, "setid": 10, "set": "Harry Potter Collection"},
        {"movieid": 50, "setid": 0, "set": ""},  # Non-set movie, untouched
    ]
    set_cache = {10: HP_SET}
    result = apply_set_substitutions(movies_picked, set_cache)
    assert result[0]["movieid"] == 103  # Substituted
    assert result[1]["movieid"] == 50   # Unchanged


def test_set_substitution_no_unwatched():
    """All watched in set — keep original pick (watched rewatch)."""
    movies_picked = [
        {"movieid": 301, "setid": 12, "set": "Back to the Future"},
    ]
    set_cache = {12: ALL_WATCHED_SET}
    result = apply_set_substitutions(movies_picked, set_cache)
    assert result[0]["movieid"] == 301  # Unchanged


def test_get_next_in_set():
    """After watching movie 103, next should be 104."""
    next_movie = get_next_in_set(HP_SET, current_movie_id=103)
    assert next_movie is not None
    assert next_movie["movieid"] == 104


def test_get_next_in_set_last_movie():
    """Last movie in set has no next."""
    next_movie = get_next_in_set(HP_SET, current_movie_id=104)
    assert next_movie is None


def test_get_next_in_set_not_found():
    """Movie not in set returns None."""
    next_movie = get_next_in_set(HP_SET, current_movie_id=999)
    assert next_movie is None


SINGLE_MOVIE_SET = {
    "setid": 13,
    "title": "Single Movie Set",
    "movies": [
        {"movieid": 401, "title": "Only Movie", "playcount": 0, "year": 2020},
    ],
}


# ---- find_first_unwatched_before tests ----


def test_find_earlier_unwatched_exists():
    """Playing movie 104 (Goblet of Fire), movie 103 is earlier and unwatched."""
    result = find_first_unwatched_before(HP_SET, current_movie_id=104)
    assert result is not None
    assert result["movieid"] == 103


def test_find_earlier_unwatched_all_earlier_watched():
    """Playing movie 103, movies 101-102 are watched — no earlier unwatched."""
    result = find_first_unwatched_before(HP_SET, current_movie_id=103)
    assert result is None


def test_find_earlier_unwatched_first_in_set():
    """Playing the first movie in a set — no earlier movies exist."""
    result = find_first_unwatched_before(HP_SET, current_movie_id=101)
    assert result is None


def test_find_earlier_unwatched_not_in_set():
    """Movie ID not in the set — returns None."""
    result = find_first_unwatched_before(HP_SET, current_movie_id=999)
    assert result is None


def test_find_earlier_unwatched_single_movie_set():
    """Single movie set — no earlier movie possible."""
    result = find_first_unwatched_before(SINGLE_MOVIE_SET, current_movie_id=401)
    assert result is None


def test_find_earlier_unwatched_all_unwatched():
    """All unwatched, playing movie 202 — movie 201 is earlier and unwatched."""
    result = find_first_unwatched_before(ALL_UNWATCHED_SET, current_movie_id=202)
    assert result is not None
    assert result["movieid"] == 201


def test_find_earlier_unwatched_all_watched():
    """All watched, playing movie 302 — no unwatched earlier movies."""
    result = find_first_unwatched_before(ALL_WATCHED_SET, current_movie_id=302)
    assert result is None


def test_no_duplicate_sets_in_results():
    """If random picker selected two movies from same set, deduplicate."""
    movies_picked = [
        {"movieid": 103, "setid": 10, "set": "Harry Potter Collection"},
        {"movieid": 104, "setid": 10, "set": "Harry Potter Collection"},
        {"movieid": 50, "setid": 0, "set": ""},
    ]
    set_cache = {10: HP_SET}
    result = apply_set_substitutions(movies_picked, set_cache)
    # Should have only one HP movie (the first unwatched) + non-set movie
    set_movies = [m for m in result if m.get("setid") == 10]
    assert len(set_movies) == 1
    assert set_movies[0]["movieid"] == 103
