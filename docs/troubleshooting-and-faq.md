# Troubleshooting & FAQ

Common issues, solutions, and frequently asked questions about EasyMovie.

---

## Common Issues

### No Movies Found

The wizard finishes but EasyMovie says no movies match.

**Possible causes and solutions:**

| Cause | Solution |
|-------|----------|
| Filters too restrictive | Try with fewer filters — set most to "Skip" and test |
| Empty library | Ensure you have movies scanned into Kodi's library |
| Movie pool playlist empty | Disable "Limit to smart playlist" or check playlist rules |
| All movies recently suggested | Reduce the re-suggestion window or disable it temporarily |
| Genre selection too narrow | Try "Any (OR)" matching instead of "All (AND)" |

**Quick test:** Set all filters to "Skip" in Settings > Filters. If movies appear now, one of your filters was too restrictive.

---

### Same Movies Keep Appearing

You see the same suggestions every time.

**Solutions:**
1. Enable **Avoid re-suggesting recent movies** in Settings > Advanced > Re-suggestion
2. Increase the **Re-suggestion window** (try 24 or 48 hours)
3. Try **Re-roll** to get fresh suggestions
4. Check if your filters are narrowing to a very small pool

---

### Set Continuation Not Working

After finishing a collection movie, no prompt appears.

**Check these settings:**

| Setting | Required Value |
|---------|---------------|
| Enable movie set awareness | On |
| Enable continuation prompts | On |

