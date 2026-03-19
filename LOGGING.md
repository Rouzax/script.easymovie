# EasyMovie Logging Guide

**Version:** 1.0
**Last Updated:** 2026-03-19

This guide covers the logging system in EasyMovie for both users and developers.

---

## For Users

### Enabling Debug Logging

1. Go to **Settings** → **Advanced** → **Debugging**
2. Enable **"Enable debug logging"**
3. Reproduce the issue you're troubleshooting
4. Find the log file at: `special://profile/addon_data/script.easymovie/logs/easymovie.log`

### Log File Location

The debug log is stored separately from Kodi's main log:

| Platform  | Typical Path                                                                             |
| --------- | ---------------------------------------------------------------------------------------- |
| Windows   | `%APPDATA%\Kodi\userdata\addon_data\script.easymovie\logs\easymovie.log`                 |
| Linux     | `~/.kodi/userdata/addon_data/script.easymovie/logs/easymovie.log`                        |
| macOS     | `~/Library/Application Support/Kodi/userdata/addon_data/script.easymovie/logs/easymovie.log` |
| LibreELEC | `/storage/.kodi/userdata/addon_data/script.easymovie/logs/easymovie.log`                 |

### Log File Management

- Maximum file size: **500KB**
- Rotated files: `easymovie.1.log`, `easymovie.2.log`, `easymovie.3.log`
- Older files are automatically deleted when rotated

### What Gets Logged Where

| Log Level   | When Debug OFF | When Debug ON           |
| ----------- | -------------- | ----------------------- |
| **ERROR**   | Kodi log only  | Kodi log + easymovie.log |
| **WARNING** | Kodi log only  | Kodi log + easymovie.log |
| **INFO**    | Kodi log only  | Kodi log + easymovie.log |
| **DEBUG**   | Not logged     | easymovie.log only       |

This design keeps Kodi's log clean while giving you detailed debug information in a separate file.

---

## For Developers

### Architecture Overview

EasyMovie uses a custom `StructuredLogger` class that provides:

1. **Dual output** — INFO/WARNING/ERROR go to Kodi log; DEBUG goes to file only
2. **Structured logging** — Key-value pairs for machine-readable context
3. **Event naming** — Consistent `domain.action` event taxonomy
4. **Thread safety** — All file operations are lock-protected
5. **Automatic rotation** — Files rotate at 500KB

### Getting a Logger

```python
from resources.lib.utils import get_logger

log = get_logger('module_name')
```

Logger names by package:

| Package      | Logger Name                                |
| ------------ | ------------------------------------------ |
| `data/`      | `'data'`, `'queries'`                      |
| `ui/`        | `'ui'`, `'wizard'`, `'browse'`             |
| `playback/`  | `'playback'`                               |
| Entry points | `'default'`, `'clone'`, `'selector'`       |

### Log Levels

#### ERROR — Operation Failed

Use when an operation cannot complete. Always include `event=` with `.fail` suffix.

```python
log.error("Movie query failed",
          event="query.fail",
          movie_id=movie_id)
```

For exceptions, use `log.exception()` to auto-capture stack trace:

```python
try:
    risky_operation()
except Exception:
    log.exception("Operation failed", event="operation.fail", id=123)
```

#### WARNING — Unexpected but Handled

Use for fallback paths, missing data that's recovered, or unusual conditions.

```python
log.warning("Movie set not found in cache",
            event="results.set_fallback",
            set_id=set_id)
```

#### INFO — Significant Events

Use for lifecycle events and user-visible actions. These appear in Kodi's log.

```python
log.info("EasyMovie launched", event="launch.start")
log.info("Playlist created", event="playlist.create", item_count=10)
```

#### DEBUG — Developer Details

Use freely for troubleshooting. Never appears in Kodi's log.

```python
log.debug("Filtering movies", count=47)
log.debug("Movie matched genre filter", movie_id=123)
```

### Event Naming Convention

Events follow the pattern: `domain.action`

| Domain         | Used For              | Example Events                                         |
| -------------- | --------------------- | ------------------------------------------------------ |
| `launch`       | Addon lifecycle       | `launch.start`, `launch.mode_selected`                 |
| `settings`     | Configuration         | `settings.load`                                        |
| `filter`       | Filter/wizard flow    | `filter.ask`, `filter.preset`, `filter.skip`, `filter.no_results` |
| `query`        | Kodi API queries      | `query.movies`, `query.sets`, `query.fail`             |
| `results`      | Result generation     | `results.generate`, `results.set_substitute`           |
| `playback`     | Movie playback        | `playback.start`, `playback.resume`, `playback.complete` |
| `playlist`     | Playlist ops          | `playlist.create`, `playlist.start`                    |
| `continuation` | Set continuation      | `continuation.prompt`, `continuation.accepted`, `continuation.declined` |
| `history`      | Re-suggestion tracking| `history.save`, `history.prune`                        |
| `ui`           | User interface        | `ui.open`, `ui.select`, `ui.browse`, `ui.surprise`     |
| `clone`        | Clone operations      | `clone.create`, `clone.fail`                           |
| `selector`     | Genre/rating picker   | `selector.open`, `selector.save`                       |

### Timing Operations

Use `log_timing()` for expensive operations:

```python
from resources.lib.utils import get_logger, log_timing

log = get_logger('data')

with log_timing(log, "movie_query"):
    result = json_query(get_all_movies_query())
```

For operations with multiple phases, use the `timer.mark()` method:

```python
with log_timing(log, "generate_results", movie_count=500) as timer:
    filtered = apply_filters(movies, config)
    timer.mark("filtering")

    results = select_and_sort_results(filtered, count=10)
    timer.mark("selection")

# Logs: generate_results completed | duration_ms=150, movie_count=500,
#       filtering_ms=100, selection_ms=50
```

### Module Docstrings

Every module with logging should include a Logging section:

```python
"""
Module description here.

Logging:
    Logger: 'module_name'
    Key events:
        - domain.action (LEVEL): Description
        - domain.other (LEVEL): Description
    See LOGGING.md for full guidelines.
"""
```

### Anti-Patterns to Avoid

- **Don't log sensitive data**
- **Don't use print()** — use `log.debug()` instead
- **Don't forget event= for INFO/WARNING/ERROR**
- **Don't use error() in except blocks** — use `log.exception()` for automatic stack traces
- **Don't log in tight loops without throttling** — log summaries instead

### Log Output Format

#### Kodi Log
```
[EasyMovie.module] message | event=domain.action, key=value, ...
```

#### easymovie.log File
```
2026-03-19 14:45:12.401 [INFO ] [EasyMovie.module] message | event=domain.action, key=value
2026-03-19 14:45:12.402 [DEBUG] [EasyMovie.module] developer details | count=47
```

---

## Troubleshooting

### Log File Not Created

1. Check that debug logging is enabled in settings
2. Verify the addon_data directory exists and is writable
3. Check Kodi's log for initialization errors

### Log File Too Large

The file auto-rotates at 500KB. If you're generating logs faster than expected, check for:
- Tight loops with logging
- Repeated operations that should be batched

### Missing Expected Logs

- **DEBUG** logs only appear when debug logging is enabled
- Check you're looking at the right file (easymovie.log vs kodi.log)
- Verify the logger name matches what you expect

---

*For more information, see the [EasyMovie README](README.md) and source code.*
