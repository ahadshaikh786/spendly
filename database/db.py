import os
import sqlite3
from datetime import date

from werkzeug.security import generate_password_hash


# ------------------------------------------------------------------ #
# Configuration                                                       #
# ------------------------------------------------------------------ #

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "expense_tracker.db")

CATEGORIES = [
    "Food",
    "Transport",
    "Bills",
    "Health",
    "Entertainment",
    "Shopping",
    "Other",
]


# ------------------------------------------------------------------ #
# Connection                                                          #
# ------------------------------------------------------------------ #

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    # SQLite defaults foreign keys off and forgets the setting on close.
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# ------------------------------------------------------------------ #
# Schema                                                              #
# ------------------------------------------------------------------ #

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            name          TEXT NOT NULL,
            email         TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at    TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            amount      REAL    NOT NULL,
            category    TEXT    NOT NULL,
            date        TEXT    NOT NULL,
            description TEXT,
            created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    conn.commit()
    conn.close()


# ------------------------------------------------------------------ #
# Seed data                                                           #
# ------------------------------------------------------------------ #

def seed_db():
    conn = get_db()

    if conn.execute("SELECT COUNT(*) FROM users").fetchone()[0] > 0:
        conn.close()
        return

    cursor = conn.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        ("Demo User", "demo@spendly.com", generate_password_hash("demo123")),
    )
    user_id = cursor.lastrowid

    month = date.today().strftime("%Y-%m")
    expenses = [
        (user_id, 450.00, "Food", month + "-03", "Groceries for the week"),
        (user_id, 120.00, "Transport", month + "-05", "Auto to office"),
        (user_id, 1899.00, "Bills", month + "-07", "Electricity bill"),
        (user_id, 650.00, "Health", month + "-10", "Monthly medicines"),
        (user_id, 499.00, "Entertainment", month + "-12", "Streaming subscription"),
        (user_id, 2250.00, "Shopping", month + "-15", "Running shoes"),
        (user_id, 300.00, "Other", month + "-18", "Gift for a friend"),
        (user_id, 280.00, "Food", month + "-20", "Dinner with friends"),
    ]
    conn.executemany(
        "INSERT INTO expenses (user_id, amount, category, date, description)"
        " VALUES (?, ?, ?, ?, ?)",
        expenses,
    )

    conn.commit()
    conn.close()


# ------------------------------------------------------------------ #
# Users                                                               #
# ------------------------------------------------------------------ #

def create_user(name, email, password):
    conn = get_db()
    try:
        cursor = conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            (name, email, generate_password_hash(password)),
        )
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()


def get_user_by_email(email):
    conn = get_db()
    try:
        return conn.execute(
            "SELECT * FROM users WHERE email = ?", (email,)
        ).fetchone()
    finally:
        conn.close()


def get_user_by_id(user_id):
    conn = get_db()
    try:
        # Explicit columns, not SELECT * — this row is rendered into a
        # template, so password_hash must not be in it at all.
        return conn.execute(
            "SELECT id, name, email, created_at FROM users WHERE id = ?", (user_id,)
        ).fetchone()
    finally:
        conn.close()


# ------------------------------------------------------------------ #
# Expenses                                                            #
# ------------------------------------------------------------------ #

def get_expense_summary(user_id):
    conn = get_db()
    try:
        return conn.execute(
            "SELECT COUNT(*) AS count, COALESCE(SUM(amount), 0) AS total,"
            " MIN(date) AS first_date, MAX(date) AS last_date"
            " FROM expenses WHERE user_id = ?",
            (user_id,),
        ).fetchone()
    finally:
        conn.close()


def get_month_total(user_id, month):
    conn = get_db()
    try:
        return conn.execute(
            "SELECT COUNT(*) AS count, COALESCE(SUM(amount), 0) AS total"
            " FROM expenses WHERE user_id = ? AND substr(date, 1, 7) = ?",
            (user_id, month),
        ).fetchone()
    finally:
        conn.close()


def get_category_totals(user_id):
    conn = get_db()
    try:
        return conn.execute(
            "SELECT category, COUNT(*) AS count, SUM(amount) AS total"
            " FROM expenses WHERE user_id = ?"
            " GROUP BY category ORDER BY total DESC",
            (user_id,),
        ).fetchall()
    finally:
        conn.close()


def get_recent_expenses(user_id, limit):
    conn = get_db()
    try:
        return conn.execute(
            "SELECT id, amount, category, date, description FROM expenses"
            " WHERE user_id = ? ORDER BY date DESC, id DESC LIMIT ?",
            (user_id, limit),
        ).fetchall()
    finally:
        conn.close()
