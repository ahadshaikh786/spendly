# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

"Spendly" — a Flask expense tracker built as a **teaching scaffold**. The UI (landing, auth, legal pages, full CSS design system) is finished; the application logic is deliberately stubbed out and implemented step by step. `app.py` marks the unbuilt routes under a `Placeholder routes — students will implement these` header, each returning a string naming its step (Step 3 logout, Step 4 profile, Steps 7–9 expense CRUD). `database/db.py` and `static/js/main.js` are comment-only placeholders.

Consequences when working here:
- Templates are ahead of the backend. `register.html` and `login.html` POST to routes that currently accept GET only; adding `methods=["GET", "POST"]` plus handling is the intended implementation, not a bug fix elsewhere.
- Don't implement future steps unprompted. If asked for Step N, leave the later placeholders alone.
- `database/db.py` has a contract spelled out in its comments: `get_db()` (SQLite connection with `row_factory` and foreign keys enabled), `init_db()` (`CREATE TABLE IF NOT EXISTS`), `seed_db()` (dev sample data). Follow it.

## Commands

The venv is committed-adjacent but gitignored; use its binaries directly rather than activating.

```bash
python3 -m venv venv                        # first-time setup
venv/bin/pip install -r requirements.txt
venv/bin/python app.py                      # dev server, http://127.0.0.1:5001 (debug=True)
venv/bin/pytest                             # no tests exist yet; pytest + pytest-flask are installed
venv/bin/pytest tests/test_auth.py::test_login -v   # single test, once tests exist
```

Port 5001, not 5000 (macOS AirPlay conflicts with 5000). The SQLite file `expense_tracker.db` is gitignored and created at runtime.

## Structure and conventions

- `app.py` — single module, all routes. No blueprints; keep it that way unless the step calls for it.
- `templates/base.html` — every page extends it. Provides the navbar, footer, `{% block title %}`, `content`, `head`, `scripts`. Use `url_for('route_name')` for internal links, never hardcoded paths.
- `static/css/style.css` — one hand-written stylesheet, no build step, no framework. Organized into banner-commented sections (Variables, Reset, Navbar, Hero, Mock window, Buttons, Features, CTA, Auth pages, Legal pages, Footer, Responsive). Add new styles in a new banner section at the end, before Responsive.
- **All colors, fonts, radii, and widths come from `:root` custom properties** (`--ink*`, `--paper*`, `--accent*`, `--danger*`, `--border*`, `--font-display`/`--font-body`, `--radius-*`). Never introduce a raw hex value in a rule; add a variable if a new one is genuinely needed.
- Design language: warm off-white paper (`--paper`), near-black ink, deep green accent (`#1a472a`), DM Serif Display for headings and DM Sans for body (loaded from Google Fonts in `base.html`).
- Error display convention: templates render `{% if error %}<div class="auth-error">{{ error }}</div>{% endif %}`, so route handlers pass `error=` into `render_template` rather than using flash messages.
- `.bak` files (`style.css.bak`, `landing.html.bak`) are pre-redesign snapshots kept intentionally. Don't edit or delete them, and don't treat them as live code.

## Comment style

Section headers in `app.py` and `style.css` use a fixed-width banner box:

```python
# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #
```

Match it when adding sections.
