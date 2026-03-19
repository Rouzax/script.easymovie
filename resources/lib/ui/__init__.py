"""
UI package initialization.

Provides theme application for all EasyMovie windows.
"""
import xbmcgui

from resources.lib.constants import THEME_COLORS, KODI_HOME_WINDOW_ID


def apply_theme(theme_id: int) -> None:
    """Apply theme colors as window properties.

    Args:
        theme_id: Theme constant (THEME_GOLDEN_HOUR, etc.)
    """
    home = xbmcgui.Window(KODI_HOME_WINDOW_ID)
    colors = THEME_COLORS.get(theme_id, THEME_COLORS[0])
    for prop, value in colors.items():
        home.setProperty(prop, value)
