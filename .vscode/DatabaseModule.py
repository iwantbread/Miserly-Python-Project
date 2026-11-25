import re
import sqlite3
from datetime import date
from decimal import Decimal, InvalidOperation

MIN_AGE = 0
MAX_AGE = 120
MAX_AMOUNT_CENTS = 100_000_000  # 1,000,000.00


# ---------- Errors ----------
class ValidationError(ValueError):
    """The input failed validation."""


class DuplicateError(ValueError):
    """A unique value (such as an email) is already in use."""


# ---------- Validation ----------
NAME_PATTERN = re.compile(r"^[^\W\d_]+(?:['-][^\W\d_]+)*$")
EMAIL_PATTERN = re.compile(
    r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}$"
)


def validate_name(raw, label="name") -> str:
    name = str(raw).strip()
    if not name:
        raise ValidationError(f"{label} cannot be empty")
    if len(name) > 50 or not NAME_PATTERN.match(name):
        raise ValidationError(f"{label} may only contain letters, hyphens and apostrophes")
    return name.title()


def validate_age(raw) -> int:
    try:
        age = int(str(raw).strip())
    except ValueError:
        raise ValidationError("age must be a whole number")
    if not MIN_AGE <= age <= MAX_AGE:
        raise ValidationError(f"age must be between {MIN_AGE} and {MAX_AGE}")
    return age


def validate_email(raw) -> str:
    email = str(raw).strip().lower()
    if len(email) > 254 or not EMAIL_PATTERN.match(email):
        raise ValidationError("email must look like name@example.com")
    return email


def validate_item(raw) -> str:
    item = str(raw).strip()
    if not item or len(item) > 100:
        raise ValidationError("item must be between 1 and 100 characters")
    return item


def parse_amount_to_cents(raw) -> int:
    """Turn what the user typed ('12.50') into whole cents (1250)."""
    try:
        amount = Decimal(str(raw).strip())
    except InvalidOperation:
        raise ValidationError("amount must be a number like 12.50")
    if not amount.is_finite() or not Decimal("0") < amount <= Decimal(MAX_AMOUNT_CENTS) / 100:
        raise ValidationError("amount must be greater than 0 and not unreasonably large")
    if amount != amount.quantize(Decimal("0.01")):
        raise ValidationError("amount can have at most 2 decimal places")
    return int(amount * 100)


def validate_date(raw) -> str:
    """Return an ISO date string (YYYY-MM-DD). Blank means today."""
    if raw is None or str(raw).strip() == "":
        return date.today().isoformat()
    try:
        return date.fromisoformat(str(raw).strip()).isoformat()
    except ValueError:
        raise ValidationError("date must look like 2026-11-25")


# ---------- Connection and schema ----------
def get_connection(db_name):
    connection = sqlite3.connect(db_name)
    connection.row_factory = sqlite3.Row  # rows can be turned into dicts
    connection.execute("PRAGMA foreign_keys = ON")  # needed on every connection
    return connection


def create_tables(connection):
    with connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                foreName TEXT NOT NULL,
                surName TEXT NOT NULL,
                age INTEGER NOT NULL,
                email TEXT UNIQUE NOT NULL COLLATE NOCASE
            )
        """)
        connection.execute("""
            CREATE TABLE IF NOT EXISTS purchases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                item TEXT NOT NULL,
                amount_cents INTEGER NOT NULL,
                purchased_on TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_purchases_user_date "
            "ON purchases (user_id, purchased_on)"
        )


# ---------- Users ----------
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


# ---------- Purchases (always scoped to one user) ----------
def add_purchase(connection, user_id: int, item, amount, purchased_on=None) -> int:
    """`amount` is what the user typed in euros, e.g. '12.50'. Stored as cents."""
    values = (
        user_id,
        validate_item(item),
        parse_amount_to_cents(amount),
        validate_date(purchased_on),
    )
    query = (
        "INSERT INTO purchases (user_id, item, amount_cents, purchased_on) "
        "VALUES (?, ?, ?, ?)"
    )
    with connection:
        return connection.execute(query, values).lastrowid


def fetch_purchases(connection, user_id: int) -> list[dict]:
    rows = connection.execute(
        "SELECT id, item, amount_cents, purchased_on FROM purchases "
        "WHERE user_id = ? ORDER BY purchased_on DESC, id DESC",
        (user_id,),
    ).fetchall()
    return [dict(row) for row in rows]


def update_purchase(connection, user_id: int, purchase_id: int, **changes) -> bool:
    """Change chosen parts of one of this user's purchases."""
    converters = {
        "item": ("item", validate_item),
        "amount": ("amount_cents", parse_amount_to_cents),
        "purchased_on": ("purchased_on", validate_date),
    }
    if not changes:
        raise ValueError("Provide at least one field to update")

    clauses, params = [], []
    for field, value in changes.items():
        if field not in converters:
            raise ValueError(f"Cannot update '{field}'")
        column, convert = converters[field]
        clauses.append(f"{column} = ?")
        params.append(convert(value))
    params += [purchase_id, user_id]

    query = "UPDATE purchases SET " + ", ".join(clauses) + " WHERE id = ? AND user_id = ?"
    with connection:
        return connection.execute(query, params).rowcount > 0


def delete_purchase(connection, user_id: int, purchase_id: int) -> bool:
    with connection:
        return connection.execute(
            "DELETE FROM purchases WHERE id = ? AND user_id = ?",
            (purchase_id, user_id),
        ).rowcount > 0


def monthly_totals(connection, user_id: int) -> list[dict]:
    rows = connection.execute(
        "SELECT strftime('%Y-%m', purchased_on) AS month, SUM(amount_cents) AS total_cents "
        "FROM purchases WHERE user_id = ? GROUP BY month ORDER BY month",
        (user_id,),
    ).fetchall()
    return [dict(row) for row in rows]