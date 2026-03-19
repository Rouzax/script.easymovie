"""
Centralized constants for EasyMovie.

All magic numbers, string literals, property names, setting IDs,
and configuration values live here. Import from this module rather
than hardcoding values elsewhere.
"""

# Addon identity
ADDON_ID = "script.easymovie"
ADDON_NAME = "EasyMovie"

# Kodi window IDs
KODI_HOME_WINDOW_ID = 10000

# Window property prefixes
PROP_PREFIX = "EasyMovie"

# Log file configuration
LOG_DIR = "logs"
LOG_FILENAME = "easymovie.log"
LOG_MAX_BYTES = 500 * 1024  # 500KB
LOG_BACKUP_COUNT = 3
LOG_MAX_VALUE_LENGTH = 200
LOG_TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S.%f"
LOG_TIMESTAMP_TRIM = 23  # Trim microseconds to milliseconds

# Primary function modes
MODE_BROWSE = 0
MODE_PLAYLIST = 1
MODE_ASK = 2

# Filter modes (for settings: Ask / Pre-set / Skip)
FILTER_ASK = 0
FILTER_PRESET = 1
FILTER_SKIP = 2

# Watched status values
WATCHED_UNWATCHED = 0
WATCHED_WATCHED = 1
WATCHED_BOTH = 2

# Genre matching modes
GENRE_MATCH_OR = 0
GENRE_MATCH_AND = 1

# Year filter types
YEAR_FILTER_AFTER = 0
YEAR_FILTER_BEFORE = 1
YEAR_FILTER_BETWEEN = 2

# Sort options
SORT_RANDOM = 0
SORT_TITLE = 1
SORT_YEAR = 2
SORT_RATING = 3
SORT_RUNTIME = 4
SORT_DATE_ADDED = 5

# Sort directions
SORT_ASC = 0
SORT_DESC = 1

# View styles
VIEW_POSTER_GRID = 0  # New EasyMovie default
VIEW_CARD_LIST = 1
VIEW_POSTERS = 2
VIEW_BIG_SCREEN = 3
VIEW_SPLIT_VIEW = 4

# Theme IDs (shared with EasyTV)
THEME_GOLDEN_HOUR = 0
THEME_ULTRAVIOLET = 1
THEME_EMBER = 2
THEME_NIGHTFALL = 3

# Theme color definitions (AARRGGBB format)
# Same values as EasyTV for visual consistency
THEME_COLORS = {
    THEME_GOLDEN_HOUR: {
        'EasyMovie.Accent': 'FFF5A623',
        'EasyMovie.AccentGlow': 'FFF5C564',
        'EasyMovie.AccentBG': '59B4781E',
        'EasyMovie.ButtonTextFocused': 'FF0D1117',
        'EasyMovie.ButtonFocus': 'FFD4912A',
    },
    THEME_ULTRAVIOLET: {
        'EasyMovie.Accent': 'FFA78BFA',
        'EasyMovie.AccentGlow': 'FFC4B5FD',
        'EasyMovie.AccentBG': '596432B4',
        'EasyMovie.ButtonTextFocused': 'FFFFFFFF',
        'EasyMovie.ButtonFocus': 'FF7C3AED',
    },
    THEME_EMBER: {
        'EasyMovie.Accent': 'FFF87171',
        'EasyMovie.AccentGlow': 'FFFCA5A5',
        'EasyMovie.AccentBG': '59B43232',
        'EasyMovie.ButtonTextFocused': 'FFFFFFFF',
        'EasyMovie.ButtonFocus': 'FFEF4444',
    },
    THEME_NIGHTFALL: {
        'EasyMovie.Accent': 'FF60A5FA',
        'EasyMovie.AccentGlow': 'FF93C5FD',
        'EasyMovie.AccentBG': '59286AB4',
        'EasyMovie.ButtonTextFocused': 'FFFFFFFF',
        'EasyMovie.ButtonFocus': 'FF3B82F6',
    },
}

# Re-suggestion window options (hours)
RESURFACE_WINDOWS = {
    0: 4,
    1: 8,
    2: 12,
    3: 24,
    4: 48,
    5: 72,
}

# Runtime filter ranges for wizard (in minutes)
RUNTIME_RANGES = [
    (0, 90, "Under 90 minutes"),
    (90, 120, "90 – 120 minutes"),
    (120, 150, "120 – 150 minutes"),
    (150, 0, "Over 150 minutes"),  # 0 = no upper limit
    (0, 0, "Any runtime"),  # both 0 = no filter
]

# Score filter ranges for wizard
SCORE_RANGES = [
    (80, "8.0+ (Excellent)"),
    (70, "7.0+ (Good)"),
    (60, "6.0+ (Above Average)"),
    (50, "5.0+ (Average)"),
    (0, "Any score"),
]

# Timing constants (milliseconds)
NOTIFICATION_DURATION_MS = 5000
DIALOG_WAIT_SLEEP_MS = 100
PLAYLIST_ADD_DELAY_MS = 50

# Playback
PLAYBACK_COMPLETE_THRESHOLD = 0.90  # 90% watched = complete

# Continuation prompt
CONTINUATION_DEFAULT_CONTINUE_SET = 0
CONTINUATION_DEFAULT_CONTINUE_PLAYLIST = 1

# Version prerelease ordering
VERSION_PRERELEASE_ALPHA = 0
VERSION_PRERELEASE_BETA = 1
VERSION_PRERELEASE_RELEASE = 2
