import sqlite3
from icecream import ic


# Set up the database connection
def get_connection(db_name):
    try:
        return sqlite3.connect(db_name)
    except Exception as e:
        ic(f"Error connecting to database: {e}")
        raise

# Create a table in the database
def create_table(connection):
     query = """
     CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL
        
    )
    """



















def main():
    connection = get_connection("Users.db")

if __name__ == "__main__":
        main()