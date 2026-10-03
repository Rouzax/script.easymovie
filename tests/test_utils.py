"""Tests for utils.py core functions."""
import time
from unittest.mock import MagicMock

import pytest


@pytest.fixture(autouse=True)
def mock_kodi_modules(monkeypatch):
    """Mock Kodi modules that aren't available in test environment."""
    xbmc = MagicMock()
    xbmcaddon = MagicMock()
    xbmcgui = MagicMock()
    xbmcvfs = MagicMock()

    monkeypatch.setitem(__import__('sys').modules, 'xbmc', xbmc)
    monkeypatch.setitem(__import__('sys').modules, 'xbmcaddon', xbmcaddon)
    monkeypatch.setitem(__import__('sys').modules, 'xbmcgui', xbmcgui)
    monkeypatch.setitem(__import__('sys').modules, 'xbmcvfs', xbmcvfs)

    # Reset singleton state
    if 'resources.lib.utils' in __import__('sys').modules:
        del __import__('sys').modules['resources.lib.utils']
    if 'resources.lib.constants' in __import__('sys').modules:
        del __import__('sys').modules['resources.lib.constants']

    yield {
        'xbmc': xbmc,
        'xbmcaddon': xbmcaddon,
        'xbmcgui': xbmcgui,
        'xbmcvfs': xbmcvfs,
    }


class TestStructuredLogger:
    def test_format_message_no_kwargs(self, mock_kodi_modules):
        from resources.lib.utils import StructuredLogger
        logger = StructuredLogger("test")
        result = logger._format_message("hello")
        assert result == "[EasyMovie.test] hello"

    def test_format_message_with_kwargs(self, mock_kodi_modules):
        from resources.lib.utils import StructuredLogger
        logger = StructuredLogger("test")
        result = logger._format_message("hello", key="value", count=42)
        assert "[EasyMovie.test] hello | " in result
        assert "key=value" in result
        assert "count=42" in result

    def test_format_message_truncates_long_values(self, mock_kodi_modules):
        from resources.lib.utils import StructuredLogger
        logger = StructuredLogger("test")
        long_value = "x" * 300
        result = logger._format_message("msg", data=long_value)
        assert "..." in result
        assert len(result) < len(long_value) + 100

    def test_module_name_in_prefix(self, mock_kodi_modules):
        from resources.lib.utils import StructuredLogger
        logger = StructuredLogger("wizard")
        result = logger._format_message("test")
        assert "[EasyMovie.wizard]" in result

    def test_format_message_replaces_lone_surrogates(self, mock_kodi_modules):
        from resources.lib.utils import StructuredLogger
        logger = StructuredLogger("test")
        bad = b"Pok\xe9mon".decode("utf-8", "surrogateescape")
        result = logger._format_message(bad, path=bad)
        result.encode("utf-8")  # raises if a surrogate survived
        assert "Pok?mon" in result

    def test_format_message_keeps_valid_non_ascii(self, mock_kodi_modules):
        from resources.lib.utils import StructuredLogger
        logger = StructuredLogger("test")
        result = logger._format_message("Pokémon ☃", title="Amélie")
        assert result == "[EasyMovie.test] Pokémon ☃ | title=Amélie"

    def test_info_hands_xbmc_log_utf8_encodable_text(self, mock_kodi_modules):
        from resources.lib.utils import StructuredLogger
        logger = StructuredLogger("test")
        bad = b"Pok\xe9mon".decode("utf-8", "surrogateescape")
        logger.info("Movie", event="test.event", title=bad)
        logged = mock_kodi_modules['xbmc'].log.call_args[0][0]
        logged.encode("utf-8")
        assert "title=Pok?mon" in logged


class TestJsonQuery:
    def test_invalid_utf8_becomes_replacement_character(self, mock_kodi_modules):
        from resources.lib.utils import json_query
        raw = b'{"result": {"title": "Pok\xe9mon"}}'
        # Kodi decodes executeJSONRPC output with surrogateescape
        mock_kodi_modules['xbmc'].executeJSONRPC.return_value = raw.decode(
            "utf-8", "surrogateescape")
        result = json_query({"method": "VideoLibrary.GetMovies"})
        assert result == {"title": "Pok�mon"}

    @pytest.fixture
    def debug_lines(self, mock_kodi_modules, monkeypatch):
        """Enable debug logging and collect the lines written to the log file."""
        from resources.lib.utils import StructuredLogger
        lines = []
        monkeypatch.setattr(StructuredLogger, "_initialized", True)
        monkeypatch.setattr(StructuredLogger, "_debug_enabled", True)
        monkeypatch.setattr(StructuredLogger, "_write_to_file",
                            lambda self, level, msg: lines.append((level, msg)))
        return lines

    @staticmethod
    def _respond(mock_kodi_modules, raw):
        mock_kodi_modules['xbmc'].executeJSONRPC.return_value = raw.decode(
            "utf-8", "surrogateescape")

    def test_replacement_is_logged_with_owning_item(self, mock_kodi_modules,
                                                     debug_lines):
        from resources.lib.utils import json_query
        self._respond(mock_kodi_modules,
                      b'{"result": {"movies": [{"movieid": 7, "title": "Up"},'
                      b' {"movieid": 812, "title": "Am\xe9lie", "plot": "ok"}]}}')
        json_query({"method": "VideoLibrary.GetMovies"})
        assert len(debug_lines) == 1
        level, msg = debug_lines[0]
        assert level == "DEBUG"
        assert "event=jsonrpc.invalid_utf8" in msg
        assert "method=VideoLibrary.GetMovies" in msg
        assert "field=result.movies[1].title" in msg
        assert "movieid=812" in msg

    def test_replacement_in_list_names_the_enclosing_item(self, mock_kodi_modules,
                                                           debug_lines):
        from resources.lib.utils import json_query
        self._respond(mock_kodi_modules,
                      b'{"result": {"movies": [{"movieid": 3, "title": "Heat",'
                      b' "genre": ["Crime", "Dr\xe9ma"]}]}}')
        json_query({"method": "VideoLibrary.GetMovies"})
        _level, msg = debug_lines[0]
        assert "field=result.movies[0].genre[1]" in msg
        assert "movieid=3" in msg
        assert "item=Heat" in msg

    def test_clean_response_logs_nothing(self, mock_kodi_modules, debug_lines):
        from resources.lib.utils import json_query
        self._respond(mock_kodi_modules,
                      '{"result": {"movies": [{"title": "Pokémon �"}]}}'.encode())
        json_query({"method": "VideoLibrary.GetMovies"})
        assert debug_lines == []

    def test_valid_non_ascii_passes_unchanged(self, mock_kodi_modules):
        from resources.lib.utils import json_query
        raw = '{"result": {"title": "Pokémon ☃"}}'.encode("utf-8")
        mock_kodi_modules['xbmc'].executeJSONRPC.return_value = raw.decode(
            "utf-8", "surrogateescape")
        result = json_query({"method": "VideoLibrary.GetMovies"})
        assert result == {"title": "Pokémon ☃"}


