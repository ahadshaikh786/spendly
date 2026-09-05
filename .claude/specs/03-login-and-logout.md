# Spec: Login and Logout

## Overview
Gives Spendly a real session. Step 1 built the SQLite data layer and Step 2 made it possible to create an account; right now a registered user is redirected to `/login`, which renders a form that goes nowhere, and `/logout` is still a placeholder string. This step wires `login.html` to a real `POST /login` handler that looks the user up by email, verifies the stored werkzeug hash, and stores the user's identity in Flask's signed-cookie `session` — then implements `/logout` to clear it. The navbar starts reflecting who is signed in. Every later step (profile in Step 4, expense CRUD in Steps 7–9) needs `session["user_id"]` to scope data to a user, so this is the gate for all of them.

## Depends on
- Step 1 (database setup) — `get_db()` and the `users` table with `password_hash`. Complete.
- Step 2 (registration) — `create_user()` and a working `POST /register`, so there are real accounts to sign in with. Complete. The seeded `demo@spendly.com` / `demo123` account from `seed_db()` also works for manual testing.

## Routes
- `GET /login` — renders the sign-in form (already implemented; gains a redirect to `/` when the visitor is already signed in) — public
- `POST /login` — validates input, verifies the password against the stored hash, sets `session["user_id"]` / `session["user_name"]` and redirects to `/`, or re-renders the form with an error — public
- `GET /logout` — clears the session and redirects to `/` — public (safe to hit when not signed in)

No new URLs are introduced; all three paths already exist in `app.py`. `/logout` moves out of the "Placeholder routes" section into the main `Routes` section.

## Database changes
No database changes. `users` already stores `id`, `name`, `email`, `password_hash` — everything login needs to authenticate and to fill the session. This step only reads from that table.

## Templates
- **Create:** none
- **Modify:**
  - `templates/base.html` — make the `.nav-links` block conditional on `session.user_id`: signed out shows the existing "Sign in" / "Get started" links unchanged; signed in shows the user's first name and a "Sign out" link pointing at `url_for('logout')`. `session` is available in Jinja by default — do not pass it into `render_template`.
  - `templates/login.html` — no structural change needed; the `{% if error %}<div class="auth-error">` block and both fields are already in place. Only touch it if the implementation needs to preserve the submitted email on a failed attempt (optional, see Rules).

## Files to change
- `app.py` — set `app.secret_key`; change `@app.route("/login")` to `methods=["GET", "POST"]` and implement the handler; move `logout()` up into the `Routes` section and implement it with `session.clear()` + redirect; add `session` to the `flask` import and `get_user_by_email` to the `database.db` import
- `database/db.py` — add `get_user_by_email(email)` under the existing `Users` banner section
- `templates/base.html` — conditional navbar links
- `static/css/style.css` — only if the signed-in navbar needs a new class (e.g. a muted greeting); add it in a new banner section at the end, before Responsive, using existing `:root` variables

## Files to create
None.

## New dependencies
No new dependencies. `werkzeug.security.check_password_hash` ships with Werkzeug, which Flask already requires and `database/db.py` already imports from. Do not add `python-dotenv` — read the secret key with `os.environ.get(...)` and a development fallback.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only — `get_user_by_email()` must use `WHERE email = ?`, never string formatting
- Passwords hashed with werkzeug — verify with `check_password_hash(row["password_hash"], password)`; never compare plaintext, never re-hash the input to compare hashes
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- SQL lives in `database/db.py`, not in the route handler. Add `get_user_by_email(email)` there returning the `sqlite3.Row` or `None`, and close the connection in a `finally` block, matching `create_user()`. **Deliberate call:** the hash *comparison* stays in `app.py` rather than a `verify_user()` helper, so the DB layer stays SQL-only and Step 4's profile page can reuse `get_user_by_email()` unchanged.
- `app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")` — Flask sessions are unsigned and will raise without it. Import `os` in `app.py`.
- Store only `session["user_id"]` and `session["user_name"]`. Never put the email, the password, or the hash in the session — the cookie is signed, not encrypted.
- Normalise the submitted email with `.strip().lower()` before lookup, matching how `POST /register` stores it
- One generic error for both an unknown email and a wrong password — `"Incorrect email or password."` — so the form can't be used to enumerate accounts. Missing fields may use `"All fields are required."`
- **Deliberate call:** successful login redirects to `url_for("landing")`, not `/profile`. `/profile` is still a Step 4 placeholder returning a raw string, and `CLAUDE.md` says not to implement future steps unprompted. Step 4 changes this redirect.
- `/logout` calls `session.clear()` and redirects to `url_for("landing")`. This is the one place a route legitimately doesn't render a template — a redirect, not a raw string, so the "always render a template" rule in `CLAUDE.md` is satisfied.
- Optional: pass `email=email` back into `render_template` on a failed attempt and add `value="{{ email or '' }}"` to the email input so the user doesn't retype it. Never echo the password back.
- Do not add a `@login_required` decorator or protect any existing route — nothing needs guarding until Step 4 introduces a real signed-in page
- Do not touch the `/profile`, `/expenses/*` placeholders, `static/js/main.js`, or the `.bak` files

## Definition of done
- [ ] `GET /login` still renders the sign-in form exactly as before when signed out
- [ ] `POST /login` with `demo@spendly.com` / `demo123` redirects to `/` and the navbar then shows the user's name and a "Sign out" link instead of "Sign in" / "Get started"
- [ ] The signed-in state survives a page reload and navigation to `/terms` and `/privacy`
- [ ] `POST /login` with a correct email and a wrong password re-renders `login.html` with an `auth-error` reading "Incorrect email or password." and does not sign the user in
- [ ] `POST /login` with an email that isn't in `users` shows that same message, worded identically to the wrong-password case
- [ ] `POST /login` with a missing email or password re-renders `login.html` with an `auth-error` message
- [ ] Email matching is case-insensitive — registering `Nitish@Example.com` then signing in as `nitish@example.com` works
- [ ] An account created through `POST /register` can sign in immediately with the password used at registration
- [ ] `GET /logout` clears the session, redirects to `/`, and the navbar reverts to "Sign in" / "Get started"
- [ ] `GET /logout` while already signed out redirects to `/` without raising
- [ ] Visiting `/login` while signed in redirects to `/` instead of showing the form
- [ ] The session cookie contains no email, password, or hash (check DevTools → Application → Cookies, or decode the `session` cookie payload)
- [ ] `git grep -n "SELECT" app.py` returns nothing — all SQL is in `database/db.py`
- [ ] The app still starts cleanly on `http://127.0.0.1:5001` with no errors
