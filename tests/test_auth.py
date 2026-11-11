import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

from main import create_app


class AuthenticationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.database = str(Path(self.temp.name) / 'test.sqlite')
        self.app = create_app({'TESTING': True, 'SECRET_KEY': 'test', 'DATABASE': self.database})
        self.client = self.app.test_client()

    def tearDown(self):
        self.temp.cleanup()

    def post(self, path, **data):
        self.client.get('/dashboard' if path == '/logout' else path)
        with self.client.session_transaction() as session:
            token = session['csrf_token']
        return self.client.post(path, data={'csrf_token': token, **data})

    def register(self, **changes):
        data = dict(name='Test User', email='user@example.com', password='password123', confirm_password='password123')
        data.update(changes)
        return self.post('/register', **data)

    def test_registration_login_logout(self):
        self.assertEqual(self.client.get('/dashboard').location, '/login')
        self.assertEqual(self.register().location, '/login')
        with closing(sqlite3.connect(self.database)) as db:
            self.assertNotEqual(db.execute('SELECT password_hash FROM users').fetchone()[0], 'password123')
        self.assertEqual(self.post('/login', email='USER@example.com', password='password123').location, '/dashboard')
        self.assertIn('Test User', self.client.get('/dashboard').text)
        self.assertEqual(self.client.get('/logout').status_code, 405)
        self.assertEqual(self.post('/logout').location, '/login')
        self.assertEqual(self.client.get('/dashboard').location, '/login')

    def test_validation_and_duplicates(self):
        for changes in ({'name': ''}, {'email': 'invalid'}, {'password': 'short'}, {'confirm_password': 'different'}):
            self.assertEqual(self.register(**changes).status_code, 200)
        self.register()
        self.assertIn('already exists', self.register(email='USER@example.com').text)
        with closing(sqlite3.connect(self.database)) as db:
            self.assertEqual(db.execute('SELECT COUNT(*) FROM users').fetchone()[0], 1)

    def test_invalid_credentials(self):
        self.register()
        for email, password in (('user@example.com', 'wrong'), ('missing@example.com', 'password123'), ("' OR 1=1 --", 'password123')):
            self.assertIn('Email or password is incorrect', self.post('/login', email=email, password=password).text)
            self.assertEqual(self.client.get('/dashboard').location, '/login')

    def test_csrf_required(self):
        self.assertEqual(self.client.post('/register', data={}).status_code, 400)
        self.assertEqual(self.client.post('/login', data={'csrf_token': 'wrong'}).status_code, 400)

    def test_user_content_escaped(self):
        self.register(name='<script>alert(1)</script>')
        self.post('/login', email='user@example.com', password='password123')
        page = self.client.get('/dashboard').text
        self.assertNotIn('<script>', page)
        self.assertIn('&lt;script&gt;', page)


if __name__ == '__main__':
    unittest.main()