**Also verify:**
- The movie is actually part of a Kodi movie set (check in Kodi's library)
- There's at least one more unwatched movie in the collection
- You watched past Kodi's "minimum percentage watched" threshold (default 90%)

---

### Wrong Movie Suggested for Set

EasyMovie suggests the wrong "next" movie in a collection.

**Possible causes:**

| Cause | Solution |
|-------|----------|
| Set ordering incorrect in Kodi | Check movie set ordering in your library metadata |
| Watch status incorrect | Manually fix watched/unwatched status in Kodi's library |
| Duplicate movies in library | Remove duplicates |

---

### Clone Won't Update

After updating EasyMovie, a clone still shows old behavior.

**Solution:**
1. Launch the clone
2. Accept the update prompt when it appears
3. Restart Kodi when prompted

**If no prompt appears:**
- The clone may already be up to date
- Try uninstalling and recreating the clone

---

### Slow Wizard Performance

The filter wizard feels sluggish.

**Solutions:**
1. Disable **Cumulative counts** in Settings > Advanced > Filters — this reduces database queries per wizard step
2. Disable **Show movie counts in wizard** entirely for the fastest experience
3. On low-power devices, fewer filter steps (set more to "Skip") helps

---

### Movies Not Marking as Watched

Movies you watch through EasyMovie don't update their status.

**Check Kodi settings:**
1. Go to **Settings > Player > Videos**
2. Find "Minimum percentage watched" (default 90%)
3. Ensure you're watching past this threshold

**Note:** This is a Kodi setting, not an EasyMovie setting. EasyMovie uses normal Kodi playback, so watch status is handled by Kodi.

---

## Debug Logging

For diagnosing complex issues, enable detailed logging.

### Enabling Logs

1. Go to **Settings > Advanced > Debugging**
2. Enable **Enable debug logging**
3. Reproduce the issue
4. Check the log file

### Log File Locations

| Platform | Path |
|----------|------|
| **Windows** | `%APPDATA%\Kodi\userdata\addon_data\script.easymovie\logs\easymovie.log` |
| **Linux** | `~/.kodi/userdata/addon_data/script.easymovie/logs/easymovie.log` |
| **macOS** | `~/Library/Application Support/Kodi/userdata/addon_data/script.easymovie/logs/easymovie.log` |
| **LibreELEC** | `/storage/.kodi/userdata/addon_data/script.easymovie/logs/easymovie.log` |
| **OSMC** | `/home/osmc/.kodi/userdata/addon_data/script.easymovie/logs/easymovie.log` |

### What to Look For

- **ERROR** entries indicate failures
- **WARNING** entries indicate recoverable issues
- Timestamps help correlate with when problems occurred
- Module names (data, ui, playback) indicate where issues happen

### Reporting Bugs

When reporting issues, include:
1. EasyMovie version (from addon info)
2. Kodi version (from System > System info)
3. What you were trying to do
4. What happened instead
5. Relevant log entries

---

## Frequently Asked Questions

### General

**Q: Does EasyMovie work with Kodi 20?**
A: No. EasyMovie requires Kodi 21 (Omega) or later.

**Q: Does EasyMovie modify my library?**
A: No. EasyMovie only reads from your library. It never modifies movies, sets, or watch status except through normal Kodi playback.

**Q: Can I use EasyMovie with multiple profiles?**
A: Yes. Each Kodi profile has separate EasyMovie settings and data.

**Q: Does EasyMovie work with streaming addons?**
A: Partially. EasyMovie works with movies in your Kodi library. Streaming addons that don't add content to the library won't be visible to EasyMovie.

**Q: Does EasyMovie need a background service?**
A: No. Unlike EasyTV, EasyMovie queries your library live each time you launch it. There's no background processing or startup delay.

---

### Filters

**Q: How does genre AND/OR matching work?**
A: With OR (default), selecting "Action" and "Comedy" returns movies with *either* genre. With AND, only movies tagged with *both* genres appear.

**Q: Can I save filter presets?**
A: Yes. Set any filter to "Pre-set" mode in settings, then configure the values. The wizard will use those values silently without showing a dialog.

**Q: Can I skip all filters?**
A: Yes. Set every filter to "Skip" and EasyMovie will show random movies from your entire library (or movie pool, if configured).

**Q: What if I change my mind mid-wizard?**
A: Press Back to return to the previous step. Press Cancel/Esc to exit the wizard entirely.

---

### Movie Sets

**Q: What counts as a movie set?**
A: Kodi's built-in movie sets (collections). These are typically created automatically by scrapers like TMDb or manually by you.

**Q: Does it work with custom sets?**
A: Yes. Any movie set recognized by Kodi works with EasyMovie's set awareness.

**Q: What if I don't have all movies in a set?**
A: EasyMovie works with what's available. If you have movies 1 and 3 but not 2, it suggests movie 3 after you watch movie 1.

**Q: Can I disable set features for specific sets?**
A: No. Set awareness is a global setting. It's either on or off for all collections.

---

### Browse Mode

**Q: Can I change the view style?**
A: Yes. Five styles are available: Showcase, Card List, Posters, Big Screen, and Split View. Change in Settings > Browse Mode.

**Q: Can I change the number of results?**
A: Yes. Configure 1–50 movies in Settings > Browse Mode > Results.

**Q: What does "Re-roll" do exactly?**
A: It generates a completely new random selection using the same filter criteria. The re-suggestion system ensures you don't see the same movies again.

**Q: What does "Surprise Me" do?**
A: It picks one random movie from the current results and starts playing immediately.

---

### Technical

**Q: How much storage does EasyMovie use?**
A: Minimal. The settings file and re-suggestion data are typically under 1MB combined.

**Q: Can I backup my EasyMovie settings?**
A: Yes. Copy the `addon_data/script.easymovie/` folder from your Kodi userdata directory.

**Q: Does EasyMovie cache anything?**
A: Only the re-suggestion history (which movies were recently shown) and your last wizard answers. All movie data is queried fresh from Kodi's library each time.

---

## Getting Help

### Resources

| Resource | Link |
|----------|------|
| **GitHub Issues** | [Report a bug](https://github.com/Rouzax/script.easymovie/issues) |
| **Kodi Forum** | [EasyMovie Thread](https://forum.kodi.tv/showthread.php?tid=385063) |
| **Wiki** | You're here! |

### When Asking for Help

Include:
1. EasyMovie version (from addon info)
2. Kodi version (from System > System info)
3. What you're trying to do
4. What's happening instead
5. Your relevant settings
6. Log excerpts (if applicable)

---

## Related Pages

- **[Installation](installation.md)** — Initial setup
- **[Settings Reference](settings-reference.md)** — All settings explained
- **[Advanced Features](advanced-features.md)** — Debug logging details
- **[Filter Wizard](filter-wizard.md)** — Filter troubleshooting
