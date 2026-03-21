"""Tests for the filter wizard flow logic."""
from resources.lib.ui.wizard import WizardFlow
from resources.lib.constants import FILTER_ASK, FILTER_PRESET, FILTER_SKIP


def test_all_filters_ask():
    """When all filters are set to Ask, wizard has 7 steps."""
    settings = {
        "ignore_genre_mode": FILTER_ASK,
        "genre_mode": FILTER_ASK,
        "watched_mode": FILTER_ASK,
        "mpaa_mode": FILTER_ASK,
        "runtime_mode": FILTER_ASK,
        "year_mode": FILTER_ASK,
        "score_mode": FILTER_ASK,
    }
    flow = WizardFlow(settings)
    assert len(flow.steps) == 7


def test_all_filters_preset():
    """When all filters are preset, wizard has 0 steps (skip to results)."""
    settings = {
        "genre_mode": FILTER_PRESET,
        "watched_mode": FILTER_PRESET,
        "mpaa_mode": FILTER_PRESET,
        "runtime_mode": FILTER_PRESET,
        "year_mode": FILTER_PRESET,
        "score_mode": FILTER_PRESET,
    }
    flow = WizardFlow(settings)
    assert len(flow.steps) == 0


def test_all_filters_skip():
    """When all filters are skipped, wizard has 0 steps."""
    settings = {
        "genre_mode": FILTER_SKIP,
        "watched_mode": FILTER_SKIP,
        "mpaa_mode": FILTER_SKIP,
        "runtime_mode": FILTER_SKIP,
        "year_mode": FILTER_SKIP,
        "score_mode": FILTER_SKIP,
    }
    flow = WizardFlow(settings)
    assert len(flow.steps) == 0


def test_mixed_filters():
    """Only Ask filters create wizard steps."""
    settings = {
        "genre_mode": FILTER_ASK,
        "watched_mode": FILTER_SKIP,
        "mpaa_mode": FILTER_PRESET,
        "runtime_mode": FILTER_ASK,
        "year_mode": FILTER_SKIP,
        "score_mode": FILTER_SKIP,
    }
    flow = WizardFlow(settings)
    assert len(flow.steps) == 2


def test_back_navigation():
    """Going back returns to previous step."""
    settings = {
        "genre_mode": FILTER_ASK,
        "watched_mode": FILTER_ASK,
        "mpaa_mode": FILTER_SKIP,
        "runtime_mode": FILTER_ASK,
        "year_mode": FILTER_SKIP,
        "score_mode": FILTER_SKIP,
    }
    flow = WizardFlow(settings)
    assert flow.current_step_index == 0

    flow.advance()
    assert flow.current_step_index == 1

    flow.go_back()
    assert flow.current_step_index == 0


def test_go_back_at_start_returns_false():
    """Going back from first step signals cancellation."""
    settings = {"genre_mode": FILTER_ASK, "watched_mode": FILTER_SKIP,
                "mpaa_mode": FILTER_SKIP, "runtime_mode": FILTER_SKIP,
                "year_mode": FILTER_SKIP, "score_mode": FILTER_SKIP}
    flow = WizardFlow(settings)
    result = flow.go_back()
    assert result is False  # Signal to cancel wizard


def test_advance_returns_true_when_more_steps():
    """Advance returns True when there are more steps."""
    settings = {
        "genre_mode": FILTER_ASK,
        "watched_mode": FILTER_ASK,
        "mpaa_mode": FILTER_SKIP,
        "runtime_mode": FILTER_SKIP,
        "year_mode": FILTER_SKIP,
        "score_mode": FILTER_SKIP,
    }
    flow = WizardFlow(settings)
    result = flow.advance()
    assert result is True


def test_advance_returns_false_at_end():
    """Advance returns False when no more steps (wizard complete)."""
    settings = {
        "genre_mode": FILTER_ASK,
        "watched_mode": FILTER_SKIP,
        "mpaa_mode": FILTER_SKIP,
        "runtime_mode": FILTER_SKIP,
        "year_mode": FILTER_SKIP,
        "score_mode": FILTER_SKIP,
    }
    flow = WizardFlow(settings)
    result = flow.advance()
    assert result is False  # Only one step, now past it


def test_set_and_get_answer():
    """Answers can be set and retrieved."""
    settings = {
        "genre_mode": FILTER_ASK,
        "watched_mode": FILTER_SKIP,
        "mpaa_mode": FILTER_SKIP,
        "runtime_mode": FILTER_SKIP,
        "year_mode": FILTER_SKIP,
        "score_mode": FILTER_SKIP,
    }
    flow = WizardFlow(settings)
    flow.set_answer("genre", ["Action", "Comedy"])
    assert flow.get_answers()["genre"] == ["Action", "Comedy"]


