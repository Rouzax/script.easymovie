"""
Filter wizard flow controller.

Manages the sequence of filter dialogs, back navigation,
answer persistence, and building the final FilterConfig.

Logging:
    Logger: 'wizard'
    Key events:
        - filter.ask (INFO): Showing filter dialog to user
        - filter.preset (DEBUG): Filter using preset value
        - filter.skip (DEBUG): Filter skipped
    See LOGGING.md for full guidelines.
"""
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from resources.lib.constants import (
    FILTER_ASK, FILTER_PRESET, FILTER_SKIP,
    WATCHED_BOTH,
)
from resources.lib.data.filters import FilterConfig


# The ordered list of filter types in the wizard
FILTER_ORDER = ["genre", "watched", "mpaa", "runtime", "year", "score"]

# Mapping from filter type to settings mode key
_MODE_KEYS = {
    "genre": "genre_mode",
    "watched": "watched_mode",
    "mpaa": "mpaa_mode",
    "runtime": "runtime_mode",
    "year": "year_mode",
    "score": "score_mode",
}


@dataclass
class WizardStep:
    """A single step in the wizard flow."""
    filter_type: str
    index: int


class WizardFlow:
    """Manages the wizard flow for filter selection.

    Reads filter mode settings to determine which steps to show,
    maintains answer stack for back navigation, and builds a
    FilterConfig from combined preset + user answers.
    """

    def __init__(self, settings: Dict[str, Any]) -> None:
        """Initialize wizard from settings.

        Args:
            settings: Dict containing filter mode settings
                (genre_mode, watched_mode, etc.) and preset values.
        """
        self._settings = settings
        self._answers: Dict[str, Any] = {}
        self._current_index = 0

        # Build step list: only filters set to ASK
        self.steps: List[WizardStep] = []
        for i, filter_type in enumerate(FILTER_ORDER):
            mode_key = _MODE_KEYS[filter_type]
            mode = settings.get(mode_key, FILTER_SKIP)
            if mode == FILTER_ASK:
                self.steps.append(WizardStep(
                    filter_type=filter_type,
                    index=len(self.steps),
                ))

    @property
    def current_step_index(self) -> int:
        """Current position in the wizard."""
        return self._current_index

    @property
    def current_step(self) -> Optional[WizardStep]:
        """Get the current step, or None if complete."""
        if self._current_index < len(self.steps):
            return self.steps[self._current_index]
        return None

    @property
    def is_complete(self) -> bool:
        """Whether the wizard has no more steps."""
        return self._current_index >= len(self.steps)

    def advance(self) -> bool:
        """Move to the next step.

        Returns:
            True if there is a next step, False if wizard is now complete.
        """
        self._current_index += 1
        return self._current_index < len(self.steps)

    def go_back(self) -> bool:
        """Move to the previous step.

        Returns:
            True if moved back, False if already at start (signals cancel).
        """
        if self._current_index <= 0:
            return False
        self._current_index -= 1
        return True

    def set_answer(self, filter_type: str, value: Any) -> None:
        """Record the user's answer for a filter step."""
        self._answers[filter_type] = value

    def get_answers(self) -> Dict[str, Any]:
        """Get all recorded answers."""
        return dict(self._answers)

    def load_last_answers(self, answers: Dict[str, Any]) -> None:
        """Pre-populate answers from a previous session."""
        self._answers.update(answers)

    def build_filter_config(self) -> FilterConfig:
        """Build a FilterConfig from combined preset values and wizard answers.

        For each filter type:
        - ASK: use the wizard answer
        - PRESET: use the preset value from settings
        - SKIP: use default (no filter)
        """
        config = FilterConfig()

        # Genre
        genre_mode = self._settings.get("genre_mode", FILTER_SKIP)
        if genre_mode == FILTER_ASK:
            config.genres = self._answers.get("genre")
        elif genre_mode == FILTER_PRESET:
            config.genres = self._settings.get("preset_genres")
        config.genre_match_and = self._settings.get("genre_match_and", False)

        # Watched
        watched_mode = self._settings.get("watched_mode", FILTER_SKIP)
        if watched_mode == FILTER_ASK:
            config.watched = self._answers.get("watched", WATCHED_BOTH)
        elif watched_mode == FILTER_PRESET:
            config.watched = self._settings.get("watched_preset", WATCHED_BOTH)

        # MPAA
        mpaa_mode = self._settings.get("mpaa_mode", FILTER_SKIP)
        if mpaa_mode == FILTER_ASK:
            config.mpaa_ratings = self._answers.get("mpaa")
        elif mpaa_mode == FILTER_PRESET:
            config.mpaa_ratings = self._settings.get("preset_mpaa")

        # Runtime
        runtime_mode = self._settings.get("runtime_mode", FILTER_SKIP)
        if runtime_mode == FILTER_ASK:
            rt = self._answers.get("runtime", {})
            config.runtime_min = rt.get("min", 0)
            config.runtime_max = rt.get("max", 0)
        elif runtime_mode == FILTER_PRESET:
            config.runtime_min = self._settings.get("runtime_min", 0)
            config.runtime_max = self._settings.get("runtime_max", 0)

        # Year
        year_mode = self._settings.get("year_mode", FILTER_SKIP)
        if year_mode == FILTER_ASK:
            yr = self._answers.get("year", {})
            config.year_from = yr.get("from", 0)
            config.year_to = yr.get("to", 0)
        elif year_mode == FILTER_PRESET:
            config.year_from = self._settings.get("year_from", 0)
            config.year_to = self._settings.get("year_to", 0)

        # Score
        score_mode = self._settings.get("score_mode", FILTER_SKIP)
        if score_mode == FILTER_ASK:
            config.min_score = self._answers.get("score", 0)
        elif score_mode == FILTER_PRESET:
            config.min_score = self._settings.get("min_score", 0)

        return config
