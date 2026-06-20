"""Integration tests for the full EasyMovie flow."""

SAMPLE_MOVIES = [
    {
        "movieid": 1, "title": "Action Hero",
        "genre": ["Action", "Thriller"], "year": 2024,
        "rating": 7.5, "runtime": 6600,
        "mpaa": "Rated R", "set": "Hero Collection", "setid": 10,
        "playcount": 0, "dateadded": "2024-01-15",
        "file": "/movies/action.mkv", "resume": {"position": 0, "total": 0},
        "lastplayed": "",
    },
    {
        "movieid": 2, "title": "Comedy Night",
        "genre": ["Comedy"], "year": 2023,
        "rating": 6.5, "runtime": 5400,
        "mpaa": "Rated PG-13", "set": "", "setid": 0,
        "playcount": 1, "dateadded": "2023-06-01",
        "file": "/movies/comedy.mkv", "resume": {"position": 0, "total": 0},
        "lastplayed": "2024-01-01",
    },
    {
        "movieid": 3, "title": "Drama Classic",
        "genre": ["Drama"], "year": 1995,
        "rating": 8.5, "runtime": 8400,
        "mpaa": "Rated R", "set": "", "setid": 0,
        "playcount": 0, "dateadded": "2022-03-10",
        "file": "/movies/drama.mkv", "resume": {"position": 0, "total": 0},
        "lastplayed": "",
    },
]


class TestFilterIntegration:
    """Test the filter pipeline end-to-end."""

    def test_all_presets_straight_to_results(self):
        """When all filters are preset, wizard has no steps."""
        from resources.lib.constants import FILTER_PRESET
        from resources.lib.ui.wizard import WizardFlow

        settings = {
            "genre_mode": FILTER_PRESET,
            "preset_genres": ["Action"],
            "genre_match_and": False,
            "watched_mode": FILTER_PRESET,
            "watched_preset": 0,
            "mpaa_mode": FILTER_PRESET,
            "preset_mpaa": ["Rated R"],
            "runtime_mode": FILTER_PRESET,
            "runtime_min": 0,
            "runtime_max": 0,
            "year_mode": FILTER_PRESET,
            "year_from": 0,
            "year_to": 0,
            "score_mode": FILTER_PRESET,
            "min_score": 0,
        }
        flow = WizardFlow(settings)
        assert flow.is_complete

        config = flow.build_filter_config()
        assert config.genres == ["Action"]
        assert config.watched == 0
        assert config.mpaa_ratings == ["Rated R"]

    def test_filter_then_sort_pipeline(self):
        """Filtering + sorting produces valid results."""
        from resources.lib.data.filters import FilterConfig, apply_filters
        from resources.lib.data.results import select_and_sort_results
        from resources.lib.constants import SORT_TITLE, SORT_ASC

        config = FilterConfig(
            genres=["Action", "Drama"],
            genre_match_and=False,
            watched=0,
        )
        filtered = apply_filters(SAMPLE_MOVIES, config)
        assert len(filtered) == 2  # Action Hero + Drama Classic

        results = select_and_sort_results(filtered, count=10,
                                          sort_by=SORT_TITLE, sort_dir=SORT_ASC)
        assert results[0]["title"] == "Action Hero"
        assert results[1]["title"] == "Drama Classic"

    def test_no_results_after_filtering(self):
        """Strict filters can produce empty results."""
        from resources.lib.data.filters import FilterConfig, apply_filters

        config = FilterConfig(
            genres=["SciFi"],
            genre_match_and=False,
        )
        filtered = apply_filters(SAMPLE_MOVIES, config)
        assert len(filtered) == 0


