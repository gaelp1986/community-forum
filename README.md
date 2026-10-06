# Community Discussion Forum
Full-stack forum with user authentication — Flask, SQLite, vanilla JS/HTML/CSS.

## Features
- User registration & login with salted password hashing (werkzeug)
- Server-side sessions via signed cookies
- Post feed with author attribution (SQL JOIN across users/posts)

## Auth design
Passwords are never stored — only salted hashes. Login re-hashes the
attempt and compares. Session cookies are signed, so they can be read
but not forged. Post authorship comes from the session, not the client.

## Run locally
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
FLASK_DEBUG=1 python app.py
```
Then visit http://localhost:5000

## Deploy
The app reads its configuration from environment variables:

| Variable | Purpose |
|---|---|
| `SECRET_KEY` | **Required in production.** Signs session cookies. Generate one with `python -c "import secrets; print(secrets.token_hex(32))"` |
| `DATABASE_PATH` | Optional. Where the SQLite file lives (defaults to `forum.db` next to `app.py`) |
| `FLASK_DEBUG` | Set to `1` only for local development |

Tables are created automatically on startup. In production, run with
gunicorn instead of `python app.py`:
```
gunicorn app:app
```
SQLite needs a persistent disk. PythonAnywhere keeps files between
restarts. Render's free tier wipes the disk on each deploy, so use a
persistent disk or a different database there.

## Built with
Python, SQL, HTML
 — AI-accelerated scaffolding with
human-owned auth and data logic.

Originally built at All Star Code (2023); rebuilt with real
authentication and a relational database, 2026.
