"""Tests for the browse window Info action handling."""
import resources.lib.ui.context_menu as cm
from resources.lib.constants import ACTION_CONTEXT_MENU, ACTION_SHOW_INFO
from resources.lib.ui import browse_window as bw
from resources.lib.ui.browse_window import BrowseWindow


def test_action_show_info_is_11():
    """ACTION_SHOW_INFO matches Kodi's standard Info action id."""
    assert ACTION_SHOW_INFO == 11


class _FakeAction:
    """Minimal stand-in for a Kodi action object."""

    def __init__(self, action_id):
        self._id = action_id

    def getId(self):
        return self._id

    def getButtonCode(self):
        return 0


def _make_window():
    """Construct a BrowseWindow without showing it (Kodistubs allow this)."""
    return BrowseWindow("x.xml", "/tmp", "Default", "1080i")


def test_show_info_plays_on_play_result(monkeypatch):
    """Play in the info dialog makes the browse window return the movie."""
    win = _make_window()
    movie = {"movieid": 7, "title": "T"}
    win._movies = [movie]
    monkeypatch.setattr(bw, "json_query",
                        lambda q: {"moviedetails": {"title": "T"}})
    monkeypatch.setattr(bw, "show_info_dialog",
                        lambda m, d, addon_id: bw.INFO_RESULT_PLAY)
    closed = {"v": False}
    monkeypatch.setattr(win, "close", lambda: closed.__setitem__("v", True))
    win._show_info(movie)
    assert win._result == movie
    assert closed["v"] is True


def test_show_info_cancel_keeps_window_open(monkeypatch):
    win = _make_window()
    movie = {"movieid": 7, "title": "T"}
    monkeypatch.setattr(bw, "json_query",
                        lambda q: {"moviedetails": {"title": "T"}})
    monkeypatch.setattr(bw, "show_info_dialog", lambda m, d, addon_id: None)
    closed = {"v": False}
    monkeypatch.setattr(win, "close", lambda: closed.__setitem__("v", True))
    win._show_info(movie)
    assert win._result is None
    assert closed["v"] is False


def test_info_action_with_focused_movie_triggers_native_info():
    """Pressing Info on a focused movie calls _show_info with it."""
    window = _make_window()
    movie = {"movieid": 42, "title": "Example"}
    window._get_focused_movie = lambda: movie
    calls = []
    window._show_info = lambda m: calls.append(m)

    window.onAction(_FakeAction(ACTION_SHOW_INFO))

    assert calls == [movie]


def test_info_action_with_no_focused_movie_does_nothing():
    """Pressing Info with no movie focused does not trigger native info."""
    window = _make_window()
    window._get_focused_movie = lambda: None
    calls = []
    window._show_info = lambda m: calls.append(m)

    window.onAction(_FakeAction(ACTION_SHOW_INFO))

    assert calls == []


def test_non_info_action_does_not_trigger_native_info(monkeypatch):
    """An unrelated action (context menu) does not call _show_info."""
    window = _make_window()
    window._get_focused_movie = lambda: {"movieid": 1, "title": "X"}
    calls = []
    window._show_info = lambda m: calls.append(m)

    # Context menu opens its own dialog; stub it so the branch is inert here.
    monkeypatch.setattr(cm, "show_context_menu", lambda movie, addon_id: None)

    window.onAction(_FakeAction(ACTION_CONTEXT_MENU))

    assert calls == []
