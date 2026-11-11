# Miserly — Flask authentication

Registration, login, logout, and a protected dashboard for the team's business tracker. The supplied ZIP contains empty UI files, so this implementation uses a responsive green theme.

## Run locally (PowerShell)

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

Open http://127.0.0.1:5000, create an account, then log in. SQLite is created automatically in `instance/`. This directory also holds a local session signing key; keep it private and out of Git.

The virtual environment is already prepared in this workspace. You can start directly with `.\.venv\Scripts\python.exe main.py` without activating it.

## Team integration

`main.py` exposes `create_app()` and `/register`, `/login`, `/logout` (POST), and `/dashboard`. The dashboard is a placeholder for the rest of the business tracker. Follow its `@login_required` pattern to protect new routes; `g.user` contains the signed-in user's ID, name, and email. Scope future business records to `g.user['id']`.

Templates live in `templates/` and styles in `static/style.css`. Every POST form needs the hidden `csrf_token` field shown in the existing templates. Passwords are hashed with Werkzeug; SQL uses bound parameters. Logout clears the session. Password reset and email verification are not included.

For deployment, set a private, stable `SECRET_KEY` environment variable, use HTTPS and `SESSION_COOKIE_SECURE=True`, add login rate limiting, and use a production WSGI server. Debug mode is off unless `FLASK_DEBUG=1`.

Run tests with `python -m unittest discover -s tests -v`.

## Learn how it works

Start with [the Python and Flask learning guide](docs/learning-guide.md), then read [templates and styles](docs/templates-and-styles.md) and [tests and project files](docs/testing-and-project-files.md). These explain every application statement, template line, CSS rule, test, and supporting file, with beginner syntax examples and lecturer preparation.
