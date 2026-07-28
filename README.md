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
pip install flask
python app.py
```
Then visit http://localhost:5000

## Built with
Python,SQL,HTML
 — AI-accelerated scaffolding with
human-owned auth and data logic.

Originally built at All Star Code (2023); rebuilt with real
authentication and a relational database, 2026.
