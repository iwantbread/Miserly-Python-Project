# DatabaseModule

Database tools for the spending app. Import the package and call its functions.

```python
from contextlib import closing
import DatabaseModule as db

with closing(db.get_connection("SpendingApp.db")) as conn:
    db.create_tables(conn)
    user_id = db.register_user(conn, "Aoife", "Murphy", 29, "aoife@example.com")
    db.add_purchase(conn, user_id, "Groceries", "42.50")
    print(db.fetch_purchases(conn, user_id))
```

## Rules of the module

- Every function takes an open connection as its first argument. The module never opens
  its own connection, never prints, and never asks for input.
- Open one connection per request or task. Don't share a connection between threads.
- Bad input raises `ValidationError`. A taken email raises `DuplicateError`.
  Both are subclasses of `ValueError`.
- Functions return dicts (or lists of dicts) and IDs as ints. Update and delete functions
  return `True` if a row was changed and `False` if nothing matched.
- Money goes in as a string in euros (`"12.50"`) and is stored and returned as integer cents.
- Purchase functions always take `user_id`, and only touch that user's rows. Take the ID
  from the logged-in session, never from a form or request.
- `fetch_user` and `fetch_all_users` are for admin use only. This module does not check permissions.
- Passwords and login are not handled here.

## Adding a new table

1. Create `DatabaseModule/yourthing.py` with a `SCHEMA` list of SQL statements and your functions.
2. Add the module to `MODULES` in `schema.py` (tables that others refer to come first).
3. Export the public functions in `__init__.py` and `__all__`.