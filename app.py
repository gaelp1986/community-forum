import sqlite3
from flask import Flask, g, redirect, render_template, request, url_for
from werkzeug.security import generate_password_hash

DATABASE = "forum.db"

app = Flask(__name__)
app.secret_key = "dev-secret-key-change-me"


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
    with open("schema.sql") as f:
        db.executescript(f.read())
    db.close()


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
        return redirect(url_for("register"))

    return render_template("register.html")


@app.route("/")
def hello():
    return "Community Forum — coming soon."


if __name__ == "__main__":
    import os

    if not os.path.exists(DATABASE):
        init_db()
    app.run(debug=True)
