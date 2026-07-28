import sqlite3
from flask import Flask, g

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


@app.route("/")
def hello():
    return "Community Forum — coming soon."


if __name__ == "__main__":
    import os

    if not os.path.exists(DATABASE):
        init_db()
    app.run(debug=True)
