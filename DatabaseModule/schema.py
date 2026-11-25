from . import purchases, users

# Each module below exposes SCHEMA, a list of SQL statements.
# To add a table: create a module with its own SCHEMA and list it here (parents before children).
MODULES = [users, purchases]


def create_tables(connection):
    with connection:
        for module in MODULES:
            for statement in module.SCHEMA:
                connection.execute(statement)