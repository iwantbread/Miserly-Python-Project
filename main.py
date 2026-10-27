from multiprocessing.dummy import connection
import sqlite3
from icecream import ic


# Set up the database connection
def get_connection(db_name):
    try:        
        ic(f"Connected to database: {db_name}")  
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
        age INTEGER NOT NULL,
        email TEXT UNIQUE NOT NULL
    )
    """
    try:
        with connection:
            connection.execute(query)
            ic("Table created successfully.")
    except Exception as e:
        ic(f"Error creating table: {e}")
        raise

def insert_user(connection, name:str, age:int, email:str):
    query = "INSERT INTO users (name, age, email) VALUES (?, ?, ?)"
    try:
        with connection:
            connection.execute(query, (name, age, email))
            ic(f"User {name} inserted successfully.")
    except Exception as e:
        ic(f"Error inserting user: {e}")
        raise

def main():
    connection = get_connection("Users.db")
    
    create_table(connection)
    try:
        start = input("Please Choose an option: \n 1. Insert User \n 2. Delete User \n 3. Fetch User data \n 4. Exit \n")
        if start == '1': 
            name = input("Enter name: ")
            age = int(input("Enter age: "))
            email = input("Enter email: ")
            insert_user(connection, name, age, email)
        if start == '2':
            print("Delete User functionality not implemented yet.")
        if start == '3':
            print("Fetch User data functionality not implemented yet.")
        if start == '4':
            print("Exiting the program.")
            connection.close()
            exit()
    finally:
        connection.close()
    

if __name__ == "__main__":
        main()