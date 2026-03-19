"""
Movie set awareness logic.

Handles finding the correct movie within a set (first unwatched),
substituting random picks, and determining set continuations.

Logging:
    Logger: 'data'
    Key events:
        - results.set_substitute (DEBUG): Movie substituted for set-correct entry
        - continuation.next_found (DEBUG): Next movie in set identified
    See LOGGING.md for full guidelines.
"""
from typing import Dict, List, Optional, Any


def find_first_unwatched_in_set(
    set_details: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    """Find the first unwatched movie in a set (by release order).

    Args:
        set_details: MovieSetDetails response with movies sorted by year.

    Returns:
        First unwatched movie dict, or None if all watched.
    """
    for movie in set_details.get("movies", []):
        if movie.get("playcount", 0) == 0:
            return movie
    return None


def apply_set_substitutions(
    movies: List[Dict[str, Any]],
    set_cache: Dict[int, Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Replace set-member movies with the first unwatched entry in their set.

    Also deduplicates: if multiple movies from the same set were picked,
    only the first occurrence (substituted) is kept.

    Args:
        movies: List of picked movie dicts.
        set_cache: Dict of setid -> GetMovieSetDetails response.

    Returns:
        New list with substitutions applied and set duplicates removed.
    """
    seen_sets = set()
    result = []

    for movie in movies:
        set_id = movie.get("setid", 0)

        if set_id and set_id in set_cache:
            # Skip if we already have a movie from this set
            if set_id in seen_sets:
                continue
            seen_sets.add(set_id)

            # Find first unwatched in set
            first_unwatched = find_first_unwatched_in_set(set_cache[set_id])
            if first_unwatched is not None:
                # Copy the substitute and preserve set info
                substitute = dict(first_unwatched)
                substitute["set"] = movie.get("set", "")
                substitute["setid"] = set_id
                result.append(substitute)
            else:
                # All watched — keep original pick
                result.append(movie)
        else:
            result.append(movie)

    return result


def get_next_in_set(
    set_details: Dict[str, Any],
    current_movie_id: int,
) -> Optional[Dict[str, Any]]:
    """Get the next movie in a set after the given movie.

    Used for continuation prompts: "You just watched X,
    want to watch Y next?"

    Args:
        set_details: MovieSetDetails response with movies sorted by year.
        current_movie_id: The movie that was just watched.

    Returns:
        Next movie dict, or None if current is last or not found.
    """
    movies = set_details.get("movies", [])
    for i, movie in enumerate(movies):
        if movie.get("movieid") == current_movie_id:
            if i + 1 < len(movies):
                return movies[i + 1]
            return None
    return None
