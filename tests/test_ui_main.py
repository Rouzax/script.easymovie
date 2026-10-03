"""Tests for the special entry points handled by ui/main.py."""
import sys
from unittest.mock import MagicMock

import pytest

from resources.lib.ui import main


@pytest.fixture
def icon_browse(monkeypatch):
    """Run the set_icon entry point with 'Browse...' chosen in the picker."""
    vfs = MagicMock()
    vfs.translatePath.return_value = "/data/"
    vfs.copy.return_value = True
    gui = MagicMock()
    addon = MagicMock()
    addon.getAddonInfo.return_value = "/addon"
    log = MagicMock()

    monkeypatch.setattr(sys, "argv", ["default.py", "set_icon"])
    monkeypatch.setattr(main, "xbmcvfs", vfs)
    monkeypatch.setitem(sys.modules, "xbmcgui", gui)
    monkeypatch.setattr(main, "get_addon", lambda _addon_id: addon)
    monkeypatch.setattr(main, "get_logger", lambda _name: log)
    monkeypatch.setattr(main, "invalidate_icon_cache", MagicMock())
    monkeypatch.setattr(main, "_reopen_settings", MagicMock())
    # The last entry of the icon list is "Browse..."
    monkeypatch.setattr(main, "show_select_dialog", lambda **_kw: [4])

    def run(browsed_path):
        gui.Dialog.return_value.browse.return_value = browsed_path
        assert main._handle_entry_args("script.easymovie") is True
        return vfs, addon, log

    return run


def test_browsed_icon_with_invalid_utf8_name_is_not_copied(icon_browse):
    bad = b"/pics/Pok\xe9mon.png".decode("utf-8", "surrogateescape")
    vfs, addon, log = icon_browse(bad)
    vfs.copy.assert_not_called()
    addon.setSetting.assert_not_called()
    assert log.warning.call_args.kwargs["event"] == "icon.path_invalid"


def test_browsed_icon_with_valid_non_ascii_name_is_copied(icon_browse):
    vfs, addon, _log = icon_browse("/pics/Pokémon.png")
    vfs.copy.assert_any_call("/pics/Pokémon.png", "/addon/icon.png")
    addon.setSetting.assert_called_once_with("icon_choice", "custom")
