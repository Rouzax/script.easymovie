# Kodi Development Patterns & Gotchas

Quick reference for Kodi addon development patterns used in EasyMovie.

## Window Properties

Kodi addons use window properties on the Home window (10000) for data sharing:

```python
import xbmcgui

home = xbmcgui.Window(10000)

# Write
home.setProperty('EasyMovie.Accent', 'FFF5A623')

# Read
accent = home.getProperty('EasyMovie.Accent')

# Clear
home.clearProperty('EasyMovie.Accent')
```

Properties are ephemeral (cleared on Kodi restart) and string-only. Prefix with `EasyMovie.` to avoid collisions.

**Movie ID Instability:** Kodi reassigns movie IDs during library rebuilds (clean + scan). Never persist movie IDs as permanent identifiers without validation.

## Settings Dialog Behavior

### Cache Issue

Kodi's settings dialog caches values in memory. If you programmatically call `setSetting()` while the dialog is closed, then the user manually reopens it, they may see stale values.

**Workaround:** For action buttons that modify settings:
1. Action script writes result to a window property
2. On next launch, check the property and call `setSetting()`

### Action Buttons

Settings XML supports `<close>true</close>` to close the dialog when an action fires:
```xml
<setting id="run_selector" type="action" label="32100">
    <level>0</level>
    <default />
    <constraints>
        <options>RunScript(script.easymovie,selector,genres)</options>
    </constraints>
    <close>true</close>
</setting>
```

## JSON-RPC Query Patterns

### Query Builder Pattern

All queries go through centralized builders in `data/queries.py`:

```python
from resources.lib.utils import json_query

query = {
    "jsonrpc": "2.0",
    "method": "VideoLibrary.GetMovies",
    "params": {
        "properties": ["title", "genre", "year", "rating"],
        "sort": {"method": "title"}
    },
    "id": 1
}

result = json_query(query)
```

### Server-Side Random

Use Kodi's built-in random sorting instead of client-side shuffle:
```python
"sort": {"method": "random"}
```
No performance penalty vs sequential ordering.

## Addon Lifecycle

### Script Invocations

Scripts launched via `RunScript()` run in their own Python interpreter instance. They share no state with other scripts except through window properties and the filesystem.

EasyMovie has no background service — it runs only when invoked.

## Multi-Instance (Clones)

EasyMovie supports clone instances for specialized configurations (e.g., "Kids Movies" with pre-set filters). Clone addon IDs follow the pattern `script.easymovie.clone_name`.

## Kodi API Stubs

For development, install Kodistubs for autocomplete and type checking:
```bash
pip install Kodistubs
```

This provides type stubs for `xbmc`, `xbmcgui`, `xbmcplugin`, `xbmcaddon`, `xbmcvfs`, and `xbmcdrm`.
