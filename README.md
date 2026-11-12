# Miserly — beginner Flask project

A small registration, login, and logout app for our business tracker. The dashboard is a placeholder for the team's other features.

## Run it

In the VS Code terminal, from this project folder:

```powershell
.\.venv\Scripts\python.exe main.py
```

Open **http://127.0.0.1:5000** in your browser. Keep the terminal running; press **Ctrl+C** to stop it. If the previous version is running, stop it and start again to see the rewrite.

A teammate setting it up for the first time can run:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

## Understand it

- `main.py`: commented Python functions for registration, login, and logout.
- `templates/`: three separate HTML pages: `register.html`, `login.html`, and `dashboard.html`.
- `static/style.css`: a short green stylesheet shared by the pages.
- `instance/miserly.sqlite`: automatically created database; existing accounts still work.
- `requirements.txt`: the Flask package requirement.
- [Short learning guide](docs/learning-guide.md): basic syntax, how the app works, and a lecturer explanation.

The app uses a fresh random signing key each time it starts: restarting signs you out, but keeps your registered account. The older `instance/secret_key` file, if present, is no longer used.

## Try these checks

1. Open `/dashboard` before logging in. You should return to login.
2. Register with mismatching passwords. You should see an error.
3. Register a valid account with a password of 8–128 characters.
4. Try registering the same email again. It should be rejected.
5. Log in with a wrong password, then the correct one.
6. Check your name appears on the dashboard.
7. Click **Log out**, then open `/dashboard` again. You should return to login.
8. Restart the app and log in again. Your account should still exist.

This is a local classroom demo. Passwords are hashed, SQL values use placeholders, and POST forms include a CSRF token. Email checks are basic; email verification, password reset, and public deployment are outside this small version.
