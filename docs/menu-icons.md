# Menu Icons

EasyMovie ships a set of white menu icons for your skin's home menu, so EasyMovie and each of its clones can have an icon that looks like it belongs to the same family. Using them is optional: EasyMovie works the same without them.

![All EasyMovie menu icons with their file names](assets/menu-icons.png)

---

## What You Get

Every icon is a film strip with a small badge in the bottom-right corner, so a row of EasyMovie entries reads as one group while each stays recognisable.

| Icon | Suggested use |
|------|---------------|
| `easymovie` | EasyMovie itself (film strip with sparkles) |
| `easymovie-dedicated` | EasyMovie itself, with the sparkles cut out of the film frame instead of a badge |
| `easymovie-lettered` | EasyMovie itself, with the "easy MOVIE" wordmark from the add-on icon cut out of a film strip |
| `easymovie-lettered-outline` | As above, with the wordmark in an open film frame |
| `easymovie-grown-ups` | The plain film strip, with no badge |
| `easymovie-kids` | A clone for children's movies (child's face badge) |
| `easymovie-just-added` | A clone for recently added movies (plus badge) |
| `easymovie-hidden-gems` | A clone for overlooked movies (diamond badge) |
| `easymovie-thriller-night` | A clone for thrillers (eye badge) |
| `easymovie-date-night` | A clone for date-night movies (heart badge) |
| `easymovie-random` | A clone for a random playlist (die badge) |
| `easymovie-bookmark`, `-christmas-tree`, `-crown`, `-ghost`, `-gift`, `-hourglass`, `-moon`, `-paw`, `-smile`, `-trophy`, `-ufo`, `-world` | Spare badges for clones of your own (holiday, comedy, horror, sci-fi, short films, late night, and so on) |
| `random`, `christmas-tree` | A plain die and a plain tree, without the film strip, for other menu entries such as a random movie or a seasonal smart playlist |

The lettered icons show the wordmark clearly from about 40 pixels up. Below that, the text turns into texture, so pick a sparkle icon if your skin shows menu icons small.

---

## Where the Icons Are

The icons are installed with the add-on, in:

```
special://home/addons/script.easymovie/resources/icons/menu/
```

`special://home` is Kodi's own data folder. On disk that is:

| Platform | Folder |
|----------|--------|
| Windows | `%APPDATA%\Kodi\addons\script.easymovie\resources\icons\menu\` |
| Linux | `~/.kodi/addons/script.easymovie/resources/icons/menu/` |
| LibreELEC / CoreELEC | `/storage/.kodi/addons/script.easymovie/resources/icons/menu/` |
| Android | `Android/data/org.xbmc.kodi/files/.kodi/addons/script.easymovie/resources/icons/menu/` |
| macOS | `~/Library/Application Support/Kodi/addons/script.easymovie/resources/icons/menu/` |

Each [clone](clones.md) carries its own copy of the same icons in its own add-on folder (for example `special://home/addons/script.easymovie.kids/resources/icons/menu/`). Pointing every menu entry at the main EasyMovie folder is simplest, because that folder stays in place for as long as EasyMovie is installed. An add-on update replaces the files in it, so do not edit them there; copy an icon elsewhere first if you want to change it.

---

## Using an Icon in Your Menu

1. Open your skin's menu editor from the skin settings (in Arctic Zephyr Mod it is **Customise home menu**; other skins name it differently).
2. Select the EasyMovie or clone menu item.
3. Choose the option to set a custom icon or thumbnail. With Skin Shortcuts, which many skins use for their menus, this opens Kodi's standard image browser.
4. Browse to the folder above and pick the icon.

Every folder in the table above is a hidden folder (`.kodi`, `AppData`, `Library`). If the image browser does not show it, turn on **Settings → Media → General → Show hidden files and directories** first.

### How the Icons Look

The icons are white on a transparent background, the same format skins use for their own menu icons. Skins that tint their icons (with a theme or highlight colour) tint these as well. They are drawn to the same size as the icons in skins such as Arctic Zephyr Mod, so they line up with the skin's own entries.

---

## Troubleshooting

| What you see | Likely cause | Fix |
|--------------|--------------|-----|
| The `.kodi`, `AppData` or `Library` folder does not appear in the image browser | Kodi hides hidden folders by default | Turn on **Settings → Media → General → Show hidden files and directories** |
| The icon disappeared after removing a clone | The menu entry pointed at that clone's own add-on folder, which is removed with the clone | Point the entry at the main EasyMovie folder instead |

---

## Credits

The icons are built from [Tabler Icons](https://tabler.io/icons) (MIT licence); the licence text ships next to them as `LICENSE-tabler-icons.txt`. The wordmark on the lettered icons uses the same fonts as the EasyMovie add-on icon.

---

## Related Pages

- [Clones](clones.md): create the extra EasyMovie entries these icons are designed for
- [Playlist Mode](playlist-mode.md)
