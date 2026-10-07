# The Stoop
[![tests](https://github.com/gaelp1986/community-forum/actions/workflows/tests.yml/badge.svg)](https://github.com/gaelp1986/community-forum/actions/workflows/tests.yml)

A full-stack community discussion forum with user authentication — Flask, SQLite, HTML/CSS.

**Live:** https://gaelp2807.pythonanywhere.com

## Features
- User registration & login with salted password hashing (werkzeug)
- Sessions stored in signed cookies
- Post feed with author attribution (SQL JOIN across users/posts)
- Public read-only feed; posting requires an account
- Per-user rate limit on posting (5 posts per 10 minutes)

## Auth design
Passwords are never stored — only salted hashes. Login re-hashes the
attempt and compares. The session lives in a cookie signed with the
app's secret key, so users can read it but can't forge or alter it.
Post authorship comes from the signed session, never from form data.

## Run locally
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
FLASK_DEBUG=1 python app.py
```
Then visit http://localhost:5000

## Tests
```
pytest
```
The suite covers registration, login/logout, posting, HTML escaping,
the post length limit and the per-user rate limit. Each test gets a
fresh SQLite database through the `create_app` factory. GitHub Actions
runs it on every push and pull request.

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
gunicorn "app:create_app()"
```
SQLite needs a persistent disk. PythonAnywhere keeps files between
restarts. Render's free tier wipes the disk on each deploy, so use a
persistent disk or a different database there.

## Built with
Python (Flask), SQL (SQLite), HTML and CSS. AI-accelerated scaffolding
with human-owned auth and data logic.

Originally built at All Star Code (2023); rebuilt with real
authentication and a relational database, 2026.
