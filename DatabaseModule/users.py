import sqlite3

from .errors import DuplicateError
from .validation import validate_age, validate_email, validate_name

SCHEMA = [
    """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        foreName TEXT NOT NULL,
        surName TEXT NOT NULL,
        age INTEGER NOT NULL,
        email TEXT UNIQUE NOT NULL COLLATE NOCASE
    )
    """,
]

PUBLIC_USER_COLUMNS = "id, foreName, surName, age, email"


def register_user(connection, foreName, surName, age, email) -> int:
    """Create a user and return the new user's ID."""
    values = (
        validate_name(foreName, "first name"),
        validate_name(surName, "second name"),
        validate_age(age),
        validate_email(email),
    )
    query = "INSERT INTO users (foreName, surName, age, email) VALUES (?, ?, ?, ?)"
    try:
        with connection:
            return connection.execute(query, values).lastrowid
    except sqlite3.IntegrityError:
        raise DuplicateError("an account with that email already exists")


def get_user(connection, user_id: int):
    row = connection.execute(
        f"SELECT {PUBLIC_USER_COLUMNS} FROM users WHERE id = ?", (user_id,)
    ).fetchone()
    return dict(row) if row else None


def fetch_user(connection, **criteria) -> list[dict]:
    """Search by id, foreName, surName and/or email. Intended for admin use only."""
    allowed = {"id", "foreName", "surName", "email"}
    nocase = {"foreName", "surName", "email"}

    if not criteria:
        raise ValueError("Provide at least one field to search by")

    clauses, params = [], []
    for field, value in criteria.items():
        if field not in allowed:
            raise ValueError(f"Cannot search by '{field}'")
        if field in nocase:
            clauses.append(f"{field} = ? COLLATE NOCASE")
            value = str(value).strip()
        else:
            clauses.append(f"{field} = ?")
        params.append(value)

    query = f"SELECT {PUBLIC_USER_COLUMNS} FROM users WHERE " + " AND ".join(clauses)
    return [dict(row) for row in connection.execute(query, params).fetchall()]


def fetch_all_users(connection) -> list[dict]:
    """Admin use only."""
    rows = connection.execute(f"SELECT {PUBLIC_USER_COLUMNS} FROM users").fetchall()
    return [dict(row) for row in rows]


def update_user(connection, user_id: int, **changes) -> bool:
    """Change chosen fields of one user. Returns False if the user doesn't exist."""
    validators = {
        "foreName": lambda v: validate_name(v, "first name"),
        "surName": lambda v: validate_name(v, "second name"),
        "age": validate_age,
        "email": validate_email,
    }
    if not changes:
        raise ValueError("Provide at least one field to update")

    clauses, params = [], []
    for field, value in changes.items():
        if field not in validators:
            raise ValueError(f"Cannot update '{field}'")
        clauses.append(f"{field} = ?")
        params.append(validators[field](value))
    params.append(user_id)

    query = "UPDATE users SET " + ", ".join(clauses) + " WHERE id = ?"
    try:
        with connection:
            return connection.execute(query, params).rowcount > 0
    except sqlite3.IntegrityError:
        raise DuplicateError("that email is already used by another account")


def delete_user(connection, user_id: int) -> bool:
    """Delete a user and, through the foreign key, all of their purchases."""
    with connection:
        return connection.execute("DELETE FROM users WHERE id = ?", (user_id,)).rowcount > 0