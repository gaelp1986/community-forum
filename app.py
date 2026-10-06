import os
import sqlite3

from flask import Flask, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.environ.get("DATABASE_PATH", os.path.join(BASE_DIR, "forum.db"))

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")

# Each user may make at most POST_LIMIT posts in any POST_WINDOW_MINUTES.
POST_LIMIT = 5
POST_WINDOW_MINUTES = 10


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(DATABASE)
    with open(os.path.join(BASE_DIR, "schema.sql")) as f:
        db.executescript(f.read())
    db.close()


init_db()


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        if not username or not password:
            return render_template("register.html", error="Username and password are required.")

        db = get_db()
        existing = db.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
        if existing:
            return render_template("register.html", error="That username is already taken.")

        password_hash = generate_password_hash(password)
        db.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, password_hash),
        )
        db.commit()
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]

        db = get_db()
        user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        if user is None or not check_password_hash(user["password_hash"], password):
            return render_template("login.html", error="Invalid username or password.")

        session["user_id"] = user["id"]
        session["username"] = user["username"]
        return redirect(url_for("index"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/", methods=["GET", "POST"])
def index():
    db = get_db()
    error = None
    draft = ""

    if request.method == "POST":
        if "user_id" not in session:
            return redirect(url_for("login"))
        content = request.form["content"].strip()
        recent = db.execute(
            """
            SELECT COUNT(*) FROM posts
            WHERE user_id = ? AND created_at > datetime('now', ?)
            """,
            (session["user_id"], f"-{POST_WINDOW_MINUTES} minutes"),
        ).fetchone()[0]
        if recent >= POST_LIMIT:
            error = (
                f"You can post up to {POST_LIMIT} times every "
                f"{POST_WINDOW_MINUTES} minutes. Try again in a few minutes."
            )
            draft = content
        else:
            if content:
                db.execute(
                    "INSERT INTO posts (user_id, content) VALUES (?, ?)",
                    (session["user_id"], content),
                )
                db.commit()
            return redirect(url_for("index"))

    posts = db.execute(
        """
        SELECT posts.id, posts.content, posts.created_at, users.username
        FROM posts
        JOIN users ON posts.user_id = users.id
        ORDER BY posts.created_at DESC
        """
    ).fetchall()

    return render_template(
        "index.html",
        posts=posts,
        username=session.get("username"),
        error=error,
        draft=draft,
    )


if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")
