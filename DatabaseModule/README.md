# DatabaseModule

Functions for saving and reading users and their spending in a SQLite database (a single `.db` file).

```python
from contextlib import closing
import DatabaseModule as db

with closing(db.get_connection("example.db")) as conn:
    db.create_tables(conn)
    user_id = db.register_user(conn, "Aoife", "Murphy", 29, "aoife@example.com")
    db.add_purchase(conn, user_id, "Groceries", "42.50")
    print(db.fetch_purchases(conn, user_id))
```

Every function takes the connection (`conn`) as its first argument.

## Files

| File | What it does |
|------|--------------|
| `__init__.py` | Lists everything you can use. Import with `import DatabaseModule as db`. |
| `connection.py` | Opens the database file. |
| `schema.py` | Creates the tables. |
| `users.py` | User functions. |
| `purchases.py` | Spending functions. |
| `validation.py` | Checks input (email, age, names, amounts, dates). |
| `errors.py` | `ValidationError` and `DuplicateError`. |

## Setup

| Function | What it does | Returns |
|----------|--------------|---------|
| `get_connection(file)` | Opens (or creates) the database file | Connection |
| `create_tables(conn)` | Creates the tables if missing. Safe to call every time | Nothing |

## Users

| Function | What it does | Returns |
|----------|--------------|---------|
| `register_user(conn, foreName, surName, age, email)` | Adds a user | New user ID |
| `get_user(conn, user_id)` | Gets one user | Dict, or `None` |
| `update_user(conn, user_id, **changes)` | Changes `foreName`, `surName`, `age` and/or `email` | `True` / `False` |
| `delete_user(conn, user_id)` | Deletes a user and all their purchases | `True` / `False` |
| `fetch_user(conn, **search)` | Finds users by `id`, `foreName`, `surName` and/or `email` (admin only) | List of dicts |
| `fetch_all_users(conn)` | Lists all users (admin only) | List of dicts |

## Spending

| Function | What it does | Returns |
|----------|--------------|---------|
| `add_purchase(conn, user_id, item, amount, purchased_on=None)` | Adds a purchase. Date defaults to today | New purchase ID |
| `fetch_purchases(conn, user_id)` | Lists the user's purchases, newest first | List of dicts |
| `update_purchase(conn, user_id, purchase_id, **changes)` | Changes `item`, `amount` and/or `purchased_on` | `True` / `False` |
| `delete_purchase(conn, user_id, purchase_id)` | Deletes one purchase | `True` / `False` |
| `monthly_totals(conn, user_id)` | Totals spending per month | List of dicts |

`True` / `False` means a row was changed / nothing matched (wrong ID, or it belongs to another user). It is not an error.

## Data formats

- User: `{'id': 1, 'foreName': 'Aoife', 'surName': 'Murphy', 'age': 29, 'email': 'aoife@example.com'}`
- Purchase: `{'id': 1, 'item': 'Groceries', 'amount_cents': 4250, 'purchased_on': '2026-11-25'}`
- Monthly total: `{'month': '2026-11', 'total_cents': 4250}`
- Money goes in as euros (`"42.50"`) and comes out as cents (`4250`).
- Dates are `YYYY-MM-DD`.

## Errors

| Error | Raised when |
|-------|-------------|
| `ValidationError` | Input is invalid. The message says why. |
| `DuplicateError` | The email is already used. |

```python
try:
    db.register_user(conn, "Aoife", "Murphy", 29, "bad-email")
except db.ValidationError as e:
    print(e)
```

Input rules: names are letters only (hyphens and apostrophes allowed), up to 50 characters. Age is 0-120. Email must look like `name@example.com`. Item is 1-100 characters. Amount is above 0 with at most 2 decimals.

## Rules

1. Open one connection per task and close it (`with closing(...)`).
2. Take `user_id` from the logged-in user, never from something they typed.
3. `fetch_user` and `fetch_all_users` are admin only. The module doesn't check who calls them.
4. The module never prints or asks for input. It returns values or raises errors.
5. Passwords and login are handled elsewhere.

## Adding a table

1. Create `yourthing.py` with a `SCHEMA` list of SQL statements and your functions.
2. Add the module to `MODULES` in `schema.py`.
3. Export the functions in `__init__.py`.

Always pass values with `?` placeholders, never by building SQL strings.