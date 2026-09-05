# Spec: Profile Page

## Overview
Turns `/profile` from a placeholder string into Spendly's first genuinely private page. Step 3 gave the app a real session but nothing yet depends on it — every route is still reachable signed out, and a successful login dumps the user back on the marketing landing page. This step adds a `@login_required` decorator, points it at a new `profile.html` that renders the signed-in user's account details read fresh from the `users` table, and changes the post-login redirect to land there. It is the first page in the app that answers "who am I signed in as", and the decorator it introduces is the same gate Steps 7–9 will reuse to scope expense CRUD to a single user.

## Depends on
- Step 1 (database setup) — `get_db()`, the `users` table, and its `created_at` column. Complete.
- Step 2 (registration) — `create_user()` and `POST /register`, so accounts exist to view. Complete.
- Step 3 (login and logout) — `session["user_id"]` / `session["user_name"]` and the conditional navbar in `base.html`. Complete. This step is the first consumer of that session, and it takes over the `login()` redirect that Step 3 deliberately left pointing at `landing`. (Where it now points is amended under Routes.)

## Routes
- `GET /profile` — renders the signed-in user's account details; redirects to `/login` when signed out — logged-in
- `GET /login` — unchanged URL and method, but a successful `POST` no longer redirects to `url_for("landing")` — public

> **Amended after implementation.** This step originally pointed the post-login redirect at `url_for("profile")`. A dashboard at `/dashboard` was built immediately afterwards, and login now lands there instead — a dashboard is the more useful landing than an account page. `/profile` is reached from the navbar. The already-signed-in guards on `/login` and `/register` still redirect to `landing`; only the successful-`POST` branch changed.

No new URLs are introduced. `/profile` already exists in `app.py` and moves out of the "Placeholder routes — students will implement these" section into the main `Routes` section, leaving only the three `/expenses/*` placeholders behind.

## Database changes
No database changes. `users` already has `id`, `name`, `email`, `password_hash` and `created_at TEXT NOT NULL DEFAULT (datetime('now'))` — everything the page displays. This step only reads from that table, and adds no columns, tables or constraints.

## Templates
- **Create:**
  - `templates/profile.html` — extends `base.html`; a page header, then a card listing the account's name, email and "Member since", plus an initials avatar derived from the user's name. Follows the `auth-section` / `auth-container` structural rhythm already used by `login.html` and `register.html`.
- **Modify:**
  - `templates/base.html` — add a "Profile" link inside the existing `{% if session.user_id %}` branch of `.nav-links`, before the "Sign out" link, using `url_for('profile')`. Do not touch the signed-out branch.

## Files to change
- `app.py` — add `functools.wraps` and `datetime` imports; add `get_user_by_id` to the `database.db` import; add a `login_required` decorator in its own banner section above `Routes`; implement `profile()` and move it up into `Routes`; change the successful-login redirect away from `url_for("landing")` (now `url_for("dashboard")` — see the amendment under Routes)
- `database/db.py` — add `get_user_by_id(user_id)` under the existing `Users` banner section, beside `get_user_by_email()`
- `templates/base.html` — add the "Profile" nav link to the signed-in branch
- `static/css/style.css` — add a `Profile page` banner section at the end, before `Responsive`, plus a `.nav-links` rule for the new link if the existing anchor styling isn't enough

## Files to create
- `.claude/specs/04-profile-page.md` — this spec
- `templates/profile.html`

