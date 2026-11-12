import secrets  # Makes random values for the session key and form tokens.
import sqlite3  # Lets Python read and write our small database.
from pathlib import Path  # Helps create file and folder paths.

from flask import Flask, redirect, render_template, request, session
# Ready-made password tools: we do not need to write a hashing algorithm.
from werkzeug.security import check_password_hash, generate_password_hash


# Create the website. Flask connects web addresses to the functions below.
app = Flask(__name__)
# This random key protects the login cookie. Restarting the app signs users out.
app.secret_key = secrets.token_hex(32)
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['MAX_CONTENT_LENGTH'] = 16384

# Keep the database in instance/, using the same file as the earlier version.
Path(app.instance_path).mkdir(exist_ok=True)
app.config['DATABASE'] = Path(app.instance_path) / 'miserly.sqlite'


def get_database():
    # Open the database. Row lets us use user['name'] instead of user[1].
    database = sqlite3.connect(app.config['DATABASE'])
    database.row_factory = sqlite3.Row
    # Each user has one row. SQLite supplies the id; UNIQUE prevents duplicate emails.
    database.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL
    )''')
    return database


@app.before_request
def check_form():
    # Run before each request. Give this browser a random form token.
    if 'form_token' not in session:
        session['form_token'] = secrets.token_hex(32)
    # Forms send the token back. Reject missing or different tokens (CSRF protection).
    if request.method == 'POST':
        if request.form.get('form_token') != session['form_token']:
            return 'Please go back, reload the page, and submit the form again.', 400


@app.route('/register', methods=['GET', 'POST'])
def register():
    # GET shows the form. POST means the user clicked its submit button.
    error = ''
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirmation = request.form.get('confirm_password', '')

        # Check one rule at a time. Never strip or lowercase a password.
        if name == '' or len(name) > 80:
            error = 'Enter your name (up to 80 characters).'
        elif '@' not in email or '.' not in email or len(email) > 254:
            error = 'Enter a valid email address.'
        elif len(password) < 8 or len(password) > 128:
            error = 'Use a password between 8 and 128 characters.'
        elif password != confirmation:
            error = 'Your passwords do not match.'
        else:
            database = get_database()
            # Hash the password so the database never stores the original text.
            password_hash = generate_password_hash(password)
            try:
                # The ? marks receive values separately, keeping them out of SQL code.
                database.execute(
                    'INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)',
                    (name, email, password_hash)
                )
                database.commit()  # Save the new account.
            except sqlite3.IntegrityError:
                error = 'That email is already registered. Please log in.'
            database.close()

            if error == '':
                return redirect('/login')

    # Pass the error text to HTML. An empty string means there is no error to show.
    return render_template('register.html', error=error)


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = ''
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        database = get_database()
        # fetchone() gives us one user, or None if this email was not found.
        user = database.execute(
            'SELECT * FROM users WHERE email = ?', (email,)
        ).fetchone()
        database.close()

        if user is None:
            error = 'Email or password is incorrect.'
        elif len(password) > 128:
            error = 'Email or password is incorrect.'
        elif check_password_hash(user['password_hash'], password):
            # The session remembers this browser's login between page requests.
            session.clear()
            session['user_id'] = user['id']
            session['name'] = user['name']
            return redirect('/dashboard')
        else:
            error = 'Email or password is incorrect.'

    return render_template('login.html', error=error)


@app.route('/')
@app.route('/dashboard')
def dashboard():
    # Both addresses show this page. Only a logged-in browser can open it.
    if 'user_id' not in session:
        return redirect('/login')
    return render_template('dashboard.html', name=session['name'])


@app.route('/logout', methods=['POST'])
def logout():
    session.clear()  # Forget the login, then return to the login form.
    return redirect('/login')


# Start the local server only when running this file directly.
if __name__ == '__main__':
    app.run()
