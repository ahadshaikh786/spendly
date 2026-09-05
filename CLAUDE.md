# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

"Spendly" — a Flask expense tracker built as a **teaching scaffold**. The UI (landing, auth, legal pages, full CSS design system) is finished; the application logic is deliberately stubbed out and implemented step by step. `app.py` marks the unbuilt routes under a `Placeholder routes — students will implement these` header, each returning a string naming its step (Step 3 logout, Step 4 profile, Steps 7–9 expense CRUD). `database/db.py` and `static/js/main.js` are comment-only placeholders.

Consequences when working here:
- Templates are ahead of the backend. `register.html` and `login.html` POST to routes that currently accept GET only; adding `methods=["GET", "POST"]` plus handling is the intended implementation, not a bug fix elsewhere.
- Don't implement future steps unprompted. If asked for Step N, leave the later placeholders alone.
- `database/db.py` has a contract spelled out in its comments: `get_db()` (SQLite connection with `row_factory` and foreign keys enabled), `init_db()` (`CREATE TABLE IF NOT EXISTS`), `seed_db()` (dev sample data). Follow it.

## Architecture

Flask monolith, no blueprints, no ORM, no build step for frontend assets.

```
app.py                  # single module: Flask app + all routes
database/
  __init__.py           # empty, makes database a package
  db.py                  # get_db() / init_db() / seed_db() contract (Step 1, unimplemented)
templates/               # Jinja2, all extend base.html
  base.html              # navbar, footer, blocks: title / head / content / scripts
  landing.html, login.html, register.html, terms.html, privacy.html
static/
  css/style.css          # one hand-written stylesheet, :root custom properties for theming
  js/main.js             # placeholder, comment-only until a later step
expense_tracker.db       # gitignored SQLite file, created at runtime by init_db()/seed_db()
```

Request flow: browser → Flask route in `app.py` → `render_template()` with a Jinja template from `templates/` (extending `base.html`) → route handlers that need data will call into `database/db.py`'s `get_db()` once it's implemented. There's no service/model layer — routes talk to SQLite directly via `sqlite3` (per the `db.py` contract), and templates receive plain dicts/rows via `render_template(..., **context)`.

No JS framework, no CSS framework, no bundler — `static/js/main.js` and `static/css/style.css` are served as-is via Flask's static handler and linked from `base.html` with `url_for('static', filename=...)`.

## Commands

The venv is committed-adjacent but gitignored; use its binaries directly rather than activating.

```bash
python3 -m venv venv                        # first-time setup
source venv/bin/activate          # Windows: venv\Scripts\activate
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

## Code style

**Python (`app.py`)**
- Double-quoted strings, 4-space indentation, no docstrings or type hints — match the existing plain style.
- One route per function, named after what it serves (`landing`, `register`, `add_expense`, `edit_expense`), with two blank lines between top-level functions (PEP 8).
- Keep route handlers thin: validate/fetch, then a single `render_template(...)` call. Once `database/db.py` is implemented, query through `get_db()` there rather than embedding SQL in `app.py`.

**Templates (`templates/*.html`)**
- 4-space indentation. Every page template opens with `{% extends "base.html" %}`, then `{% block title %}`, then `{% block content %}`.
- Blank line right after `{% block content %}` and right before `{% endblock %}`; blank lines also separate major sections within a block (e.g. header / card / switch-link in the auth pages).
- Use `url_for('route_name')` for `<a>` navigation links, per the existing convention in `base.html`, `login.html`, and `register.html`. The auth forms' `action="/login"` / `action="/register"` are the one existing exception (hardcoded rather than `url_for`) — leave them as-is unless a step specifically calls for changing them.

**CSS (`static/css/style.css`)**
- 4-space indentation. A rule with one or two short declarations collapses to a single line (`.brand-name { color: var(--ink); }`, `.nav-links a:hover { color: var(--ink); }`); anything longer breaks one declaration per line.
- Class selectors only — no IDs, no bare element selectors except in the Reset section (`*`, `html`, `body`, `a`).
- Transitions are inline shorthand on the base rule (`transition: color 0.2s;`), not separate `:hover`-only declarations.

## Comment style

Section headers in `app.py` and `style.css` use a fixed-width banner box:

```python
# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #
```

Match it when adding sections.

## Warnings and things to avoid
Never use raw string returns for stub routes once a step is implemented — always render a template
Never hardcode URLs in templates — always use url_for()
Never put DB logic in route functions — it belongs in database/db.py
Never install new packages mid-feature without flagging it — keep requirements.txt in sync
Never use JS frameworks — the frontend is intentionally vanilla
database/db.py is currently empty — do not assume helpers exist until the step that implements them
FK enforcement is manual — SQLite foreign keys are off by default; get_db() must run PRAGMA foreign_keys = ON on every connection
The app runs on port 5001, not the Flask default 5000 — don't change this