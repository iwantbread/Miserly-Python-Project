"""Database tools for the spending app.

Import this package and use what is listed in __all__. See README.md for the rules.
"""
from .connection import get_connection
from .errors import DuplicateError, ValidationError
from .purchases import (
    add_purchase,
    delete_purchase,
    fetch_purchases,
    monthly_totals,
    update_purchase,
)
from .schema import create_tables
from .users import (
    delete_user,
    fetch_all_users,
    fetch_user,
    get_user,
    register_user,
    update_user,
)
from .validation import (
    parse_amount_to_cents,
    validate_age,
    validate_date,
    validate_email,
    validate_item,
    validate_name,
)

__all__ = [
    "get_connection", "create_tables",
    "ValidationError", "DuplicateError",
    "register_user", "get_user", "fetch_user", "fetch_all_users", "update_user", "delete_user",
    "add_purchase", "fetch_purchases", "update_purchase", "delete_purchase", "monthly_totals",
    "validate_name", "validate_age", "validate_email", "validate_item",
    "parse_amount_to_cents", "validate_date",
]