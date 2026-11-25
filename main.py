from contextlib import closing

import DatabaseModule as db
print(db)
DB_NAME = "SpendingApp.db"


def handle(action, *args, **kwargs):
    """Mimics one web request: open a connection, run the action, close it,
    and turn errors into HTTP-style status codes."""
    try:
        with closing(db.get_connection(DB_NAME)) as connection:
            return 200, action(connection, *args, **kwargs)
    except db.ValidationError as e:
        return 400, str(e)
    except db.DuplicateError as e:
        return 409, str(e)


# ---------- Small helpers ----------
def euros(cents: int) -> str:
    return f"{cents // 100}.{cents % 100:02d}"


def ask_int(prompt):
    try:
        return int(input(prompt).strip())
    except ValueError:
        print("Please enter a whole number.")
        return None


def load_purchases(user_id):
    _, purchases = handle(db.fetch_purchases, user_id)
    return purchases


def print_purchases(purchases):
    print(f"\n{'ID':<5}{'Date':<12}{'Item':<25}{'Amount':>10}")
    for p in purchases:
        print(f"{p['id']:<5}{p['purchased_on']:<12}{p['item'][:24]:<25}{euros(p['amount_cents']):>10}")
    total = sum(p["amount_cents"] for p in purchases)
    print(f"{'Total':<42}{euros(total):>10}")


# ---------- Before logging in ----------
def register():
    print("\n--- Register ---")
    foreName = input("First name: ")
    surName = input("Second name: ")
    age = input("Age: ")
    email = input("Email: ")
    status, body = handle(db.register_user, foreName, surName, age, email)
    if status == 200:
        print("Account created. You can now log in.")
    else:
        print(f"Could not register: {body}")


def log_in():
    """Stand-in for the real login, which another programmer is handling.
    It just finds the user by email. Replace this with proper authentication."""
    print("\n--- Log in ---")
    email = input("Email: ")
    status, matches = handle(db.fetch_user, email=email)
    if status != 200 or not matches:
        print("No account found with that email.")
        return None
    return matches[0]


# ---------- After logging in ----------
def add_spending(user_id):
    print("\n--- Add spending ---")
    item = input("What did you buy? ")
    amount = input("Amount (e.g. 12.50): ")
    purchased_on = input("Date YYYY-MM-DD (Enter for today): ")
    status, body = handle(db.add_purchase, user_id, item, amount, purchased_on)
    print("Spending added." if status == 200 else f"Could not add spending: {body}")


def view_spending(user_id):
    purchases = load_purchases(user_id)
    if not purchases:
        print("\nNo spending recorded yet.")
    else:
        print_purchases(purchases)


def edit_spending(user_id):
    purchases = load_purchases(user_id)
    if not purchases:
        print("\nNo spending recorded yet.")
        return
    print_purchases(purchases)
    purchase_id = ask_int("\nID of the entry to edit: ")
    if purchase_id is None:
        return

    print("Press Enter to keep the current value.")
    changes = {}
    item = input("New item: ").strip()
    if item:
        changes["item"] = item
    amount = input("New amount: ").strip()
    if amount:
        changes["amount"] = amount
    purchased_on = input("New date (YYYY-MM-DD): ").strip()
    if purchased_on:
        changes["purchased_on"] = purchased_on

    if not changes:
        print("No changes made.")
        return
    status, body = handle(db.update_purchase, user_id, purchase_id, **changes)
    if status != 200:
        print(f"Could not update: {body}")
    elif body:
        print("Entry updated.")
    else:
        print("No entry with that ID.")


def delete_spending(user_id):
    purchases = load_purchases(user_id)
    if not purchases:
        print("\nNo spending recorded yet.")
        return
    print_purchases(purchases)
    purchase_id = ask_int("\nID of the entry to delete: ")
    if purchase_id is None:
        return
    if input(f"Delete entry {purchase_id}? (y/n): ").strip().lower() != "y":
        print("Cancelled.")
        return
    _, deleted = handle(db.delete_purchase, user_id, purchase_id)
    print("Entry deleted." if deleted else "No entry with that ID.")


def show_totals(user_id):
    _, totals = handle(db.monthly_totals, user_id)
    if not totals:
        print("\nNo spending recorded yet.")
        return
    print("\n--- Monthly totals ---")
    for row in totals:
        print(f"{row['month']}: {euros(row['total_cents'])}")


def update_profile(user_id):
    _, user = handle(db.get_user, user_id)
    print(f"\nCurrent details: {user['foreName']} {user['surName']}, age {user['age']}, {user['email']}")
    print("Press Enter to keep the current value.")

    changes = {}
    for field, label in (
        ("foreName", "first name"),
        ("surName", "second name"),
        ("age", "age"),
        ("email", "email"),
    ):
        value = input(f"New {label}: ").strip()
        if value:
            changes[field] = value

    if not changes:
        print("No changes made.")
        return
    status, body = handle(db.update_user, user_id, **changes)
    print("Profile updated." if status == 200 and body else f"Could not update profile: {body}")


def user_menu(user_id):
    """user_id plays the role of the web session: it is set at login and
    every database call is made on behalf of this one user."""
    while True:
        _, user = handle(db.get_user, user_id)
        choice = input(
            f"\n=== Hello, {user['foreName']} ===\n"
            " 1. Add spending\n"
            " 2. View my spending\n"
            " 3. Edit a spending entry\n"
            " 4. Delete a spending entry\n"
            " 5. Monthly totals\n"
            " 6. Update my profile\n"
            " 7. Log out\n> "
        ).strip()

        if choice == "1":
            add_spending(user_id)
        elif choice == "2":
            view_spending(user_id)
        elif choice == "3":
            edit_spending(user_id)
        elif choice == "4":
            delete_spending(user_id)
        elif choice == "5":
            show_totals(user_id)
        elif choice == "6":
            update_profile(user_id)
        elif choice == "7":
            print("Logged out.")
            return
        else:
            print("Invalid choice.")


# ---------- Entry point ----------
def main():
    handle(db.create_tables)
    try:
        while True:
            choice = input(
                "\n=== Spending Tracker ===\n 1. Register\n 2. Log in\n 3. Exit\n> "
            ).strip()
            if choice == "1":
                register()
            elif choice == "2":
                user = log_in()
                if user:
                    user_menu(user["id"])
            elif choice == "3":
                print("Goodbye.")
                return
            else:
                print("Invalid choice.")
    except (KeyboardInterrupt, EOFError):
        print("\nGoodbye.")


if __name__ == "__main__":
    main()