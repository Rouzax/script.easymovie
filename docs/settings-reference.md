# Settings Reference

Complete reference for all EasyMovie settings. Open settings via **Add-ons > EasyMovie > Configure** (or highlight EasyMovie and press `C`).

> **Note:** Some settings only appear when relevant. See the [dependencies summary](#settings-dependencies) at the bottom.

---

## Settings Categories

EasyMovie organizes settings into seven categories:

| Category | Purpose |
|----------|---------|
| **[EasyMovie](#easymovie)** | Launch behavior and appearance |
| **[Filters](#filters)** | What to ask in the wizard |
| **[Movie Sets](#movie-sets)** | Collection awareness and continuation |
| **[Browse Mode](#browse-mode)** | Browse results appearance |
| **[Playlist Mode](#playlist-mode)** | Playlist configuration |
| **[Playback](#playback)** | What happens during/after watching |
| **[Advanced](#advanced)** | Movie pool, re-suggestion, debugging, tools |

---

## EasyMovie

*The fundamental choice: what happens when you launch EasyMovie.*

### On Launch

| Setting | Options | Default | Description |
|---------|---------|---------|-------------|
| **When I open EasyMovie** | Browse / Playlist / Ask each time | Ask each time | Choose what happens when you launch |

### Appearance

| Setting | Options | Default | Description |
|---------|---------|---------|-------------|
| **Theme** | Golden Hour / Ultraviolet / Ember / Nightfall | Golden Hour | Accent color theme for all windows and dialogs |
| **Set custom icon** | (button) | - | Choose a custom addon icon |
| **Reset to default icon** | (button) | - | Restore the original EasyMovie icon |

---

## Filters

*Configure how the wizard handles each filter. Every filter has three modes: Ask (show dialog), Pre-set (use saved values), Skip (ignore).*

### Genre

**Ignore Genres:**

| Setting | Options | Default | Description |
|---------|---------|---------|-------------|
| **Ignore genre filter** | Ask / Pre-set / Skip | Skip | Exclude genres from results |
| **Ignore genre matching** | Any selected (OR) / All selected (AND) | Any (OR) | How to match ignored genres |
| **Select genres to ignore...** | (button) | - | Open genre selector |
| **Ignored genres** | (display) | - | Currently ignored genres |

**Select Genres:**

| Setting | Options | Default | Description |
|---------|---------|---------|-------------|
| **Genre filter** | Ask / Pre-set / Skip | Ask | Include genres in results |
| **Genre matching** | Any selected (OR) / All selected (AND) | Any (OR) | How to match selected genres |
| **Select genres...** | (button) | - | Open genre selector |
| **Selected genres** | (display) | - | Currently selected genres |

### Watched

| Setting | Options | Default | Description |
|---------|---------|---------|-------------|
| **Watched filter** | Ask / Pre-set / Skip | Ask | Filter by watched status |
| **Watched status** | Unwatched / Watched / Both | Unwatched | Pre-set watched filter value |

### Age Rating

| Setting | Options | Default | Description |
|---------|---------|---------|-------------|
| **Age rating filter** | Ask / Pre-set / Skip | Skip | Filter by MPAA/certification |
| **Select ratings...** | (button) | - | Open rating selector |
| **Selected ratings** | (display) | - | Currently selected ratings |

### Runtime

| Setting | Options | Default | Description |
|---------|---------|---------|-------------|
| **Runtime filter** | Ask / Pre-set / Skip | Skip | Filter by movie length |
| **Minimum runtime (minutes)** | 0–300 (step 5) | 0 | Minimum length (0 = no minimum) |
| **Maximum runtime (minutes)** | 0–300 (step 5) | 0 | Maximum length (0 = no maximum) |

### Year

| Setting | Options | Default | Description |
|---------|---------|---------|-------------|
| **Year filter** | Ask / Pre-set / Skip | Skip | Filter by release year |
| **Year filter type** | After year / Before year / Between years / Less than X years ago | After year | How to filter years |
| **From year** | 1920–2030 | 2000 | Starting year |
| **To year** | 1920–2030 | 2026 | Ending year (Between only) |
| **Maximum age (years)** | 1–30 | 5 | Recency filter value |

### Score

| Setting | Options | Default | Description |
|---------|---------|---------|-------------|
| **Score filter** | Ask / Pre-set / Skip | Skip | Filter by rating score |
| **Minimum score** | 0–100 (step 5) | 0 | Minimum score (70 = 7.0 rating) |

---

## Movie Sets

*Control how EasyMovie handles movie collections.*

### Set Awareness

| Setting | Options | Default | Description |
|---------|---------|---------|-------------|
| **Enable movie set awareness** | On / Off | On | Suggest first unwatched set movie |
| **Show set information** | On / Off | On | Display set name and position in browse view |

### Continuation

| Setting | Options | Default | Description |
|---------|---------|---------|-------------|
| **Enable continuation prompts** | On / Off | On | Prompt for next set movie after watching |
| **Countdown duration (seconds)** | 5–60 (step 5) | 20 | Timer before auto-action |
| **If countdown expires** | Continue set / Continue playlist | Continue set | Default action on timeout |

See [Movie Sets](movie-sets.md) for detailed feature documentation.

---

## Browse Mode

*Settings for "Browse" mode - the visual results screen.*

### Appearance

| Setting | Options | Default | Description |
|---------|---------|---------|-------------|
| **View style** | Showcase / Card List / Posters / Big Screen / Split View | Showcase | Visual layout for results |
| **Return to EasyMovie after playback** | On / Off | On | Return to movie list after watching |

### Results

| Setting | Options | Default | Description |
|---------|---------|---------|-------------|
| **Number of movies** | 1–50 | 10 | How many results to show |
| **Sort by** | Random / Title / Year / Rating / Runtime / Date Added | Random | Result ordering |
| **Sort direction** | Ascending / Descending | Descending | Sort order |

---

## Playlist Mode

*Settings for "Playlist" mode - automatic movie marathon generation.*

### Basics

| Setting | Options | Default | Description |
|---------|---------|---------|-------------|
| **Number of movies** | 1–20 | 5 | Playlist length |
| **Sort by** | Random / Title / Year / Rating / Runtime / Date Added | Random | Playlist ordering |
| **Sort direction** | Ascending / Descending | Descending | Sort order |

### Playback

| Setting | Options | Default | Description |
|---------|---------|---------|-------------|
| **Start playlist with unfinished movies** | On / Off | On | Prioritize partially watched movies |
| **Seek to resume point for movies** | On / Off | On | Auto-skip to resume position |

---

## Playback

*Settings that affect what happens during and after watching.*

### On Launch

| Setting | Options | Default | Description |
|---------|---------|---------|-------------|
| **Check for in-progress movie on launch** | On / Off | On | Offer to resume a partially watched movie |

### During Playback

| Setting | Options | Default | Description |
|---------|---------|---------|-------------|
| **Show info when playing** | On / Off | On | Notification when a movie starts |

### Notifications

| Setting | Options | Default | Description |
|---------|---------|---------|-------------|
| **Show processing notifications** | On / Off | On | Progress notifications during search and filtering |

### Warnings

| Setting | Options | Default | Description |
|---------|---------|---------|-------------|
| **Warn about earlier unwatched movies in set** | On / Off | On | Alert for out-of-order set watching |

---

## Advanced

*Technical settings and utilities.*

### Movie Pool

| Setting | Options | Default | Description |
|---------|---------|---------|-------------|
| **Limit to smart playlist** | On / Off | Off | Restrict the movie pool to a Kodi smart playlist |
| **Select playlist...** | (button) | - | Choose a `.xsp` file |
| **Selected playlist** | (display) | - | Currently selected playlist |

### Re-suggestion

| Setting | Options | Default | Description |
|---------|---------|---------|-------------|
| **Avoid re-suggesting recent movies** | On / Off | On | Don't repeat recently suggested movies |
| **Re-suggestion window** | 4h / 8h / 12h / 24h / 48h / 72h | 24 hours | Cooldown period before a movie can appear again |

### Filters

| Setting | Options | Default | Description |
|---------|---------|---------|-------------|
| **Remember last wizard answers** | On / Off | On | Pre-fill wizard dialogs with previous answers |
| **Show movie counts in wizard** | On / Off | On | Display how many movies match each option |
| **Cumulative counts** | On / Off | On | Narrow counts through wizard steps |

### Debugging

| Setting | Options | Default | Description |
|---------|---------|---------|-------------|
| **Enable debug logging** | On / Off | Off | Write diagnostics to a separate log file |

Log location: `special://profile/addon_data/script.easymovie/logs/easymovie.log`

### Tools

| Setting | Options | Default | Description |
|---------|---------|---------|-------------|
| **Create EasyMovie copy...** | (button) | - | Create a clone with separate settings |

---

## Settings Dependencies

Some settings only appear based on other settings:

| Setting | Appears When |
|---------|--------------|
| Ignore genre matching, Select genres to ignore | Ignore genre filter is "Pre-set" |
| Genre matching, Select genres | Genre filter is "Pre-set" |
| Watched status | Watched filter is "Pre-set" |
| Select ratings, Selected ratings | Age rating filter is "Pre-set" |
| Runtime min/max | Runtime filter is "Pre-set" |
| Year filter type, From year, To year, Maximum age | Year filter is "Pre-set" |
| To year | Year filter type is "Between years" |
| Maximum age | Year filter type is "Less than X years ago" |
| Minimum score | Score filter is "Pre-set" |
| Show set information | Set awareness enabled |
| Continuation prompts | Set awareness enabled |
| Countdown duration, If countdown expires | Set awareness + continuation enabled |
| Select playlist, Selected playlist | Limit to smart playlist enabled |
| Re-suggestion window | Avoid re-suggesting enabled |
| Cumulative counts | Show movie counts enabled |

---

## Related Pages

- **[Filter Wizard](filter-wizard.md)** - How filter settings affect the wizard
- **[Browse Mode](browse-mode.md)** - How browse settings work in practice
- **[Playlist Mode](playlist-mode.md)** - How playlist settings work in practice
- **[Movie Sets](movie-sets.md)** - How set settings work
- **[Advanced Features](advanced-features.md)** - Clone and debugging details
- **[Troubleshooting](troubleshooting-and-faq.md)** - Debug logging explained
