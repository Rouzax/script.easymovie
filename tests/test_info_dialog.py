"""Tests for the custom movie info dialog."""
from resources.lib.ui.info_dialog import (
    INFO_PLAY,
    INFO_RESULT_PLAY,
    STR_GENRE,
    STR_RATED,
    STR_RATING,
    STR_RUNTIME,
    STR_YEAR,
    InfoDialog,
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


def test_format_runtime_exact_hour():
    assert format_runtime(3600) == "1h 0m"


def test_format_runtime_zero_is_empty():
    assert format_runtime(0) == ""


def test_format_rating_with_votes():
    assert format_rating(7.5, "2558") == "7.5 (2,558 votes)"


def test_format_rating_without_votes():
    assert format_rating(7.5, "") == "7.5"


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
        (STR_RATING, "7.5 (2,558 votes)"),
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


def _make_dialog():
    """Construct an InfoDialog without doModal (Kodistubs allow this)."""
    d = InfoDialog("script-easymovie-info.xml", "/tmp", "Default", "1080i")
    d._addon_id = "script.easymovie"
    d.movie = {"movieid": 1, "title": "T"}
    d.details = {"title": "T", "year": 2024, "rating": 7.5, "votes": "10",
                 "runtime": 6000, "mpaa": "Rated R", "genre": ["Action"],
                 "plot": "P", "tagline": "tag", "trailer": "", "art": {},
                 "cast": []}
    return d


def test_play_button_sets_play_result(monkeypatch):
    d = _make_dialog()
    closed = {"v": False}
    monkeypatch.setattr(d, "close", lambda: closed.__setitem__("v", True))
    d.onClick(INFO_PLAY)
    assert d.result == INFO_RESULT_PLAY
    assert closed["v"] is True


def test_back_leaves_no_play_result(monkeypatch):
    d = _make_dialog()
    monkeypatch.setattr(d, "close", lambda: None)

    class _A:
        def getId(self):
            return 92  # ACTION_NAV_BACK

    d.onAction(_A())
    assert d.result is None
