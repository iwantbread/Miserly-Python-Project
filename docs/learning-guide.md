# Start here: the small Flask project

Read `main.py` beside this guide. Its comments explain the code in small steps. You do not need to understand Flask's own source code or memorise every library detail.

## What you built

This is the account part of a business tracker: registration, login, logout, and a protected dashboard. Business tracking features come later.

The browser displays **HTML** for content and **CSS** for appearance. **Python** runs on your computer as the server. **Flask** is a Python library that receives browser requests, calls your Python functions, and sends responses back.

Opening a page normally sends **GET**. Submitting these forms sends **POST**, including the named input values.

## The files

- `main.py`: starts Flask, handles requests, checks forms, and reads or saves accounts.
- `templates/register.html`: registration form.
- `templates/login.html`: login form.
- `templates/dashboard.html`: greeting and logout button.
- `static/style.css`: colours, spacing, inputs, and buttons.
- `requirements.txt`: tells pip which Flask versions to install.
- `README.md`: launching instructions and manual checks.
- `.gitignore`: tells Git to ignore generated files and local data.
- `docs/learning-guide.md`: this explanation.

Generated folders include `.venv/` (Python and installed packages), `__pycache__/` (Python's cache), and `instance/` (the database). `.git/` holds version history.

## Connect an address to Python

```python
@app.route('/login', methods=['GET', 'POST'])
def login():
```

The `@app.route(...)` line tells Flask: “Use the function below for this address.” `def` defines a function, which is a named set of instructions.

| Address | Function | Purpose |
| --- | --- | --- |
| `/register` | `register()` | Show or process registration. |
| `/login` | `login()` | Show or process login. |
| `/` and `/dashboard` | `dashboard()` | Show the dashboard if logged in. |
| `/logout` | `logout()` | Accept a POST and log out. |

`render_template('login.html', error=error)` builds HTML from that file, passing in an error message. `{{ error }}` inserts its value; `{% if error %}` displays something conditionally. This template language is Jinja.

`redirect('/login')` tells the browser to request that address next.

## Registration, step by step

1. GET shows the registration form.
2. POST sends its values. `request.form.get('email', '')` reads the input named `email`, or returns an empty string if missing.
3. `.strip()` removes surrounding spaces; `.lower()` lowercases the email. Passwords are left unchanged.
4. Conditions check name length, basic email format, password length, and matching confirmation.
5. `generate_password_hash(password)` makes a salted password hash: a representation used for checking passwords later. It is not reversible password encryption.
6. SQLite saves the name, email, and hash. A unique email rule prevents duplicates.
7. Success redirects to login; failure renders the form with an error.

## Reading and saving accounts

SQLite is a database stored in `instance/miserly.sqlite`. One row in its `users` table represents one account: `id`, `name`, `email`, and `password_hash`.

`get_database()` opens it and ensures the table exists. `execute()` runs SQL, `commit()` saves an insert, and `close()` closes the connection.

```python
'SELECT * FROM users WHERE email = ?', (email,)
```

The `?` receives the email separately, keeping input out of SQL instructions. `(email,)` is a one-item tuple: the comma matters. `fetchone()` returns a matching row or `None` when none exists.

## Login and logout

Login finds the email's account and calls `check_password_hash(stored_hash, entered_password)`. Wrong details show an error.

Correct details clear old session data, then store `user_id` and `name`. The dashboard checks for `user_id`; without it, the browser returns to login.

`session` remembers information between requests using a **signed browser cookie**. Signing detects changes; it does not encrypt the contents. No password goes into this cookie.

Logout calls `session.clear()` and redirects to login.

The app generates a new signing key at startup. Restarting signs everyone out, but accounts remain in SQLite. Any older `instance/secret_key` file is unused by this version.

## One form protection helper

`check_form()` runs before each request. It creates a random `form_token` in the session. Forms send it back in a hidden input; POST requests with missing or different tokens are rejected. This is CSRF protection, helping prevent another website from submitting actions through your browser.

## Python syntax to recognise

| Syntax | Meaning |
| --- | --- |
| `=` / `==` / `!=` | Assign / compare equal / compare different. |
| `if`, `elif`, `else` | Choose which instructions run. |
| `len(password)` | Count its characters. |
| `user is None` | Check that no row was found. |
| `return` | Finish a function and send back its result. |
| `try` / `except` | Attempt something and handle a specified error, such as duplicate email. |
| `# comment` | Explanation Python ignores. |

Indentation groups instructions. `or` means either condition can be true.

## Four sentences for your lecturer

“I used Flask to connect web addresses to Python functions. Registration validates inputs and stores a password hash in SQLite. Login checks that hash and remembers the account through a signed session cookie. Logout clears the session, and the dashboard rejects requests without a login.”

This is a local learning app: email checking is basic, and password reset, email verification, rate limiting, and production deployment are additional work.
