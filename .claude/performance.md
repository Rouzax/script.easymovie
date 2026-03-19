# JSON-RPC Performance Reference

Performance baselines for Kodi JSON-RPC queries. Use this to inform optimization decisions.

## Test Environment

- **Kodi Host:** vm2.home.lan (MariaDB backend)
- **Library:** 673 movies
- **Method:** Manual testing via curl

## Key Rules

1. **Bulk query > Per-movie iteration** — Fetch all movies once, filter client-side
2. **Skip art for data-only operations** — Saves ~40-50% query time
3. **Use server-side sorting/filtering** — No client overhead
4. **Use `limit` to bound result sets** — Count queries with `limit:1` are ~80-100ms

## Quick Reference Timings

| Operation | Expected Time | Strategy |
|-----------|---------------|----------|
| All movies (no art) | ~200-400ms | GetMovies standard props |
| All movies (with art) | ~400-800ms | GetMovies + artwork |
| Single movie by ID | ~80-100ms | GetMovieDetails |
| Movie set details | ~80-100ms | GetMovieSetDetails |
| All movie sets | ~50-100ms | GetMovieSets |

## EasyMovie Strategy

EasyMovie uses a two-phase query approach:

1. **Phase 1: Bulk data query** — Fetch all movies without art (~200-400ms). Apply filters client-side.
2. **Phase 2: Art query** — After filtering and selection, fetch art only for the ~10-20 movies being displayed.

This avoids fetching art for hundreds of movies that will be filtered out.

## DO

- Use bulk queries with client-side filtering
- Request only needed properties (skip art/streamdetails when not displayed)
- Use server-side `sort: { method: "random" }` for randomization
- Cache expensive query results where data is stable
- Use `limit` to bound result sets

## DON'T

- Query movies one-by-one in a loop (N+1 pattern)
- Request art properties for background/data operations
- Re-query data that was already fetched
