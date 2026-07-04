"""Tests for the custom movie info dialog."""
from resources.lib.ui.info_dialog import (
    STR_GENRE,
    STR_RATED,
    STR_RATING,
    STR_RUNTIME,
    STR_YEAR,
    build_cast_items,
    build_metadata_rows,
    format_certification,
    format_genres,
    format_rating,
    format_runtime,
)


def test_format_runtime_hours_and_minutes():
    assert format_runtime(96 * 60) == "1h 36m"


def test_format_runtime_under_an_hour():
    assert format_runtime(45 * 60) == "45m"


def test_format_runtime_zero_is_empty():
    assert format_runtime(0) == ""


def test_format_rating_with_votes():
    assert format_rating(7.5, "2558") == "★ 7.5 (2,558 votes)"


def test_format_rating_without_votes():
    assert format_rating(7.5, "") == "★ 7.5"


def test_format_rating_zero_is_empty():
    assert format_rating(0.0, "1234") == ""


def test_format_genres_slash_joined():
    assert format_genres(["Action", "Thriller"]) == "Action / Thriller"


def test_format_genres_empty():
    assert format_genres([]) == ""


def test_format_certification_strips_rated_prefix():
    assert format_certification("Rated R") == "R"


def test_format_certification_passthrough():
    assert format_certification("TV-MA") == "TV-MA"


def test_build_metadata_rows_collapses_empty():
    details = {"year": 2024, "rating": 7.5, "votes": "2558",
               "runtime": 96 * 60, "mpaa": "Rated R",
               "genre": ["Action", "Thriller"]}
    rows = build_metadata_rows(details)
    assert rows == [
        (STR_YEAR, "2024"),
        (STR_RATING, "★ 7.5 (2,558 votes)"),
        (STR_RUNTIME, "1h 36m"),
        (STR_RATED, "R"),
        (STR_GENRE, "Action / Thriller"),
    ]


def test_build_metadata_rows_skips_missing():
    rows = build_metadata_rows({"year": 2024})
    assert rows == [(STR_YEAR, "2024")]


def test_build_cast_items_limits_and_maps():
    cast = [{"name": "A", "role": "Hero", "thumbnail": "img://a"},
            {"name": "B", "role": "", "thumbnail": ""}]
    assert build_cast_items(cast, limit=1) == [("A", "Hero", "img://a")]
    assert build_cast_items(cast, limit=10) == [
        ("A", "Hero", "img://a"), ("B", "", "")]
