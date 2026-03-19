---
description: Run the full EasyMovie release workflow
---

# Release Workflow

You are executing the EasyMovie release workflow. Follow each step in order.
Do not skip steps. Stop and ask the user if anything is ambiguous.

## Step 0: Establish Context

1. Read `addon.xml` — extract the `version` attribute (tilde format, e.g., `1.0.0~alpha1`)
2. Read `changelog.txt` — confirm the top entry version matches addon.xml
3. Compute both formats:
   - `TILDE_VERSION` = version as-is from addon.xml (e.g., `1.0.0~alpha1`)
   - `HYPHEN_VERSION` = replace `~` with `-` (e.g., `1.0.0-alpha1`)
4. Detect pre-release: YES if version contains `alpha`, `beta`, or `rc`; NO otherwise
5. Show the user: version (both formats), pre-release status, today's date

## Step 1: Pre-Release Validation

Run ALL of these checks. Report results as a checklist. If ANY check fails, STOP and describe what needs resolving. Do not continue until the user confirms.

- [ ] **Syntax check passes:** `find . -name "*.py" -not -path "*/__pycache__/*" -exec python3 -m py_compile {} \;`
- [ ] **Static analysis clean:** `pyflakes $(find . -name "*.py" -not -path "*/__pycache__/*")`
- [ ] **Type checking passes:** `pyright`
- [ ] **addon.xml version matches changelog.txt top entry**
- [ ] **All changes committed:** `git status` shows clean working tree
- [ ] **No existing git tag:** `git tag -l "v{HYPHEN_VERSION}"` returns empty
- [ ] **No existing GitHub release:** `gh release view "v{HYPHEN_VERSION}"` returns error
- [ ] **Kodi addon checker passes:** `kodi-addon-checker --branch omega .` (warnings about dev files like `__pycache__`, `.ruff_cache` are expected — only errors/problems are blockers)
- [ ] **Zip excludes match .gitignore:** Read `.gitignore` and verify every dev-only entry is covered by the zip exclude list in CLAUDE.md. Flag any missing exclusions.

## Step 2: Read Release Template

Read `.claude/release-template.md` for version format rules, audience guidelines, consolidation rules, and output format specifications. Follow them exactly for all subsequent writing.

## Step 3: Analyze Changes

1. Read the changelog.txt entry for this version (the top entry)
2. Run `git log` since the previous tag to check for any changes not yet in the changelog
3. Apply consolidation rules:
   - Identify any bug fixes for things introduced in the same version — collapse them
   - Identify iterative refinements — consolidate to final result
4. Summarize the changes and show to the user for confirmation before writing anything

## Step 4: Draft All Content

Draft all release content and show it for review. Do NOT edit any files yet.

### 4a. Draft changelog.txt changes

- Verify the existing entry follows the template format
- Confirm correct version header (tilde format), today's date
- Show the entry to the user — propose corrections if needed

### 4b. Draft addon.xml `<news>`

- Write 4-6 bullets in plain user language following the template rules
- No section headers, no emoji, no code references
- Header line: `v{TILDE_VERSION} ({DATE})`
- Show the proposed `<news>` content to the user

### 4c. Draft GitHub release notes

- Write release notes following the GitHub Release Notes template from `.claude/release-template.md`
- Show the full release notes to the user

### 4d. Draft commit message

- Format: `Release v{HYPHEN_VERSION} - {one-line summary}`
- The summary should capture the most important change(s) in this release
- Show the commit message to the user

### 4e. Review gate

Present all four drafts together and ask the user: **"All content ready. Approve to publish?"**

Do NOT proceed until the user explicitly approves. If they request changes, revise the drafts and show them again.

## Step 5: Publish

Only proceed here after the user has approved all content in Step 4e.

### 5a. Write changelog.txt + addon.xml

- Apply the approved changelog.txt changes
- Update the `<news>` element in addon.xml with approved content

### 5b. Commit

- Stage `changelog.txt` and `addon.xml`
- Commit with the approved message

### 5c. Git Tag

- Create annotated tag: `git tag -a "v{HYPHEN_VERSION}" -m "Release v{HYPHEN_VERSION} - {summary}"`

### 5d. Push

- Push commit and tag: `git push origin main && git push origin "v{HYPHEN_VERSION}"`

### 5e. Build Zip

Use the packaging command from CLAUDE.md, but substitute the version for the zip filename so tildes become hyphens and include the `v` prefix:

