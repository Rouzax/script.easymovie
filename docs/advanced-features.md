# Advanced Features

EasyMovie includes several features for power users: movie pool filtering, smart re-suggestion, and debug logging. For creating multiple addon instances, see [Clones](clones.md).

---

## Movie Pool

Limit the movies EasyMovie draws from to a Kodi smart playlist. This lets you create themed movie nights, family-friendly pools, or seasonal collections.

### Setting Up a Movie Pool

1. Create a smart playlist in Kodi (`.xsp` file with `type="movies"`)
2. Go to **Settings > Advanced > Movie Pool**
3. Enable **Limit to smart playlist**
4. Click **Select playlist...**
5. Choose your `.xsp` file

### Use Cases

| Movie Pool | Smart Playlist Rule |
|------------|-------------------|
| Family night | Rating is "G" or "PG" |
| Holiday movies | Genre is "Holiday" |
| Sci-fi collection | Genre is "Science Fiction" |
| High-quality only | Rating > 7.0 |
| Recent additions | Date added in the last 30 days |

The wizard filters stack on top of the movie pool. So if your pool is "Family movies" and you filter by "Comedy" in the wizard, you get family comedies.

---

## Smart Re-suggestion

EasyMovie tracks which movies it has recently suggested to avoid showing the same titles repeatedly.

### How It Works

When a movie appears in your results, EasyMovie records the timestamp. That movie won't appear again until the re-suggestion window expires.

| Setting | Description |
|---------|-------------|
| **Avoid re-suggesting recent movies** | Enable/disable the feature |
| **Re-suggestion window** | How long to wait: 4, 8, 12, 24, 48, or 72 hours |

**Default:** Enabled with a 24-hour window.

### Tips

- Re-roll multiple times and the system prevents repeats
- Works across sessions - close and reopen EasyMovie and it still remembers
- If your library is small, a shorter window prevents running out of movies
- Disable entirely if you don't mind seeing repeat suggestions

---

## Debug Logging

For troubleshooting issues, EasyMovie can write detailed logs to a separate file (not Kodi's main log).

### Enabling Debug Logging

1. Go to **Settings > Advanced > Debugging**
2. Enable **Enable debug logging**

### Log Location

| Platform | Path |
|----------|------|
| **Windows** | `%APPDATA%\Kodi\userdata\addon_data\script.easymovie\logs\easymovie.log` |
| **Linux** | `~/.kodi/userdata/addon_data/script.easymovie/logs/easymovie.log` |
| **macOS** | `~/Library/Application Support/Kodi/userdata/addon_data/script.easymovie/logs/easymovie.log` |
| **LibreELEC** | `/storage/.kodi/userdata/addon_data/script.easymovie/logs/easymovie.log` |
| **OSMC** | `/home/osmc/.kodi/userdata/addon_data/script.easymovie/logs/easymovie.log` |

### What Gets Logged

| Level | Content | Always Logged |
|-------|---------|---------------|
| **ERROR** | Operation failures, exceptions | Yes (Kodi + EasyMovie log) |
| **WARNING** | Recoverable issues | Yes (Kodi + EasyMovie log) |
| **INFO** | Lifecycle events (start, stop) | Yes (Kodi + EasyMovie log) |
| **DEBUG** | Detailed diagnostics | Only when debug enabled (EasyMovie log only) |

### Log Format

```
2026-03-24 20:15:30.123 [EasyMovie.ui] INFO: Addon launched, version=1.0.0
2026-03-24 20:15:31.456 [EasyMovie.data] DEBUG: Fetching movies, total=247
2026-03-24 20:15:32.789 [EasyMovie.data] DEBUG: Filtered to 42 movies
```

---

## Keyboard Shortcuts

| Key | Context | Action |
|-----|---------|--------|
| **Enter** | Browse Mode | Play selected movie |
| **C** / **Menu** | Browse Mode | Context menu |
| **T** / **Blue button** | Browse Mode | Cycle theme preview |
| **Backspace** / **Esc** | Browse Mode | Close EasyMovie |
| **Arrow keys** | Browse Mode | Navigate results |

---

## Related Pages

- **[Installation](installation.md)** - Initial setup
- **[Settings Reference](settings-reference.md)** - All settings explained
- **[Troubleshooting](troubleshooting-and-faq.md)** - Common issues
