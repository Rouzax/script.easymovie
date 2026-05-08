# Installation

Getting EasyMovie up and running takes just a few minutes.

---

## Requirements

| Requirement | Details |
|-------------|---------|
| **Kodi Version** | Kodi 21 (Omega) or Kodi 22 (Piers) or later |
| **Library** | A movie library with at least a few movies |

> **Not compatible** with Kodi 20 (Nexus) or earlier versions.

---

## Installation Methods

### From GitHub (Recommended)

1. **Download the latest release**
   - Go to [Releases](https://github.com/Rouzax/script.easymovie/releases)
   - Download the `.zip` file (e.g., `script.easymovie-1.0.0.zip`)
   - **Do not extract the zip** — Kodi needs the zip file directly

2. **Install in Kodi**
   - Open Kodi
   - Go to **Settings > Add-ons > Install from zip file**
   - Navigate to your Downloads folder
   - Select the `script.easymovie-x.x.x.zip` file

3. **Enable Unknown Sources (if prompted)**
   - Kodi may ask you to enable "Unknown sources"
   - Go to **Settings > System > Add-ons**
   - Enable **Unknown sources**
   - Return and retry the installation

4. **Confirmation**
   - You'll see a notification: "EasyMovie Add-on installed"

### From Kodi Repository

*(Coming soon — EasyMovie will be submitted to the official Kodi addon repository)*

---

## First Run

When you launch EasyMovie for the first time, it works immediately. There's no background service, no database to build, and no waiting — EasyMovie queries your library live each time.

The **filter wizard** starts right away, walking you through:

1. Watched status — Unwatched, watched, or both?
2. Genres — What are you in the mood for?
3. Age ratings — Filter by MPAA/certification
4. Runtime — How much time do you have?
5. Time period — Recent releases or classics?
6. Score — Set a quality threshold

Each filter can be answered, skipped, or pre-configured in settings. After the wizard, EasyMovie presents your curated selection.

See the [Filter Wizard](filter-wizard.md) page for a detailed walkthrough.

---

## Launching EasyMovie

### From the Add-ons Menu

Navigate to **Add-ons > Program add-ons > EasyMovie**.

### From the Home Screen (Recommended)

Most Kodi skins let you add shortcuts to your home menu. Add EasyMovie to your "Programs" or create a custom menu item for one-click access.

### Via Keyboard / Remote Shortcut

You can map EasyMovie to a button using Kodi's keymap editor or a custom `keymap.xml` file.

---

## Initial Configuration

EasyMovie works out of the box with sensible defaults, but you may want to customize:

### Essential Settings to Consider

| Setting | Location | Why Configure? |
|---------|----------|----------------|
| **When I open EasyMovie** | Settings > EasyMovie | Choose Browse, Playlist, or Ask each time |
| **Theme** | Settings > EasyMovie > Appearance | Pick your preferred accent color |
| **Filter modes** | Settings > Filters | Set each filter to Ask, Pre-set, or Skip |
| **View style** | Settings > Browse Mode | Choose from 5 visual layouts |

### Accessing Settings

**Method 1: From Kodi**
- Navigate to **Add-ons > Program add-ons**
- Highlight EasyMovie (don't click)
- Press `C` on keyboard or `Menu` on remote
- Select **Settings**

**Method 2: From Kodi settings**
- Go to **Settings > Add-ons > Program add-ons > EasyMovie > Configure**

---

## Updating EasyMovie

### Manual Update

1. Download the new version from [Releases](https://github.com/Rouzax/script.easymovie/releases)
2. Install via **Settings > Add-ons > Install from zip file**
3. Kodi will update the existing installation
4. Your settings are preserved

### Clone Updates

If you've created [clones](clones.md), they detect the version change automatically:

1. Launch the clone after updating the main EasyMovie addon
2. EasyMovie detects the version mismatch
3. A prompt asks "Would you like to update the clone now?"
4. Click **Yes** and restart Kodi

---

## Uninstallation

1. Go to **Settings > Add-ons > My add-ons > Program add-ons**
2. Select **EasyMovie**
3. Click **Uninstall**

This removes:
- The addon files

This preserves:
- Your addon data (settings, logs) in `special://profile/addon_data/script.easymovie/`

To fully remove all data, manually delete the `script.easymovie` folder from your addon_data directory.

---

## Next Steps

- **[Filter Wizard](filter-wizard.md)** — Learn how the wizard narrows your library
- **[Browse Mode](browse-mode.md)** — Explore the visual browsing experience
- **[Settings Reference](settings-reference.md)** — Fine-tune every aspect of EasyMovie