```bash
cd /home/martijn && \
version=$(python3 -c "
from xml.etree import ElementTree as et
tree = et.parse('script.easymovie/addon.xml')
v = tree.getroot().get('version').replace('~', '-')
print(v)
") && \
zip -r "script.easymovie-v${version}.zip" script.easymovie/ \
  -x "script.easymovie/.git/*" \
  -x "script.easymovie/.git*" \
  -x "script.easymovie/.github/*" \
  -x "script.easymovie/.claude/*" \
  -x "script.easymovie/.claudeignore" \
  -x "script.easymovie/.mcp.json" \
  -x "script.easymovie/CLAUDE.md" \
  -x "script.easymovie/CONTRIBUTING.md" \
  -x "script.easymovie/LOGGING.md" \
  -x "script.easymovie/README.md" \
  -x "script.easymovie/pyrightconfig.json" \
  -x "script.easymovie/.pyflakes" \
  -x "script.easymovie/docs/*" \
  -x "script.easymovie/docs/" \
  -x "script.easymovie/__pycache__/*" \
  -x "script.easymovie/**/__pycache__/*" \
  -x "script.easymovie/*.log" \
  -x "script.easymovie/_temp/*" \
  -x "script.easymovie/_temp/"
```

### 5f. Create GitHub Release

Create the release using the approved notes.

```bash
gh release create "v{HYPHEN_VERSION}" \
  "/home/martijn/script.easymovie-v{HYPHEN_VERSION}.zip" \
  --title "EasyMovie v{HYPHEN_VERSION}" \
  --notes "$(cat <<'EOF'
{RELEASE_NOTES}
EOF
)" \
  {--prerelease if alpha/beta/rc}
```

## Step 6: Submit to Kodi Official Repository (Stable Only)

**Skip this step entirely if the release is a pre-release (alpha/beta/rc).**

Ask the user: **"Submit v{TILDE_VERSION} to the official Kodi repo?"** Do not proceed unless they confirm.

### 6a. Sync fork and prepare commit

```bash
cd /tmp && rm -rf repo-scripts
gh repo clone Rouzax/repo-scripts -- --branch omega --single-branch
cd repo-scripts
git remote add upstream https://github.com/xbmc/repo-scripts.git
git fetch upstream omega
git reset --hard upstream/omega
```

### 6b. Copy addon files

Copy the addon, excluding all dev-only files (same exclusions as the zip):

```bash
rm -rf script.easymovie
rsync -a /home/martijn/script.easymovie/ script.easymovie/ \
  --exclude='.git' --exclude='.git*' --exclude='.github' \
  --exclude='.claude' --exclude='.claudeignore' --exclude='.mcp.json' \
  --exclude='CLAUDE.md' --exclude='CONTRIBUTING.md' \
  --exclude='LOGGING.md' --exclude='README.md' \
  --exclude='pyrightconfig.json' --exclude='.pyflakes' \
  --exclude='docs' --exclude='__pycache__' --exclude='*.log' \
  --exclude='_temp' --exclude='.worktrees' --exclude='.ruff_cache' \
  --exclude='.pytest_cache' --exclude='tests' \
  --exclude='conftest.py' --exclude='pytest.ini'
```

### 6c. Run kodi-addon-checker against the clean copy

```bash
kodi-addon-checker --branch omega /tmp/repo-scripts
```

This validates the exact files that will be submitted. Only warnings about the forum URL (403) are expected — any problems are blockers.

### 6d. Create single commit and push

Kodi requires exactly one commit per PR with message format `[addonid] version`:

```bash
cd /tmp/repo-scripts
git add script.easymovie/
git commit -m "[script.easymovie] {TILDE_VERSION}"
git push --force origin omega
```

### 6e. Create PR

Check for an existing open PR first to avoid duplicates:

```bash
existing=$(gh pr list --repo xbmc/repo-scripts --head Rouzax:omega --state open --json number --jq '.[0].number')
if [ -n "$existing" ]; then
  echo "Existing PR #$existing updated via force-push"
else
  gh pr create --repo xbmc/repo-scripts \
    --base omega --head Rouzax:omega \
    --title "[script.easymovie] {TILDE_VERSION}" \
    --body "$(cat <<'EOF'
**Version:** {TILDE_VERSION}
**Source:** https://github.com/Rouzax/script.easymovie
**Forum:** TBD
EOF
)"
fi
```

### 6f. Cleanup

```bash
rm -rf /tmp/repo-scripts
```

## Step 7: Forum & Reddit Copy (Optional)

Ask the user if they want forum post and/or reddit post text generated.
If yes, write them following the templates in `.claude/release-template.md`.

## Step 8: Summary

Report all artifacts created:

- Version released: `v{HYPHEN_VERSION}`
- Git tag: `v{HYPHEN_VERSION}`
- Commit pushed: yes/no
- GitHub release URL: `https://github.com/Rouzax/script.easymovie/releases/tag/v{HYPHEN_VERSION}`
- Zip file: path and size
- Kodi repo PR: URL or skipped (pre-release)
- Forum/Reddit copy: generated or skipped
