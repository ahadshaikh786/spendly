# Spec: Registration

## Overview
Implements account creation for Spendly. Step 1 built the SQLite data layer (`users`/`expenses` tables, `get_db()`/`init_db()`/`seed_db()`); this step wires the already-built `register.html` form to a real `POST /register` handler that creates a row in `users` with a hashed password. This is the first step where the app writes user-submitted data to the database, and it unblocks later steps (login/session, profile, expense CRUD) that all depend on real user accounts existing.

## Depends on
Step 1 (database setup) — `get_db()`, `init_db()`, and the `users` table must already exist and work. Confirmed complete (`database/db.py` is implemented per current code).

## Routes
- `GET /register` — renders the registration form (already implemented, unchanged) — public
- `POST /register` — validates input, creates the user, redirects to `/login` on success or re-renders the form with an error — public

No login/session handling is in scope here — `/login` stays GET-only until its own step.

## Database changes
No database changes. The `users` table (`id`, `name`, `email`, `password_hash`, `created_at`) already has every column this step needs. Registration will `INSERT` into it using the existing schema from `database/db.py`.

## Templates
- **Create:** none
- **Modify:** `templates/register.html` — add a "Confirm password" `form-group` (`id`/`name` = `confirm_password`, `type="password"`, `required`) directly below the existing password field. The error block and the `name`/`email`/`password` fields are already in place per the "templates are ahead of the backend" note in `CLAUDE.md`.

## Files to change
- `app.py` — change `@app.route("/register")` to accept `methods=["GET", "POST"]`; on `POST`, validate input, create the user, and either redirect to `url_for('login')` or re-render `register.html` with `error=`
- `templates/register.html` — add the confirm-password field
- `database/db.py` — add `create_user()` (see the override note under Rules)

## Files to create
None.

## New dependencies
No new dependencies. `werkzeug.security` is already installed and already used in `database/db.py` for seeding.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug (`generate_password_hash`), never stored in plain text
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- SQL lives in `database/db.py`, not in the route handler — add a `create_user()` helper there and call it from `app.py`. (This overrides an earlier draft of this spec that put the SQL inline; `CLAUDE.md`'s "Never put DB logic in route functions" wins.) "No service/model layer" means no ORM or abstraction layer, not SQL in routes.
- Validate required fields (`name`, `email`, `password`, `confirm_password`) are present and non-empty after stripping
- Enforce a minimum password length of 8 characters, matching the form's placeholder ("Min. 8 characters")
- `password` and `confirm_password` must match exactly — if not, re-render with "Passwords do not match." and create no user. Check this after the length check and before touching the database.
- Treat a duplicate email as a validation error, not a server error — catch the `UNIQUE` constraint (`sqlite3.IntegrityError`) or check for an existing row first, and re-render `register.html` with a friendly `error` message
- Close the DB connection after each request
- Do not add session/login logic — that belongs to a later step

## Definition of done
- [ ] `GET /register` still renders the form exactly as before
- [ ] `POST /register` with a valid new name/email/password creates exactly one new row in `users`, with `password_hash` set (not the plaintext password)
- [ ] `POST /register` on success redirects to `/login`
- [ ] `POST /register` with an email that already exists in `users` re-renders `register.html` with an `auth-error` message and creates no new row
- [ ] `POST /register` with a missing `name`, `email`, `password`, or `confirm_password` re-renders `register.html` with an `auth-error` message
- [ ] `POST /register` with a password under 8 characters re-renders `register.html` with an `auth-error` message
- [ ] `GET /register` renders a "Confirm password" field alongside the password field
- [ ] `POST /register` where `password` and `confirm_password` differ re-renders with "Passwords do not match." and creates no row
- [ ] The app still starts cleanly on `http://127.0.0.1:5001` with no errors
