"""Tests for settings loader."""
import sys
from unittest.mock import MagicMock

import pytest


@pytest.fixture(autouse=True)
def mock_kodi(monkeypatch):
    """Mock Kodi modules for settings tests."""
    xbmc = MagicMock()
    xbmcaddon = MagicMock()
    xbmcgui = MagicMock()
    xbmcvfs = MagicMock()

    monkeypatch.setitem(sys.modules, 'xbmc', xbmc)
    monkeypatch.setitem(sys.modules, 'xbmcaddon', xbmcaddon)
    monkeypatch.setitem(sys.modules, 'xbmcgui', xbmcgui)
    monkeypatch.setitem(sys.modules, 'xbmcvfs', xbmcvfs)

    # Clear cached modules
    for mod in list(sys.modules):
        if mod.startswith('resources.lib'):
            del sys.modules[mod]

    # Configure addon mock to return setting values
    addon_mock = MagicMock()
    xbmcaddon.Addon.return_value = addon_mock

    yield addon_mock


def _setup_settings(addon_mock, settings_dict):
    """Configure addon mock to return specific setting values."""
    def get_setting(key):
        return str(settings_dict.get(key, ''))
    addon_mock.getSetting.side_effect = get_setting


def test_load_settings_defaults(mock_kodi):
    """Settings loader returns valid defaults for empty settings."""
    _setup_settings(mock_kodi, {})

    from resources.lib.ui.settings import load_settings
    result = load_settings()
    assert len(result) == 8

    primary_function, theme, filters, browse, playlist, sets, playback, advanced = result
    assert filters.genre_mode == 0  # Default from int parse
    assert browse.result_count == 10  # Explicit default
    assert playlist.movie_count == 5


def test_load_settings_filter_modes(mock_kodi):
    """Filter modes are correctly parsed."""
    _setup_settings(mock_kodi, {
        'genre_mode': '1',    # FILTER_PRESET
        'watched_mode': '2',  # FILTER_SKIP
        'mpaa_mode': '0',     # FILTER_ASK
    })

    from resources.lib.ui.settings import load_settings
    _, _, filters, _, _, _, _, _ = load_settings()
    assert filters.genre_mode == 1
    assert filters.watched_mode == 2
    assert filters.mpaa_mode == 0


def test_load_settings_preset_genres(mock_kodi):
    """JSON genre presets are parsed correctly."""
    _setup_settings(mock_kodi, {
        'selected_genres': '["Action", "Comedy"]',
    })

    from resources.lib.ui.settings import load_settings
    _, _, filters, _, _, _, _, _ = load_settings()
    assert filters.preset_genres == ["Action", "Comedy"]


def test_load_settings_invalid_json_genres(mock_kodi):
    """Invalid JSON returns None for presets."""
    _setup_settings(mock_kodi, {
        'selected_genres': 'not json',
    })

    from resources.lib.ui.settings import load_settings
    _, _, filters, _, _, _, _, _ = load_settings()
    assert filters.preset_genres is None


def test_load_settings_browse(mock_kodi):
    """Browse settings are parsed correctly."""
    _setup_settings(mock_kodi, {
        'view_style': '2',
        'return_to_list': 'true',
        'browse_count': '20',
        'browse_sort': '1',
        'browse_sort_dir': '0',
    })

    from resources.lib.ui.settings import load_settings
    _, _, _, browse, _, _, _, _ = load_settings()
    assert browse.view_style == 2
    assert browse.return_to_list is True
    assert browse.result_count == 20
    assert browse.sort_by == 1
    assert browse.sort_dir == 0


def test_load_settings_set_settings(mock_kodi):
    """Movie set settings are parsed correctly."""
    _setup_settings(mock_kodi, {
        'set_enabled': 'true',
        'continuation_enabled': 'true',
        'continuation_duration': '30',
    })

    from resources.lib.ui.settings import load_settings
    _, _, _, _, _, sets, _, _ = load_settings()
    assert sets.enabled is True
    assert sets.continuation_enabled is True
    assert sets.continuation_duration == 30
