import functools, json

from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash

from api.db import get_db

# defines the first chunk of the URL after localhost
# helps us organize our endpoints
# this one specifies that its endpoints will follow the form localhost:5000/auth/[more stuff]
bp = Blueprint("auth", __name__, url_prefix="/auth")


# localhost:5000/auth/login
# first line associates the URL /login with the login function
# the user submitted a login form, so the method will be POST
@bp.route("/login", methods=["GET, POST"])
def login():
    if request.method == "POST":
        # request.form is a kind of dict mapping with form keys and values
        username = request.form["username"]
        password = request.form["password"]
        db = get_db()
        error = None

        # execute does an SQL query
        # fetchone returns one row, as opposed to fetchall which fetches the first matching row
        user = db.execute(
            "SELECT * FROM user WHERE username = ?", (username,)
        ).fetchone()

        if user is None:
            error = "Incorrect username."
        elif not check_password_hash(user["password"], password):
            error = "Incorrect password."

        if error is None:
            session.clear()
            session["user_id"] = user["id"]
            return redirect(url_for("home"))

        flash(error)

        return json.dumps({"type": "SIGNIN"})


# localhost:5000/auth/register
@bp.route("/register", methods=("GET", "POST"))
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        db = get_db()
        error = None

        if not username:
            error = "Username is required."
        elif not password:
            error = "Password is required."

        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
                db.commit()
            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                return json.dumps({"success": username})
        # if we don't end up being able to register, return the error
        return json.dumps({"error": error})