class TestSettingHelpers:
    def test_get_bool_setting_true(self, mock_kodi_modules):
        addon_mock = MagicMock()
        addon_mock.getSetting.return_value = 'true'
        mock_kodi_modules['xbmcaddon'].Addon.return_value = addon_mock

        from resources.lib.utils import get_bool_setting
        assert get_bool_setting('test_setting') is True

    def test_get_bool_setting_false(self, mock_kodi_modules):
        addon_mock = MagicMock()
        addon_mock.getSetting.return_value = 'false'
        mock_kodi_modules['xbmcaddon'].Addon.return_value = addon_mock

        from resources.lib.utils import get_bool_setting
        assert get_bool_setting('test_setting') is False

    def test_get_int_setting(self, mock_kodi_modules):
        addon_mock = MagicMock()
        addon_mock.getSetting.return_value = '42'
        mock_kodi_modules['xbmcaddon'].Addon.return_value = addon_mock

        from resources.lib.utils import get_int_setting
        assert get_int_setting('count') == 42

    def test_get_int_setting_float_value(self, mock_kodi_modules):
        addon_mock = MagicMock()
        addon_mock.getSetting.return_value = '3.7'
        mock_kodi_modules['xbmcaddon'].Addon.return_value = addon_mock

        from resources.lib.utils import get_int_setting
        assert get_int_setting('count') == 3

    def test_get_int_setting_invalid(self, mock_kodi_modules):
        addon_mock = MagicMock()
        addon_mock.getSetting.return_value = 'not_a_number'
        mock_kodi_modules['xbmcaddon'].Addon.return_value = addon_mock

        from resources.lib.utils import get_int_setting
        assert get_int_setting('count', default=5) == 5

    def test_get_string_setting(self, mock_kodi_modules):
        addon_mock = MagicMock()
        addon_mock.getSetting.return_value = 'hello'
        mock_kodi_modules['xbmcaddon'].Addon.return_value = addon_mock

        from resources.lib.utils import get_string_setting
        assert get_string_setting('name') == 'hello'


class TestLang:
    def test_lang_returns_localized_string(self, mock_kodi_modules):
        addon_mock = MagicMock()
        addon_mock.getLocalizedString.return_value = 'Translated'
        mock_kodi_modules['xbmcaddon'].Addon.return_value = addon_mock

        from resources.lib.utils import lang
        result = lang(32000)
        addon_mock.getLocalizedString.assert_called_with(32000)
        assert result == 'Translated'


class TestLogTiming:
    def test_log_timing_captures_duration(self, mock_kodi_modules):
        from resources.lib.utils import StructuredLogger, log_timing
        logger = StructuredLogger("test")
        logger._write_to_file = MagicMock()

        # Force debug enabled so the timing log fires
        StructuredLogger._debug_enabled = True
        try:
            with log_timing(logger, "test_op"):
                time.sleep(0.01)

            # Verify debug was called (via _write_to_file)
            assert logger._write_to_file.called
            call_args = logger._write_to_file.call_args
            assert "test_op completed" in call_args[0][1]
            assert "duration_ms=" in call_args[0][1]
        finally:
            StructuredLogger._debug_enabled = False

    def test_log_timing_with_phases(self, mock_kodi_modules):
        from resources.lib.utils import StructuredLogger, log_timing
        logger = StructuredLogger("test")
        logger._write_to_file = MagicMock()

        StructuredLogger._debug_enabled = True
        try:
            with log_timing(logger, "multi_phase") as timer:
                time.sleep(0.01)
                timer.mark("phase1")
                time.sleep(0.01)
                timer.mark("phase2")

            call_args = logger._write_to_file.call_args
            logged_msg = call_args[0][1]
            assert "phase1_ms=" in logged_msg
            assert "phase2_ms=" in logged_msg
        finally:
            StructuredLogger._debug_enabled = False
