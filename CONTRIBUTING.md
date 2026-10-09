# Contributing to EasyMovie

Thank you for your interest in contributing to EasyMovie! This document outlines how you can help.

## Important Note

This project is maintained in my spare time. Response times may vary, and I may not be able to address every issue or request immediately. Your patience is appreciated!

---

## How to Contribute

### Reporting Bugs

Found something broken? Please open an issue with:

1. **Kodi version** (e.g., Kodi 21.1 Omega)
2. **Operating system** (e.g., Windows 11, LibreELEC 12, etc.)
3. **Steps to reproduce** the problem
4. **Expected behavior** vs **actual behavior**
5. **Log file** if possible (see [LOGGING.md](LOGGING.md) for how to enable debug logging)

[Open a bug report →](https://github.com/Rouzax/script.easymovie/issues/new)

### Suggesting Features

Have an idea? Open an issue describing:

1. **What** you'd like to see
2. **Why** it would be useful
3. **How** you envision it working

I can't promise every feature will be implemented, but I do read all suggestions.

[Suggest a feature →](https://github.com/Rouzax/script.easymovie/issues/new)

### Pull Requests

#### Skins
I'm not a skinner, so **skin contributions and improvements are especially welcome!** The default skin files are in:
```
resources/skins/Default/1080i/
```

If you create or improve a skin, please submit a PR.

#### Code Changes
For code changes:

1. **Open an issue first** to discuss the change
2. Fork the repository
3. Create a branch for your changes
4. Follow the existing code style
5. Test your changes in Kodi
6. Submit a pull request

Please keep PRs focused — one feature or fix per PR makes review easier.

---

## Issue Labels and Milestones

Labels say what an issue is or what it is waiting on. Milestones say when it is expected to ship.

**Labels**

| Label | Meaning |
|-------|---------|
| `bug` | Something isn't working. Set automatically by the bug report form. |
| `enhancement` | A new feature or improvement. Set automatically by the feature request form. |
| `documentation` | The docs need changing, not the add-on. |
| `needs-info` | Waiting on the reporter. The issue may be closed if the details never arrive. |
| `needs-upstream` | Waiting on Kodi or a skin. EasyMovie cannot fix it on its own. |
| `duplicate`, `invalid`, `wontfix` | Why an issue was closed without a change. |

**Milestones**

| Milestone | Meaning |
|-----------|---------|
| Next | Planned for the coming release. At release it is renamed to that version and closed, and a new Next is opened. |
| Later | Accepted, but not planned for a particular release yet. |

An issue without a milestone has not been triaged yet. Open milestones do not promise a version number; closed milestones record what each release shipped, and [changelog.txt](changelog.txt) describes the changes.

The label list lives in [.github/sync-labels.sh](.github/sync-labels.sh). Change labels there and run the script, rather than editing them on GitHub.

---

## Code Style

- Python 3.11+ compatible (Kodi 21 minimum)
- Type hints where practical
- Clear, descriptive naming
- Follow existing patterns in the codebase

---

## Development Setup

1. Clone the repository
2. Install [Kodistubs](https://pypi.org/project/Kodistubs/) for IDE support:
   ```bash
   pip install Kodistubs
   ```
3. Symlink or copy to your Kodi addons folder for testing

---

## Project Structure

```
script.easymovie/
├── default.py              # Entry point (one-liner)
├── addon.xml               # Kodi addon metadata
├── resources/
│   ├── settings.xml        # Settings definition (Kodi 21+ format)
│   ├── settings_clone.xml  # Clone addon settings template
│   ├── addon_clone.xml     # Clone addon metadata template
│   ├── selector.py         # Genre/MPAA selection dialog
│   ├── clone.py            # Clone addon creator
│   ├── language/
│   │   └── resource.language.en_gb/
│   │       └── strings.po
│   ├── skins/
│   │   └── Default/1080i/
│   │       ├── script-easymovie-postergrid.xml
│   │       ├── script-easymovie-cardlist.xml
│   │       └── ...
│   └── lib/                # Core library modules
│       ├── constants.py    # All magic values
│       ├── utils.py        # Shared utilities (logging, JSON-RPC, settings)
│       ├── data/           # Data layer
│       │   ├── queries.py      # JSON-RPC query builders
│       │   ├── filters.py      # Movie filter engine
│       │   ├── movie_sets.py   # Movie set awareness logic
│       │   ├── results.py      # Result selection and sorting
│       │   └── storage.py      # Persistent storage
│       ├── ui/             # User interface
│       │   ├── main.py         # Entry point orchestration
│       │   ├── wizard.py       # Filter wizard flow
│       │   ├── dialogs.py      # Dialog helpers
│       │   ├── browse_window.py# Browse window controller
│       │   └── settings.py     # Settings loader
│       └── playback/       # Playback logic
│           ├── player.py           # Movie player
│           ├── playlist_builder.py # Playlist builder
│           └── playback_monitor.py # Set continuation
```

---

## Architecture Principles

1. **Entry points are minimal** — `default.py` contains only a one-liner delegation to library modules

2. **No global settings** — Settings are loaded inside functions when needed, never at module level

3. **Structured logging** — Use `get_logger()` from utils.py; logs include context via keyword arguments. See [LOGGING.md](LOGGING.md) for guidelines.

4. **Constants centralized** — All magic values live in `constants.py`

---

## Adding New Features

1. **Add constants** to `resources/lib/constants.py`
2. **Add settings** to `resources/settings.xml` and localization strings
3. **Add data access** to appropriate module in `resources/lib/data/`
4. **Add UI** to appropriate module in `resources/lib/ui/`
5. **Wire up** in the main entry point

---

## Testing Locally

Install the pinned dev tooling once, then run the same gate that pre-commit and CI run:

```bash
# Install the pinned dev tools
pip install -r requirements-dev.txt

# Lint + import sorting
ruff check

# Static analysis
pyflakes $(find . -name "*.py" -not -path "*/__pycache__/*")

# Type checking (Python 3.11 target)
pyright

# Dead-code detection
vulture resources/lib --min-confidence 80

# Tests + coverage
python3 -m pytest tests/ --ignore=tests/integration --cov=resources/lib
```

Or run the whole gate through pre-commit (recommended; install the hooks once):

```bash
pre-commit install && pre-commit install --hook-type pre-push
pre-commit run --all-files
```

---

## Questions?

If you're unsure about something, ask in the [Kodi forum thread](https://forum.kodi.tv/showthread.php?tid=385063), or open an issue if it concerns a change you want to make. I'd rather answer questions than have contributions go to waste.

Thanks for helping make EasyMovie better!
