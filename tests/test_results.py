"""Tests for result selection and sorting."""
from resources.lib.data.results import select_and_sort_results
from resources.lib.constants import (
    SORT_RANDOM, SORT_TITLE, SORT_YEAR, SORT_RATING,
    SORT_RUNTIME, SORT_DATE_ADDED, SORT_ASC, SORT_DESC,
)


SAMPLE_MOVIES = [
    {"movieid": 1, "title": "Zebra", "year": 2020, "rating": 7.0, "runtime": 5400, "dateadded": "2024-01-01", "setid": 0, "set": ""},
    {"movieid": 2, "title": "Alpha", "year": 2024, "rating": 8.5, "runtime": 7200, "dateadded": "2024-06-01", "setid": 0, "set": ""},
    {"movieid": 3, "title": "Middle", "year": 2022, "rating": 6.0, "runtime": 6000, "dateadded": "2023-03-01", "setid": 0, "set": ""},
]


def test_sort_by_title_asc():
    result = select_and_sort_results(SAMPLE_MOVIES, count=3, sort_by=SORT_TITLE, sort_dir=SORT_ASC)
    assert [m["title"] for m in result] == ["Alpha", "Middle", "Zebra"]


def test_sort_by_title_desc():
    result = select_and_sort_results(SAMPLE_MOVIES, count=3, sort_by=SORT_TITLE, sort_dir=SORT_DESC)
    assert [m["title"] for m in result] == ["Zebra", "Middle", "Alpha"]


def test_sort_by_year_desc():
    result = select_and_sort_results(SAMPLE_MOVIES, count=3, sort_by=SORT_YEAR, sort_dir=SORT_DESC)
    assert result[0]["year"] == 2024
    assert result[-1]["year"] == 2020


def test_sort_by_rating_desc():
    result = select_and_sort_results(SAMPLE_MOVIES, count=3, sort_by=SORT_RATING, sort_dir=SORT_DESC)
    assert result[0]["rating"] == 8.5


def test_sort_by_runtime_asc():
    result = select_and_sort_results(SAMPLE_MOVIES, count=3, sort_by=SORT_RUNTIME, sort_dir=SORT_ASC)
    assert result[0]["runtime"] == 5400


def test_sort_by_date_added_desc():
    result = select_and_sort_results(SAMPLE_MOVIES, count=3, sort_by=SORT_DATE_ADDED, sort_dir=SORT_DESC)
    assert result[0]["dateadded"] == "2024-06-01"


def test_count_limits_results():
    result = select_and_sort_results(SAMPLE_MOVIES, count=2, sort_by=SORT_TITLE, sort_dir=SORT_ASC)
    assert len(result) == 2


def test_count_exceeds_available():
    result = select_and_sort_results(SAMPLE_MOVIES, count=100, sort_by=SORT_TITLE, sort_dir=SORT_ASC)
    assert len(result) == 3  # All available


def test_random_sort_returns_correct_count():
    result = select_and_sort_results(SAMPLE_MOVIES * 10, count=5, sort_by=SORT_RANDOM, sort_dir=SORT_ASC)
    assert len(result) == 5
