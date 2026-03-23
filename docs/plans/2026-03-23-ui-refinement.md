# UI Refinement Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Standardize heading positioning, fix descender padding, and resolve per-view layout issues across all EasyMovie browse views and the context menu.

**Architecture:** Pure layout changes in Kodi skin XML files (pixel positioning, sizing, visibility conditions) plus one 2-line Python change. No logic changes, no new controls, no new files. Design doc: `docs/plans/2026-03-23-ui-refinement-design.md`.

**Tech Stack:** Kodi WindowXMLDialog XML (1080i resolution), Python 3.8+

---

### Task 1: Update skin-guidelines.md with new rules

**Files:**
- Modify: `.claude/skin-guidelines.md`

**Step 1: Add descender padding rule**

After the "## Typography" section's "### Usage Rules", add a new subsection:

```markdown
### Descender Padding Rule

Stacked labels must maintain a minimum **4px visual gap** to prevent descender overlap (letters like g, y, p). Calculate effective text bounds accounting for font centering:

```
eff_bottom = top + (height + font_px) / 2
eff_top    = top + (height - font_px) / 2
gap        = next_eff_top - prev_eff_bottom    (must be >= 4px)
```

Font reference sizes: font10 ~21px, font12 ~24px, font13 ~30px, font14_title ~32px.
```

**Step 2: Add heading area standards**

In the "## Dialog Heading Area" section, add a note that this applies to dialog-style views. Then add a new section after it:

```markdown
## Full-Screen Heading Area

Full-screen browse views (Poster Wall, Posters, Big Screen) use a separate standard:

| Property       | Value | Notes                            |
|----------------|-------|----------------------------------|
| Heading top    | 15    |                                  |
| Heading height | 40    | Room for font14_title            |
| Count top      | 20    | font10, right-aligned            |
| Accent line top| 60    | 5px below heading bottom         |
| Content top    | 72    | 10px below line                  |
| Side padding   | 40    | Big Screen uses 80 for cinematic feel |
| Accent width   | full usable width |                   |
```

**Step 3: Commit**

```bash
git add .claude/skin-guidelines.md
git commit -m "docs: add descender padding rule and full-screen heading standard to skin guidelines"
```

---

### Task 2: Standardize Poster Wall heading + fix overlay padding + poster cell padding

**Files:**
- Modify: `resources/skins/Default/1080i/script-easymovie-postergrid.xml`

**Step 1: Heading area (15/60/72)**

| Element | Old | New |
|---------|-----|-----|
| Heading label top | 10 | 15 |
| Heading label left | 35 | 40 |
| Movie count left | 35 | 40 |
| Movie count top | 18 | 20 |
| Movie count width | 1400 | 1840 |
| Accent line left | 35 | 40 |
| Accent line top | 48 | 60 |
| Accent line width | 1850 | 1840 |
| Panel left | 35 | 40 |
| Panel top | 56 | 72 |
| Panel width | 1850 | 1840 |

Heading label width: keep 800 (plenty for addon name).
Button positions: Surprise Me left stays at 1475, Re-roll at 1685, both top 5→10 to better align with heading.

**Step 2: Poster cell padding (fix left-edge focus border clipping)**

In both `itemlayout` and `focusedlayout` (width=300, height=460 unchanged):

**itemlayout changes:**
- Poster image: left=0→5, width=300→290, height=450→435, top=5→13
- Watched scrim: left=0→5, top=5→13
- Watched icon: left=4→9, top=9→17
- Set scrim: left=220→215, top=5→13
- Set badge: left=256→251, top=9→17

**focusedlayout changes:**
- Accent border: left=-3→2, top=2→10, width=306→296, height=456→441
- Poster image: left=0→5, width=300→290, height=450→435, top=5→13
- Watched scrim: left=0→5, top=5→13
- Watched icon: left=4→9, top=9→17
- Set scrim: left=220→215, top=5→13
- Set badge: left=256→251, top=9→17

**Step 3: Overlay descender fix**

| Label | Old top | New top |
|-------|---------|---------|
| Title (font13) | 948 | 948 |
| Metadata with MPAA | 978 | 984 |
| Metadata no MPAA | 978 | 984 |
| Genre (no set) | 1002 | 1012 |
| Genre (with set) | 1002 | 1012 |

**Step 4: Add plot autoscroll**

The plot textbox (left=980, top=952) is missing autoscroll. Add:
```xml
<autoscroll delay="6000" time="3000" repeat="10000">true</autoscroll>
```

**Step 5: Verify syntax**

```bash
python3 -c "from xml.etree import ElementTree; ElementTree.parse('resources/skins/Default/1080i/script-easymovie-postergrid.xml'); print('OK')"
```

**Step 6: Commit**

```bash
git add resources/skins/Default/1080i/script-easymovie-postergrid.xml
git commit -m "fix(skin): poster wall heading, cell padding, overlay spacing, plot autoscroll"
```

---

### Task 3: Standardize Posters View heading + accent width + collection collapse

**Files:**
- Modify: `resources/skins/Default/1080i/script-easymovie-main.xml`

