# EasyMovie Release Template

This is a Claude Code prompt document — direct instructions for writing release artifacts.
Follow these rules exactly when creating release content.

## Config

- **Repository:** https://github.com/Rouzax/script.easymovie
- **Forum Thread:** TBD

## Version Format Rules

| Context | Format | Example |
|---------|--------|---------|
| `addon.xml` version attribute | `~` (tilde) | `1.0.0~alpha1` |
| `changelog.txt` header | `~` (tilde) | `v1.0.0~alpha1` |
| `addon.xml` `<news>` section | `~` (tilde) | `v1.0.0~alpha1` |
| Git tag | `-` (hyphen) | `v1.0.0-alpha1` |
| GitHub release title | `-` (hyphen) | `EasyMovie v1.0.0-alpha1` |
| GitHub URLs / links | `-` (hyphen) | `.../releases/tag/v1.0.0-alpha1` |
| Forum/Reddit post text | `-` (hyphen) | `v1.0.0-alpha1` |
| Commit message | `-` (hyphen) | `Release v1.0.0-alpha1 - Summary` |
| Zip filename | `-` (hyphen) | `script.easymovie-v1.0.0-alpha1.zip` |

**Rule of thumb:** Anything Kodi reads uses `~`. Anything on GitHub or in URLs uses `-`.
When filling in links, always convert `~` to `-` in the version string.

Stable versions are unaffected — `1.0.0` is the same everywhere.

Pre-release suffix order: `alpha` → `beta` → `rc` → stable (no suffix).

## Audience Guidelines

| Artifact | Audience | Tone & Content |
|----------|----------|----------------|
| `changelog.txt` | Developers | Technical and precise. Mention code-level changes, refactors, root causes, renamed functions. This is the developer record. |
| `addon.xml` `<news>` | End users (Kodi UI) | Short, plain language. Focus on what the user *experiences*: new capabilities, fixed annoyances. No code details. |
| GitHub Release Notes | Mixed (users + devs) | Polished markdown. Lead with user-facing changes, then technical/internal section. |
| Forum Post | End users only | Friendly, easy to scan. Highlight what's new/fixed in simple terms. No jargon. BBCode format. |
| Reddit Post | End users only | Brief and engaging. Emphasize the most interesting changes. Markdown format. |

## Consolidation Rules

Before writing any section, review the full changelog entry and git history for the current version.
Merge all changes into a coherent whole:

1. **Do NOT list a bug fix for something introduced in the same version.** If a feature was added and then fixed during the same development cycle, show the feature in its final working state. Users never saw the broken version.

2. **Do NOT list iterative refinements as separate items.** If a feature was built, then improved, then tweaked — describe the final result once, not the journey.

3. **DO still list intermediate steps in `changelog.txt`** if they represent meaningful development milestones, but consolidate them into a clean narrative.

4. **Corollary:** If a bug was introduced in a prior release (alpha1 or earlier), it gets its own Bug Fix entry in the current release.

## Output Formats

### changelog.txt

```
v{VERSION_TILDE} ({DATE})
--------------------------
New Features:
  - {description, technical precision, multi-line OK with indented continuation}

Bug Fixes:
  - Fixed: {description with root cause where useful}

Improvements:
  - {description}

Performance:
  - {description}

Internal:
  - {description, can reference code symbols}

Breaking Changes:
  - {impact on user + migration path}
```

Rules:
- Use only applicable section headers — omit empty sections
- Past tense throughout
- No emoji
- Multi-line bullets: indent continuation lines to align with first line of text

### addon.xml `<news>`

```
v{VERSION_TILDE} ({DATE})
- {bullet 1, plain user language}
- {bullet 2}
- {bullet 3}
```

Rules:
- Maximum ~6 bullets — this is a teaser, not a full changelog
- No section headers, no emoji, no code references
- One line per bullet preferred
- Outcome-focused: what changed for the user, not how

### Git Commit + Tag

```
Commit message: Release v{VERSION_HYPHEN} - {one-line summary}
Tag: v{VERSION_HYPHEN} (annotated, same message as commit)
```

### GitHub Release Notes

```markdown
## EasyMovie v{VERSION_TILDE}

{One-line summary}

### Breaking Changes

- **{name}** — {impact + migration path}

### New Features

- **{Feature name}** — {Description, outcome-focused with enough technical precision for power users}

### Bug Fixes

- **{Fix name}** — {Description}

### Internal

- {Description}

---

[Full Changelog](https://github.com/Rouzax/script.easymovie/blob/main/changelog.txt)
```

Rules:
- Title: `EasyMovie v{VERSION_HYPHEN}` (GitHub release title field, hyphen format)
- Header line inside body uses tilde: `## EasyMovie v{VERSION_TILDE}`
- Set `--prerelease` flag if alpha/beta/rc
- Omit sections with no items
- Breaking Changes section goes first, only if applicable
- Use bold for feature/fix names

### Forum Post (BBCode)

```bbcode
[B]EasyMovie v{VERSION_HYPHEN} Released[/B]

{One-line summary}

[B]What's New:[/B]
[LIST]
[*] {item}
[/LIST]

[B]Bug Fixes:[/B]
[LIST]
[*] {item}
[/LIST]

[B]Download:[/B]
[URL=https://github.com/Rouzax/script.easymovie/releases/tag/v{VERSION_HYPHEN}]GitHub Release[/URL]

[B]Full Changelog:[/B]
[URL=https://github.com/Rouzax/script.easymovie/blob/main/changelog.txt]changelog.txt[/URL]
```

### Reddit Post

```markdown
**Title:** EasyMovie v{VERSION_HYPHEN} - {one-line summary}

**Body:**
EasyMovie is a Kodi addon that simplifies movie night. Answer a few questions (genre, rating, runtime) and get a curated random selection from your library.

**What's new in v{VERSION_HYPHEN}:**
- {item}
- {item}

**Links:**
- [GitHub Release](https://github.com/Rouzax/script.easymovie/releases/tag/v{VERSION_HYPHEN})
```

## 10 Key Rules (Always Apply)

1. TILDE in Kodi files (addon.xml, changelog.txt), HYPHEN in git/GitHub/zip filename
2. Never list a bug fix for something introduced in the same version
3. changelog.txt = technical/developer audience
4. addon.xml `<news>` = plain user language, max 6 bullets, no headers, no emoji
5. GitHub notes = mixed audience, outcome-focused
6. Forum/Reddit = conversational, user-benefit focused
7. Zip filename: `script.easymovie-v{VERSION_HYPHEN}.zip` (always hyphen, always v prefix)
8. Release commit message: `Release v{VERSION_HYPHEN} - {summary}`
9. Git tag is annotated (`-a`), same message as commit
10. Pre-release flag: set `--prerelease` on GitHub release for alpha/beta/rc
