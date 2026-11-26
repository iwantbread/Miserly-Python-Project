from .validation import parse_amount_to_cents, validate_date, validate_item

SCHEMA = [
    """
    CREATE TABLE IF NOT EXISTS purchases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        item TEXT NOT NULL,
        amount_cents INTEGER NOT NULL,
        purchased_on TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_purchases_user_date ON purchases (user_id, purchased_on)",
]


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