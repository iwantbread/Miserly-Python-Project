import os
import secrets
import sqlite3
from functools import wraps
from pathlib import Path

from flask import Flask, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(SECRET_KEY=os.environ.get('SECRET_KEY'),
                            DATABASE=str(Path(app.instance_path) / 'miserly.sqlite'),
                            SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE='Lax',
                            MAX_CONTENT_LENGTH=16384)
    app.config.update(test_config or {})
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    if not app.config['SECRET_KEY']:
        key = Path(app.instance_path) / 'secret_key'
        try:
            with key.open('x') as file:
                file.write(secrets.token_hex(32))
        except FileExistsError:
            pass
        app.config['SECRET_KEY'] = key.read_text()

    def db():
        if 'db' not in g:
            g.db = sqlite3.connect(app.config['DATABASE'])
            g.db.row_factory = sqlite3.Row
        return g.db

    @app.teardown_appcontext
    def close_db(error=None):
        connection = g.pop('db', None)
        if connection is not None:
            connection.close()

    with app.app_context():
        db().execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT NOT NULL, email TEXT NOT NULL UNIQUE, password_hash TEXT NOT NULL)')
        db().commit()

    def csrf_token():
        if 'csrf_token' not in session:
            session['csrf_token'] = secrets.token_hex(32)
        return session['csrf_token']

    app.jinja_env.globals['csrf_token'] = csrf_token

    @app.before_request
    def load_user():
        g.user = db().execute('SELECT id, name, email FROM users WHERE id = ?', (session.get('user_id'),)).fetchone()
        if request.method == 'POST':
            token = session.get('csrf_token')
            if not token or not secrets.compare_digest(token, request.form.get('csrf_token', '')):
                return render_template('error.html'), 400

    def login_required(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if g.user is None:
                return redirect(url_for('login'))
            return view(*args, **kwargs)
        return wrapped

    @app.route('/')
    def index():
        return redirect(url_for('dashboard' if g.user else 'login'))

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if g.user:
            return redirect(url_for('dashboard'))
        if request.method == 'POST':
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '')
            error = None
            if not name or len(name) > 80:
                error = 'Enter your name (up to 80 characters).'
            elif len(email) > 254 or email.count('@') != 1 or not all(email.split('@')) or '.' not in email.split('@')[-1] or any(c.isspace() for c in email):
                error = 'Enter a valid email address.'
            elif not 8 <= len(password) <= 128:
                error = 'Use a password between 8 and 128 characters.'
            elif password != request.form.get('confirm_password'):
                error = 'Your passwords do not match.'
            if error is None:
                try:
                    db().execute('INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)', (name, email, generate_password_hash(password)))
                    db().commit()
                except sqlite3.IntegrityError:
                    error = 'An account with this email already exists. Please log in.'
                else:
                    flash('Account created! Log in to get started.', 'success')
                    return redirect(url_for('login'))
            flash(error, 'error')
        return render_template('auth.html', registering=True)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if g.user:
            return redirect(url_for('dashboard'))
        if request.method == 'POST':
            user = db().execute('SELECT * FROM users WHERE email = ?', (request.form.get('email', '').strip().lower(),)).fetchone()
            password = request.form.get('password', '')
            if user and len(password) <= 128 and check_password_hash(user['password_hash'], password):
                session.clear()
                session['user_id'] = user['id']
                return redirect(url_for('dashboard'))
            flash('Email or password is incorrect.', 'error')
        return render_template('auth.html', registering=False)

    @app.route('/dashboard')
    @login_required
    def dashboard():
        return render_template('dashboard.html')

    @app.route('/logout', methods=['POST'])
    @login_required
    def logout():
        session.clear()
        flash('You have been logged out.', 'success')
        return redirect(url_for('login'))

    return app


if __name__ == '__main__':
    create_app().run(debug=os.environ.get('FLASK_DEBUG') == '1')