def test_build_filter_config_from_answers():
    """Wizard answers should produce a valid FilterConfig."""
    settings = {
        "genre_mode": FILTER_ASK,
        "watched_mode": FILTER_PRESET,
        "watched_preset": 0,  # Unwatched
        "mpaa_mode": FILTER_SKIP,
        "runtime_mode": FILTER_SKIP,
        "year_mode": FILTER_SKIP,
        "score_mode": FILTER_SKIP,
    }
    flow = WizardFlow(settings)
    # Simulate user answering genre question
    flow.set_answer("genre", ["Action", "Comedy"])

    config = flow.build_filter_config()
    assert config.genres == ["Action", "Comedy"]
    assert config.watched == 0  # From preset


def test_build_filter_config_preset_genre():
    """Preset genres should be used when genre_mode is PRESET."""
    settings = {
        "genre_mode": FILTER_PRESET,
        "preset_genres": ["Drama", "Thriller"],
        "genre_match_and": True,
        "watched_mode": FILTER_SKIP,
        "mpaa_mode": FILTER_SKIP,
        "runtime_mode": FILTER_SKIP,
        "year_mode": FILTER_SKIP,
        "score_mode": FILTER_SKIP,
    }
    flow = WizardFlow(settings)
    config = flow.build_filter_config()
    assert config.genres == ["Drama", "Thriller"]
    assert config.genre_match_and is True


def test_is_complete_no_steps():
    """With no steps, wizard is immediately complete."""
    settings = {
        "genre_mode": FILTER_SKIP,
        "watched_mode": FILTER_SKIP,
        "mpaa_mode": FILTER_SKIP,
        "runtime_mode": FILTER_SKIP,
        "year_mode": FILTER_SKIP,
        "score_mode": FILTER_SKIP,
    }
    flow = WizardFlow(settings)
    assert flow.is_complete is True


def test_current_step_type():
    """Current step should return the correct filter type."""
    settings = {
        "genre_mode": FILTER_ASK,
        "watched_mode": FILTER_SKIP,
        "mpaa_mode": FILTER_ASK,
        "runtime_mode": FILTER_SKIP,
        "year_mode": FILTER_SKIP,
        "score_mode": FILTER_SKIP,
    }
    flow = WizardFlow(settings)
    assert flow.current_step.filter_type == "genre"
    flow.advance()
    assert flow.current_step.filter_type == "mpaa"


def test_ignore_genre_before_genre():
    """Ignore genre step appears before genre step in wizard."""
    settings = {
        "ignore_genre_mode": FILTER_ASK,
        "genre_mode": FILTER_ASK,
        "watched_mode": FILTER_SKIP,
        "mpaa_mode": FILTER_SKIP,
        "runtime_mode": FILTER_SKIP,
        "year_mode": FILTER_SKIP,
        "score_mode": FILTER_SKIP,
    }
    flow = WizardFlow(settings)
    assert len(flow.steps) == 2
    assert flow.steps[0].filter_type == "ignore_genre"
    assert flow.steps[1].filter_type == "genre"


def test_build_filter_config_ignore_genre_ask():
    """Wizard answers for ignore_genre flow through to FilterConfig."""
    settings = {
        "ignore_genre_mode": FILTER_ASK,
        "genre_mode": FILTER_SKIP,
        "watched_mode": FILTER_SKIP,
        "mpaa_mode": FILTER_SKIP,
        "runtime_mode": FILTER_SKIP,
        "year_mode": FILTER_SKIP,
        "score_mode": FILTER_SKIP,
    }
    flow = WizardFlow(settings)
    flow.set_answer("ignore_genre", ["Horror", "Documentary"])
    config = flow.build_filter_config()
    assert config.ignore_genres == ["Horror", "Documentary"]


def test_build_filter_config_ignore_genre_preset():
    """Preset ignore genres flow through to FilterConfig."""
    settings = {
        "ignore_genre_mode": FILTER_PRESET,
        "preset_ignore_genres": ["Horror"],
        "ignore_genre_match_and": True,
        "genre_mode": FILTER_SKIP,
        "watched_mode": FILTER_SKIP,
        "mpaa_mode": FILTER_SKIP,
        "runtime_mode": FILTER_SKIP,
        "year_mode": FILTER_SKIP,
        "score_mode": FILTER_SKIP,
    }
    flow = WizardFlow(settings)
    config = flow.build_filter_config()
    assert config.ignore_genres == ["Horror"]
    assert config.ignore_genre_match_and is True
