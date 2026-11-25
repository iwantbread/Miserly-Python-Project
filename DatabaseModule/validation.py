import re
from datetime import date
from decimal import Decimal, InvalidOperation

from .errors import ValidationError

MIN_AGE = 0
MAX_AGE = 120
MAX_AMOUNT_CENTS = 100_000_000  # 1,000,000.00

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