"""Tests for the browse window Info action handling."""
import xbmc
import xbmcgui

import resources.lib.ui.context_menu as cm

from resources.lib.constants import ACTION_CONTEXT_MENU, ACTION_SHOW_INFO
from resources.lib.ui import browse_window as bw
from resources.lib.ui.browse_window import (
    BrowseWindow,
    RESULT_ALREADY_PLAYING,
    show_browse_window,
)


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


class _FakeInfoTag:
    def __init__(self, dbid):
        self._dbid = dbid

    def getDbId(self):
        return self._dbid


class _FakePlayer:
    """Stand-in for xbmc.Player reporting a fixed playing state."""

    def __init__(self, playing, dbid=0):
        self._playing = playing
        self._dbid = dbid

    def isPlayingVideo(self):
        return self._playing

    def getVideoInfoTag(self):
        if not self._playing:
            raise RuntimeError("no tag")
        return _FakeInfoTag(self._dbid)


class _SpyStorage:
    def __init__(self):
        self.started = []

    def add_started(self, movieid, title=""):
        self.started.append((movieid, title))


def _patch_player(monkeypatch, player):
    monkeypatch.setattr(xbmc, "Player", lambda: player)
    monkeypatch.setattr(xbmc, "sleep", lambda ms: None)


def test_records_started_when_focused_movie_now_playing(monkeypatch):
    """Native Play from the pane records the movie as started for this instance."""
    window = _make_window()
    storage = _SpyStorage()
    window.set_storage(storage)
    _patch_player(monkeypatch, _FakePlayer(playing=True, dbid=42))

    recorded = window._record_native_play_if_playing(42, "Example")

    assert recorded is True
    assert storage.started == [(42, "Example")]


def test_does_not_record_when_nothing_is_playing(monkeypatch):
    """Closing the pane without playing records nothing."""
    window = _make_window()
    storage = _SpyStorage()
    window.set_storage(storage)
    _patch_player(monkeypatch, _FakePlayer(playing=False))

    recorded = window._record_native_play_if_playing(42, "Example")

    assert recorded is False
    assert storage.started == []


def test_show_browse_window_forwards_storage(monkeypatch):
    """show_browse_window passes the instance storage to the window."""
    captured = {}

    class _FakeWindow:
        def __init__(self, *args, **kwargs):
            pass

        def set_movies(self, movies):
            captured["movies"] = movies

        def set_addon_id(self, addon_id):
            captured["addon_id"] = addon_id

        def set_storage(self, storage):
            captured["storage"] = storage

        def doModal(self):
            pass

        @property
        def result(self):
            return None

    monkeypatch.setattr(bw, "BrowseWindow", _FakeWindow)
    sentinel = object()

    show_browse_window([], 0, "script.easymovie", storage=sentinel)

    assert captured["storage"] is sentinel


def test_does_not_record_when_a_different_movie_is_playing(monkeypatch):
    """A pre-existing playback of another movie is not recorded as this one."""
    window = _make_window()
    storage = _SpyStorage()
    window.set_storage(storage)
    _patch_player(monkeypatch, _FakePlayer(playing=True, dbid=999))

    recorded = window._record_native_play_if_playing(42, "Example")

    assert recorded is False
    assert storage.started == []


class _RecordingTag:
    """Infotag stub that accepts and ignores every setter call."""

    def __getattr__(self, name):
        return lambda *a, **k: None


class _RecordingListItem:
    def __init__(self, label=""):
        self.label = label
        self.path = None

    def getVideoInfoTag(self):
        return _RecordingTag()

    def setArt(self, art):
        pass

    def setPath(self, path):
        self.path = path


def test_build_info_listitem_sets_play_path(monkeypatch):
    """The info ListItem carries the file path so its Play button can play."""
    window = _make_window()
    captured = {}

    def make_listitem(label=""):
        item = _RecordingListItem(label)
        captured["item"] = item
        return item

    monkeypatch.setattr(xbmcgui, "ListItem", make_listitem)
    monkeypatch.setattr(xbmc, "Actor", lambda *a, **k: object())

    window._build_info_listitem(
        {"title": "X", "file": "smb://server/movies/Example.mkv"}, 42)

    assert captured["item"].path == "smb://server/movies/Example.mkv"


class _FakeInfoDialog:
    def __init__(self):
        self.info_calls = []

    def info(self, listitem):
        self.info_calls.append(listitem)
        return True


def _patch_info_pane(monkeypatch, details):
    """Stub the detail fetch and the native info dialog."""
    monkeypatch.setattr(bw, "json_query",
                        lambda query: {"moviedetails": details})
    dialog = _FakeInfoDialog()
    monkeypatch.setattr(xbmcgui, "Dialog", lambda: dialog)
    return dialog


def test_show_native_info_records_and_closes_on_native_play(monkeypatch):
    """Play pressed in the pane: record the play and close the browse window."""
    window = _make_window()
    storage = _SpyStorage()
    window.set_storage(storage)
    closed = []
    window.close = lambda: closed.append(True)
    dialog = _patch_info_pane(monkeypatch, {"title": "Example"})
    _patch_player(monkeypatch, _FakePlayer(playing=True, dbid=42))

    window._show_native_info({"movieid": 42, "title": "Example"})

    assert dialog.info_calls  # native pane was opened
    assert storage.started == [(42, "Example")]
    assert window.result == RESULT_ALREADY_PLAYING
    assert closed == [True]


def test_show_native_info_stays_open_when_pane_closed_without_play(monkeypatch):
    """Back out of the pane: no record, browse window stays open."""
    window = _make_window()
    storage = _SpyStorage()
    window.set_storage(storage)
    closed = []
    window.close = lambda: closed.append(True)
    _patch_info_pane(monkeypatch, {"title": "Example"})
    _patch_player(monkeypatch, _FakePlayer(playing=False))

    window._show_native_info({"movieid": 42, "title": "Example"})

    assert storage.started == []
    assert window.result is None
    assert closed == []


def test_info_action_with_focused_movie_triggers_native_info():
    """Pressing Info on a focused movie calls _show_native_info with it."""
    window = _make_window()
    movie = {"movieid": 42, "title": "Example"}
    window._get_focused_movie = lambda: movie
    calls = []
    window._show_native_info = lambda m: calls.append(m)

    window.onAction(_FakeAction(ACTION_SHOW_INFO))

    assert calls == [movie]


def test_info_action_with_no_focused_movie_does_nothing():
    """Pressing Info with no movie focused does not trigger native info."""
    window = _make_window()
    window._get_focused_movie = lambda: None
    calls = []
    window._show_native_info = lambda m: calls.append(m)

    window.onAction(_FakeAction(ACTION_SHOW_INFO))

    assert calls == []


def test_non_info_action_does_not_trigger_native_info(monkeypatch):
    """An unrelated action (context menu) does not call _show_native_info."""
    window = _make_window()
    window._get_focused_movie = lambda: {"movieid": 1, "title": "X"}
    calls = []
    window._show_native_info = lambda m: calls.append(m)

    # Context menu opens its own dialog; stub it so the branch is inert here.
    monkeypatch.setattr(cm, "show_context_menu", lambda movie, addon_id: None)

    window.onAction(_FakeAction(ACTION_CONTEXT_MENU))

    assert calls == []