**Step 1: Heading area (15/60/72) — partial, some already correct**

| Element | Old | New |
|---------|-----|-----|
| Heading top | 15 | 15 (no change) |
| Count top | 20 | 20 (no change) |
| Accent line top | 52 | 60 |
| Accent line width | 1140 | 1840 |
| Count label width | 1140 | 1840 |
| Info panel group top | 65 | 72 |

**Step 2: Collection space collapse**

Replace the single separator at top=515 and single plot at top=527 with conditional pairs:

```xml
<!-- Separator: after genre when NO collection -->
<control type="image">
    <left>0</left>
    <top>490</top>
    <width>620</width>
    <height>2</height>
    <texture colordiffuse="$INFO[Window.Property(EasyMovie.AccentGlow)]">common/line_fade.png</texture>
    <visible>String.IsEmpty(Container(655).ListItem.Property(set_name))</visible>
</control>

<!-- Separator: after set info when collection present -->
<control type="image">
    <left>0</left>
    <top>515</top>
    <width>620</width>
    <height>2</height>
    <texture colordiffuse="$INFO[Window.Property(EasyMovie.AccentGlow)]">common/line_fade.png</texture>
    <visible>!String.IsEmpty(Container(655).ListItem.Property(set_name))</visible>
</control>

<!-- Plot: positioned after separator (no collection) -->
<control type="textbox">
    <left>0</left>
    <top>502</top>
    <width>620</width>
    <height>395</height>
    <font>font12</font>
    <textcolor>FFAAAAAA</textcolor>
    <autoscroll delay="6000" time="3000" repeat="10000">true</autoscroll>
    <label>$INFO[Container(655).ListItem.Plot]</label>
    <visible>String.IsEmpty(Container(655).ListItem.Property(set_name))</visible>
</control>

<!-- Plot: positioned after separator (with collection) -->
<control type="textbox">
    <left>0</left>
    <top>527</top>
    <width>620</width>
    <height>370</height>
    <font>font12</font>
    <textcolor>FFAAAAAA</textcolor>
    <autoscroll delay="6000" time="3000" repeat="10000">true</autoscroll>
    <label>$INFO[Container(655).ListItem.Plot]</label>
    <visible>!String.IsEmpty(Container(655).ListItem.Property(set_name))</visible>
</control>
```

**Step 3: Verify syntax**

```bash
python3 -c "from xml.etree import ElementTree; ElementTree.parse('resources/skins/Default/1080i/script-easymovie-main.xml'); print('OK')"
```

**Step 4: Commit**

```bash
git add resources/skins/Default/1080i/script-easymovie-main.xml
git commit -m "fix(skin): posters view heading, full-width accent, collection space collapse"
```

---

### Task 4: Standardize Big Screen heading + fix focused row descenders

**Files:**
- Modify: `resources/skins/Default/1080i/script-easymovie-BigScreenList.xml`

**Step 1: Heading area (15/60/72)**

| Element | Old | New |
|---------|-----|-----|
| Heading top | 20 | 15 |
| Heading left | 80 | 80 (keep wider margin) |
| Count top | 25 | 20 |
| Accent line top | 62 | 60 |
| Content group top | 75 | 72 |

**Step 2: Focused row descender fix (120→125)**

In `focusedlayout`: change `height="120"` to `height="125"`.

Inside focusedlayout:
- AccentBG image height: 120→125
- Genre label top: 68→73
- Set label top: 90→100

All other positions (title 10, poster 5, metadata 42, icons 13) stay the same.

**Step 3: Verify syntax**

```bash
python3 -c "from xml.etree import ElementTree; ElementTree.parse('resources/skins/Default/1080i/script-easymovie-BigScreenList.xml'); print('OK')"
```

**Step 4: Commit**

```bash
git add resources/skins/Default/1080i/script-easymovie-BigScreenList.xml
git commit -m "fix(skin): big screen heading standardization and focused row descender spacing"
```

---

### Task 5: Fix Split View heading + row descenders + full-width accent

**Files:**
- Modify: `resources/skins/Default/1080i/script-easymovie-splitlist.xml`

**Step 1: Heading fix to dialog standard (13/66/82)**

The left panel heading group is at `<top>13</top>`. Inside it:

| Element | Old (relative to group) | New |
|---------|------------------------|-----|
| Count top | 8 | 5 |
| Accent line top | 46 | — (move outside group) |

Move the accent line OUT of the left panel heading group, placing it as a sibling in the visible content group:

```xml
<!-- Full-width accent line separator (spans both panels) -->
<control type="image">
    <left>30</left>
    <top>66</top>
    <width>1340</width>
    <height>2</height>
    <texture colordiffuse="$INFO[Window.Property(EasyMovie.AccentGlow)]">common/line_fade.png</texture>
</control>
```

Delete the accent line from inside the left panel group.

**Step 2: List position**

| Element | Old | New |
|---------|-----|-----|
| List top | 71 | 82 |
| List height | 640 | 648 |