class TestMovieSetIntegration:
    """Test movie set substitution in the result pipeline."""

    def test_set_substitution_in_results(self):
        """Movies from sets get substituted with first unwatched."""
        from resources.lib.data.movie_sets import apply_set_substitutions

        picked = [
            {"movieid": 1, "setid": 10, "set": "Hero Collection"},
            {"movieid": 2, "setid": 0, "set": ""},
        ]
        set_cache = {
            10: {
                "setid": 10,
                "title": "Hero Collection",
                "movies": [
                    {"movieid": 5, "title": "Hero 1", "playcount": 1, "year": 2020},
                    {"movieid": 1, "title": "Hero 2", "playcount": 0, "year": 2022},
                    {"movieid": 6, "title": "Hero 3", "playcount": 0, "year": 2024},
                ],
            }
        }
        result = apply_set_substitutions(picked, set_cache)
        # Should substitute with first unwatched (Hero 2, movieid=1)
        assert result[0]["movieid"] == 1
        assert result[1]["movieid"] == 2


class TestStorageIntegration:
    """Test storage with filter pipeline."""

    def test_exclude_suggested_movies(self):
        """Previously suggested movies are excluded from results."""
        from resources.lib.data.filters import FilterConfig, apply_filters

        config = FilterConfig(exclude_ids=[1, 2])
        filtered = apply_filters(SAMPLE_MOVIES, config)
        assert len(filtered) == 1
        assert filtered[0]["movieid"] == 3


class TestWizardFilterConfigIntegration:
    """Test wizard answers producing correct filter configs."""

    def test_wizard_answers_to_filter_to_results(self):
        """Full pipeline: wizard answers → FilterConfig → apply → results."""
        from resources.lib.constants import FILTER_ASK, FILTER_SKIP
        from resources.lib.ui.wizard import WizardFlow
        from resources.lib.data.filters import apply_filters
        from resources.lib.data.results import select_and_sort_results
        from resources.lib.constants import SORT_RATING, SORT_DESC

        settings = {
            "genre_mode": FILTER_ASK,
            "watched_mode": FILTER_SKIP,
            "mpaa_mode": FILTER_SKIP,
            "runtime_mode": FILTER_SKIP,
            "year_mode": FILTER_SKIP,
            "score_mode": FILTER_SKIP,
        }
        flow = WizardFlow(settings)
        flow.set_answer("genre", ["Drama"])
        flow.advance()

        config = flow.build_filter_config()
        filtered = apply_filters(SAMPLE_MOVIES, config)
        assert len(filtered) == 1
        assert filtered[0]["title"] == "Drama Classic"

        results = select_and_sort_results(filtered, count=5,
                                          sort_by=SORT_RATING, sort_dir=SORT_DESC)
        assert results[0]["rating"] == 8.5


class TestPlaylistIntegration:
    """Test playlist selection pipeline."""

    def test_playlist_mode_selects_correct_count(self):
        """Playlist mode respects movie count setting."""
        from resources.lib.data.results import select_and_sort_results
        from resources.lib.constants import SORT_RANDOM, SORT_ASC

        results = select_and_sort_results(
            SAMPLE_MOVIES, count=2,
            sort_by=SORT_RANDOM, sort_dir=SORT_ASC,
        )
        assert len(results) == 2

    def test_reroll_produces_different_order(self):
        """Re-roll can produce different results (probabilistic)."""
        from resources.lib.data.results import select_and_sort_results
        from resources.lib.constants import SORT_RANDOM, SORT_ASC

        # With 3 movies and count=3, order may differ
        large_pool = SAMPLE_MOVIES * 10  # 30 movies
        results1 = select_and_sort_results(large_pool, count=3,
                                           sort_by=SORT_RANDOM, sort_dir=SORT_ASC)
        # Multiple attempts to get different results
        different = False
        for _ in range(10):
            results2 = select_and_sort_results(large_pool, count=3,
                                               sort_by=SORT_RANDOM, sort_dir=SORT_ASC)
            if [m["movieid"] for m in results1] != [m["movieid"] for m in results2]:
                different = True
                break
        assert different, "Re-roll should produce different results"
