# UI Refinement Design: Heading Standardization, Descender Padding, and View Fixes

**Date:** 2026-03-23
**Status:** Approved

## Overview

Comprehensive UI refinement pass across all EasyMovie browse views and dialogs. Three categories of changes:

1. **Heading standardization** — consistent header/accent line positioning across all views
2. **Descender padding** — fix text overlap where letters like g, y, p collide with the next line
3. **Per-view fixes** — poster clipping, fanart strip removal, context menu sizing, collection space collapse

## Design Rule: Descender Padding

Minimum **4px visual gap** between stacked labels. Calculated using effective text bounds (accounting for font centering within label height):

```
eff_bottom = top + (height + font_px) / 2
eff_top    = top + (height - font_px) / 2
gap        = next_eff_top - prev_eff_bottom
```

Font reference sizes: font10 ~21px, font12 ~24px, font13 ~30px, font14_title ~32px.

## 1. Standardized Heading Area

### Dialog-style (13/66/82)

Already correct in Confirm, Select, Selector, Continuation, Set Warning, and Card List. Only Split View is the outlier.

| Element          | Value | Notes                        |
|------------------|-------|------------------------------|
| Heading top      | 13    |                              |
| Heading height   | 40    | font14_title                 |
| Count top        | 18    | font10, right-aligned        |
| Accent line top  | 66    |                              |
| Content top      | 82    |                              |
| Side padding     | 30    |                              |
| Accent width     | dialog_width - 60 |                   |

### Full-screen (15/60/72)

New standard for Poster Wall, Posters, and Big Screen.

| Element          | Value | Notes                        |
|------------------|-------|------------------------------|
| Heading top      | 15    |                              |
| Heading height   | 40    | font14_title                 |
| Count top        | 20    | font10, right-aligned        |
| Accent line top  | 60    |                              |
| Content top      | 72    |                              |
| Side padding     | 40    | Big Screen: 80               |
| Accent width     | full usable width |                   |

## 2. Changes by File

### script-easymovie-cardlist.xml (Card List)

**Heading:** Already at 13/66/82. No change.

**Remove fanart strip:** Delete the fanart image (top=72, 1340x100), dark scrim, and info bar (genre/set label). These are visually meaningless and redundant with row data.

**Layout after removal:**
- List starts at top=82 (was 178)
- List height: 648px (buttons move to 730)
- 648 / 78px rows = **8 rows visible** (was 6)

**Row padding:** No changes needed. Title→metadata visual gap = 7.5px (above 4px minimum).

### script-easymovie-splitlist.xml (Split View)

**Heading fix:** Align to dialog standard.
- Accent line: 46 (in group) → 53 (absolute 66)
- Count top: 8 (in group) → 5 (absolute 18)
- Move accent line outside left panel group to span full dialog width (1340px)

**Left panel rows:** Fix descender overlap (current gap = 1.5px).
- Metadata top: 32 → 38 (gap becomes 7.5px)
- Row height: 64 → **68**
- List at top=82, buttons at 740 → height 658 / 68 = **9 rows** (was 10)

**Right panel detail:** No changes needed (all gaps >= 11px).

### script-easymovie-postergrid.xml (Poster Wall)

**Heading:** Standardize to 15/60/72.
- Heading top: 10 → 15
- Accent line top: 48 → 60
- Panel top: 56 → 72
- Left margin: 35 → 40, width: 1850 → 1840

**Poster cell padding:** Add 5px internal left padding so focus border (-3px) stays within panel bounds.
- Poster image: left=0 → left=5, width=300 → 290, height=450 → 435
- Focus border: left=-3 → left=2, width=306 → 296, height=456 → 441
- Corresponding changes to watched/set badge positions

**Overlay descender fix:** (current title→metadata gap = 1.5px)
- Title: 948 (unchanged)
- Metadata: 978 → 984 (gap becomes 7.5px)
- Genre: 1002 → 1012 (gap becomes 7px)

**Plot autoscroll:** Add `<autoscroll delay="6000" time="3000" repeat="10000">true</autoscroll>` to plot textbox (currently missing).

### script-easymovie-main.xml (Posters View)

**Heading:** Standardize to 15/60/72.
- Heading top: 15 (already correct)
- Count top: 20 (already correct)
- Accent line top: 52 → 60
- Content (info panel group) top: 65 → 72

**Accent line full width:** 1140 → 1840 (spans both info panel and poster grid).
**Movie count full width:** 1140 → 1840 (right-aligns across full screen).

**Collection space collapse:** When no set_name, collapse the 25px set label space:
- Separator A at top=490 with `<visible>` for no-set (directly after genre)
- Separator B at top=515 with `<visible>` for set-present (after set label)
- Plot A at top=502 (no-set)
- Plot B at top=527 (set-present)

**Info panel padding:** No changes needed (all gaps >= 7px with generous label heights).

### script-easymovie-BigScreenList.xml (Big Screen)

**Heading:** Standardize to 15/60/72.
- Heading top: 20 → 15
- Count top: 25 → 20
- Accent line top: 62 → 60
- Content group top: 75 → 72

**Focused row descender fix:** (metadata→genre gap = 3.5px, genre→set gap = 1px)
- Genre top: 68 → 73 (gap becomes 8.5px)
- Set top: 90 → 100 (gap becomes 6px)
- Row height: 120 → **125**

**Unfocused rows:** No change needed (7px gap, stays at 90px).

~10 items still visible in fixedlist (unchanged).

### script-easymovie-contextwindow.xml (Context Menu)

**Resize:** 380x340 → **480x170** (only 2 buttons, current size is massively oversized).
- Re-center on screen: left = (1920-480)/2 = 720, top = (1080-170)/2 = 455
- Button width: 340 → 420
- Grouplist: adjust left/top/width/height for new dimensions
- Border frame: adjust to 484x174

**"Play Full Set" label:** Remove collection name from button text (Python code change). Just show the localized "Play Full Set" string.

### Python: Context menu label change

Remove the collection name from the "Play Full Set" button label. The button currently appends the set name in parentheses which causes scrolling on long names. Just use the base localized string.

### skin-guidelines.md

Add the descender padding rule (formula + font reference sizes) and the two heading area standards (dialog 13/66/82, full-screen 15/60/72) to the guidelines document.

## 3. Files Not Changed

| File | Reason |
|------|--------|
| script-easymovie-continuation.xml | Already at 13/66/82, no descender issues |
| script-easymovie-setwarning.xml | Already at 13/66/82, no descender issues |
| script-easymovie-confirm.xml | Already at 13/66/82, no descender issues |
| script-easymovie-select.xml | Already at 13/66/82, no descender issues |
| script-easymovie-selector.xml | Already at 13/66/82, no descender issues |

## 4. Content Capacity Summary

| View | Before | After | Delta |
|------|--------|-------|-------|
| Card List | 6 rows | 8 rows | +2 (fanart strip removed) |
| Split View | 10 rows | 9 rows | -1 (row height 64→68 + heading fix) |
| Big Screen | ~10 items | ~10 items | No change |
| Poster Wall | ~1.8 row grid | ~1.8 row grid | No change (poster cells slightly smaller) |
| Posters | Same | Same | -7px negligible |

## 5. Implementation Order

1. Update skin-guidelines.md with new rules
2. Heading standardization (all 4 views that need it)
3. Descender padding fixes (Split View rows, Big Screen focused rows, Poster Wall overlay)
4. Poster Wall: cell padding + plot autoscroll
5. Card List: remove fanart strip, adjust list position
6. Posters: accent line full width + collection collapse
7. Context Menu: resize + Python label change
8. Visual verification on Kodi test instance