**Step 3: Row descender fix (64→68)**

In both `itemlayout` and `focusedlayout`: change `height="64"` to `height="68"`.

Inside both layouts:
- Metadata labels (Year/MPAA/Runtime): top 32→38
- All other positions stay the same

In focusedlayout only:
- AccentBG image height: 64→68

**Step 4: Button row position**

Move buttons down to reclaim space:
- Button group top: 730→740

**Step 5: Verify syntax**

```bash
python3 -c "from xml.etree import ElementTree; ElementTree.parse('resources/skins/Default/1080i/script-easymovie-splitlist.xml'); print('OK')"
```

**Step 6: Commit**

```bash
git add resources/skins/Default/1080i/script-easymovie-splitlist.xml
git commit -m "fix(skin): split view heading standardization, full-width accent, row descender spacing"
```

---

### Task 6: Card List — remove fanart strip + adjust layout

**Files:**
- Modify: `resources/skins/Default/1080i/script-easymovie-cardlist.xml`

**Step 1: Remove fanart strip**

Delete these controls (lines 98-127):
- Fanart image (left=30, top=72, 1340x100)
- Dark scrim (left=30, top=132, 1340x46)
- Info bar label (left=30, top=148, genre/set)

**Step 2: Adjust list and button positions**

| Element | Old | New |
|---------|-----|-----|
| List top | 178 | 82 |
| List height | 502 | 638 |
| Button group top | 700 | 730 |
| Button group left | 415 | 415 (no change) |

**Step 3: Verify syntax**

```bash
python3 -c "from xml.etree import ElementTree; ElementTree.parse('resources/skins/Default/1080i/script-easymovie-cardlist.xml'); print('OK')"
```

**Step 4: Commit**

```bash
git add resources/skins/Default/1080i/script-easymovie-cardlist.xml
git commit -m "fix(skin): remove card list fanart strip, reclaim list space"
```

---

### Task 7: Context menu — resize + Python label fix

**Files:**
- Modify: `resources/skins/Default/1080i/script-easymovie-contextwindow.xml`
- Modify: `resources/lib/ui/context_menu.py:62-64`

**Step 1: Resize context menu XML**

Container group position and size:

| Property | Old | New |
|----------|-----|-----|
| left | 770 | 720 |
| top | 370 | 455 |
| width | 380 | 480 |
| height | 340 | 170 |

Accent border frame:

| Property | Old | New |
|----------|-----|-----|
| width | 384 | 484 |
| height | 344 | 174 |

Menu background:

| Property | Old | New |
|----------|-----|-----|
| width | 380 | 480 |
| height | 340 | 170 |

Grouplist (id=100):

| Property | Old | New |
|----------|-----|-----|
| left | 20 | 30 |
| top | 25 | 25 |
| width | 340 | 420 |
| height | 290 | 120 |

Both buttons:

| Property | Old | New |
|----------|-----|-----|
| width | 340 | 420 |

**Step 2: Python — remove collection name from label**

In `resources/lib/ui/context_menu.py`, delete lines 63-64:

```python
        if self._set_name:
            set_label = f"{set_label} ({self._set_name})"
```

The `_set_name` attribute is still used for `_has_set` logic and logging, so keep it. Only the label formatting changes.

**Step 3: Verify**

```bash
python3 -c "from xml.etree import ElementTree; ElementTree.parse('resources/skins/Default/1080i/script-easymovie-contextwindow.xml'); print('OK')"
python3 -m py_compile resources/lib/ui/context_menu.py && echo "OK"
```

**Step 4: Commit**

```bash
git add resources/skins/Default/1080i/script-easymovie-contextwindow.xml resources/lib/ui/context_menu.py
git commit -m "fix(skin): resize context menu, remove collection name from Play Full Set label"
```

---

### Task 8: Run full verification

**Step 1: Syntax check all changed files**

```bash
find . -name "*.py" -not -path "*/__pycache__/*" \
  -exec python3 -m py_compile {} \; && \
echo "Syntax OK" && \
pyflakes $(find . -name "*.py" -not -path "*/__pycache__/*")
```

**Step 2: XML parse check all skin files**

```bash
for f in resources/skins/Default/1080i/*.xml; do
  python3 -c "from xml.etree import ElementTree; ElementTree.parse('$f')" && echo "OK: $f" || echo "FAIL: $f"
done
```

**Step 3: Run tests**

```bash
python3 -m pytest tests/ -v
```

**Step 4: Pyright**

```bash
pyright
```

**Step 5: Visual verification on Kodi test instance**

Test each view on vm2 by launching EasyMovie and cycling through browse modes:
1. Poster Wall — check left-edge poster border visible, overlay text spacing, plot scrolls
2. Card List — confirm fanart strip gone, 8 rows visible
3. Posters — check accent line spans full width, collection collapse works
4. Big Screen — check focused row line spacing
5. Split View — check full-width accent, row spacing, 9 rows fit
6. Context menu — check compact size, "Play Full Set" without collection name
7. Continuation + Set Warning dialogs — verify unchanged, still look good
