import os
from datetime import date, datetime
from functools import wraps

from flask import Flask, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash

from database.db import (
    create_user,
    get_category_totals,
    get_db,
    get_expense_summary,
    get_month_total,
    get_recent_expenses,
    get_user_by_email,
    get_user_by_id,
    init_db,
    seed_db,
)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")


# ------------------------------------------------------------------ #
# Database bootstrap                                                  #
# ------------------------------------------------------------------ #

with app.app_context():
    init_db()
    seed_db()


# ------------------------------------------------------------------ #
# Presentation helpers                                                #
# ------------------------------------------------------------------ #

CATEGORY_ICONS = {
    "Food": "utensils",
    "Transport": "bus",
    "Bills": "zap",
    "Health": "heart-pulse",
    "Entertainment": "clapperboard",
    "Shopping": "shopping-bag",
    "Other": "ellipsis",
}


@app.template_filter("rupees")
def rupees(amount):
    whole, _, paise = "{:.2f}".format(amount).partition(".")
    if len(whole) > 3:
        head, tail = whole[:-3], whole[-3:]
        groups = []
        while len(head) > 2:
            groups.insert(0, head[-2:])
            head = head[:-2]
        if head:
            groups.insert(0, head)
        whole = ",".join(groups) + "," + tail
    return "₹" + whole + "." + paise


@app.template_filter("daymonth")
def daymonth(value):
    when = datetime.fromisoformat(value)
    return "{} {}".format(when.day, when.strftime("%b"))


# ------------------------------------------------------------------ #
# Access control                                                      #
# ------------------------------------------------------------------ #

# @wraps keeps the wrapped view's __name__, which Flask uses as the
# endpoint — without it url_for("profile") raises BuildError.
def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if not session.get("user_id"):
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped_view


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if session.get("user_id"):
        return redirect(url_for("landing"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not name or not email or not password or not confirm_password:
            return render_template("register.html", error="All fields are required.")

        if len(password) < 8:
            return render_template("register.html", error="Password must be at least 8 characters.")

        if password != confirm_password:
            return render_template("register.html", error="Passwords do not match.")

        if create_user(name, email, password) is None:
            return render_template("register.html", error="That email is already registered.")

        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("landing"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or not password:
            return render_template("login.html", error="All fields are required.", email=email)

        user = get_user_by_email(email)

        if user is None or not check_password_hash(user["password_hash"], password):
            return render_template("login.html", error="Incorrect email or password.", email=email)

        session.clear()
        session["user_id"] = user["id"]
        session["user_name"] = user["name"]

        return redirect(url_for("dashboard"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("landing"))


@app.route("/dashboard")
@login_required
def dashboard():
    user_id = session["user_id"]
    today = date.today()

    summary = get_expense_summary(user_id)
    this_month = get_month_total(user_id, today.strftime("%Y-%m"))
    categories = get_category_totals(user_id)
    recent = get_recent_expenses(user_id, 6)

    return render_template(
        "dashboard.html",
        summary=summary,
        this_month=this_month,
        categories=categories,
        recent=recent,
        month_label=today.strftime("%B %Y"),
        icons=CATEGORY_ICONS,
    )


# @app.route must stay the outer decorator — inverted, Flask registers the
# unguarded view and the login check silently never runs.
@app.route("/profile")
@login_required
def profile():
    user = get_user_by_id(session["user_id"])

    if user is None:
        session.clear()
        return redirect(url_for("login"))

    member_since = datetime.fromisoformat(user["created_at"]).strftime("%B %Y")

    return render_template("profile.html", user=user, member_since=member_since)


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/expenses/add")
def add_expense():
    return "Add expense — coming in Step 7"


@app.route("/expenses/<int:id>/edit")
def edit_expense(id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
def delete_expense(id):
    return "Delete expense — coming in Step 9"


if __name__ == "__main__":
    app.run(debug=True, port=5001)
