import sqlite3


def get_connection(db_name):
    connection = sqlite3.connect(db_name)
    connection.row_factory = sqlite3.Row  # rows can be turned into dicts
    connection.execute("PRAGMA foreign_keys = ON")  # needed on every connection
    return connection