## New dependencies
No new dependencies. `functools` and `datetime` are standard library, and `datetime` is already imported in `database/db.py`. Nothing is added to `requirements.txt`.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only — `get_user_by_id()` must use `WHERE id = ?`, never string formatting or f-strings
- Passwords hashed with werkzeug — this page never displays, re-hashes, or verifies a password; `password_hash` must not reach the template
- Use CSS variables — never hardcode hex values; the avatar, card and label styling all come from `--ink*`, `--paper*`, `--accent*`, `--border*` and `--radius-*`
- All templates extend `base.html`
- SQL lives in `database/db.py`, not in the route handler. `get_user_by_id(user_id)` returns the `sqlite3.Row` or `None` and closes its connection in a `finally` block, matching `get_user_by_email()`.
- **Read the user fresh from the database, not from the session.** `session["user_name"]` exists but is a cached copy; the profile page is the one place that must show the row of record. The session stays the identity token only.
- Add `login_required` as a decorator using `functools.wraps`, in its own banner-boxed section between `Database bootstrap` and `Routes`. It redirects to `url_for("login")` when `session.get("user_id")` is falsy. Applying it to `/profile` is the whole of its use this step — **do not** apply it to the `/expenses/*` placeholders.
- Handle the stale-session case: if `session["user_id"]` is set but `get_user_by_id()` returns `None` (the row was deleted), call `session.clear()` and redirect to `url_for("login")` rather than rendering with `None` and raising in the template.
- **Deliberate call:** the profile page is read-only this step — no edit form, no `POST /profile`, no password change, no delete-account. `CLAUDE.md` lists Step 4 as "profile" with nothing about mutation, and says not to implement future steps unprompted. Display only.
- **Deliberate call:** no expense statistics on this page (no count, no month total, no category breakdown). The `expenses` table is seeded and queryable, but reading it belongs to the dashboard and CRUD steps (7–9). Keep Step 4 to the `users` row.
- **Deliberate call:** format `created_at` into "Member since" text in the route with `datetime.strptime(user["created_at"], "%Y-%m-%d %H:%M:%S").strftime("%B %Y")`, then pass the finished string to the template. Presentation formatting is neither SQL nor Jinja logic, and `CLAUDE.md` wants thin routes ending in one `render_template(...)` — a two-line format before that call keeps `db.py` SQL-only and the template free of date munging.
- Derive the avatar initials in the template from the fetched row (`user.name`), not from `session.user_name`, and guard against a single-word name so a one-word name doesn't raise on an index.
- Keep the route thin: guard, fetch, format, one `render_template("profile.html", ...)` call
- Double-quoted strings, 4-space indent, no docstrings or type hints, two blank lines between top-level functions — match the existing `app.py` style
- `profile.html` opens with `{% extends "base.html" %}`, then `{% block title %}`, then `{% block content %}`, with a blank line after `{% block content %}` and before `{% endblock %}`, and blank lines between the header / card / footer-note sections
- CSS: class selectors only, 4-space indent, one- or two-declaration rules collapse to a single line, transitions inline on the base rule
- Do not touch the `/expenses/*` placeholders, `static/js/main.js`, the `.bak` files, or the seeded data in `seed_db()`
- Do not change the port (5001) and do not add blueprints

## Definition of done
- [ ] `GET /profile` while signed out redirects to `/login` and does not render any profile markup
- [ ] `GET /profile` after signing in as `demo@spendly.com` / `demo123` renders `profile.html` showing the name "Demo User", the email `demo@spendly.com`, and a "Member since" month and year
- [ ] The page no longer returns the raw string "Profile page — coming in Step 4" anywhere
- [ ] A successful `POST /login` no longer lands on `/` (it lands on `/dashboard` — see the Routes amendment)
- [ ] Registering a brand-new account, then signing in, shows that account's own name and email on `/profile` — not the demo user's
- [ ] Changing a user's `name` directly in the database and reloading `/profile` shows the new name without signing out and back in (proves the page reads the row, not the session)
- [ ] The navbar on `/profile` shows the "Profile" link and "Sign out" while signed in, and reverts to "Sign in" / "Get started" after `GET /logout`
- [ ] The "Profile" link is absent from the navbar when signed out, on every page
- [ ] `GET /logout` then `GET /profile` redirects to `/login`
- [ ] A user whose row is deleted from `users` while their session is live is redirected to `/login` on the next `/profile` request instead of raising a 500
- [ ] An account registered with a single-word name (e.g. "Nitish") renders `/profile` without raising
- [ ] Viewing source on `/profile` shows no password hash and no `password` field
- [ ] `git grep -n "SELECT" app.py` returns nothing — all SQL is in `database/db.py`
- [ ] `git grep -nE "#[0-9a-fA-F]{3,6}" static/css/style.css` reports no new hex values outside the `:root` block
- [ ] The new CSS sits in its own banner section before `Responsive`, and `/profile` is readable at 375px wide with no horizontal scroll
- [ ] `/`, `/login`, `/register`, `/terms` and `/privacy` all still render unchanged, signed in and signed out
- [ ] The app starts cleanly on `http://127.0.0.1:5001` with no errors
