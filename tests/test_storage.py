"""Tests for persistent storage manager."""
import pytest
from resources.lib.data.storage import StorageManager


@pytest.fixture
def storage(tmp_path):
    return StorageManager(str(tmp_path / "easymovie_data.json"))


def test_save_and_load_suggested(storage):
    storage.add_suggested(movieid=123)
    storage.add_suggested(movieid=456)
    suggested = storage.get_suggested_ids()
    assert 123 in suggested
    assert 456 in suggested


def test_prune_old_suggestions(storage):
    # Add with old timestamp
    storage._data["suggested"].append({"movieid": 1, "timestamp": 0})
    storage.add_suggested(movieid=2)  # Current timestamp
    storage.prune_suggested(max_age_hours=1)
    ids = storage.get_suggested_ids()
    assert 1 not in ids
    assert 2 in ids


def test_save_and_load_started(storage):
    storage.add_started(movieid=789)
    started = storage.get_started_ids()
    assert 789 in started


def test_save_and_load_last_filters(storage):
    filters = {"genres": ["Action"], "watched": 0}
    storage.save_last_filters(filters)
    loaded = storage.load_last_filters()
    assert loaded == filters


def test_persistence(tmp_path):
    path = str(tmp_path / "easymovie_data.json")
    s1 = StorageManager(path)
    s1.add_suggested(movieid=100)
    s1.save()

    s2 = StorageManager(path)
    assert 100 in s2.get_suggested_ids()


def test_empty_storage(storage):
    assert storage.get_suggested_ids() == set()
    assert storage.get_started_ids() == set()
    assert storage.load_last_filters() == {}


def test_duplicate_suggested(storage):
    storage.add_suggested(movieid=42)
    storage.add_suggested(movieid=42)
    # Should not duplicate
    count = sum(1 for s in storage._data["suggested"] if s["movieid"] == 42)
    assert count == 1
