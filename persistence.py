import sqlite3
from datetime import datetime


class ResponseDatabase:
    """Database class.
    This class is used to store responses in a SQLite database.
    Table: responses
    Columns: id, user_id, created_at, question, response

    """

    def __init__(self, db_name: str, table_name: str):
        """Initialize the database."""
        if not db_name.endswith(".db"):
            raise ValueError("Database name must end with .db")
        if not table_name.isidentifier():
            raise ValueError("Table name must be a valid identifier")

        self._DB_NAME = db_name
        self._TABLE_NAME = table_name

        conn = sqlite3.connect(self._DB_NAME)
        c = conn.cursor()
        c.execute(
            f"CREATE TABLE IF NOT EXISTS {self._TABLE_NAME} (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, created_at TEXT, question TEXT, response TEXT)"
        )
        conn.commit()
        conn.close()

    def __enter__(self):
        """Enter the context manager."""
        self._connection = sqlite3.connect(self._DB_NAME)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit the context manager."""
        self._connection.close()

    def store(self, user_id: int, question: str, response: str):
        """Store the response in the database."""
        now = datetime.now()
        created_at = now.isoformat(sep=" ", timespec="seconds")

        c = self._connection.cursor()
        c.execute(
            f"INSERT INTO {self._TABLE_NAME} (user_id, created_at, question, response) VALUES (?, ?, ?, ?)",
            (user_id, created_at, question, response),
        )
        self._connection.commit()

    def get(self, user_id: int):
        """Get the response from the database."""
        c = self._connection.cursor()
        c.execute(f"SELECT * FROM {self._TABLE_NAME} WHERE user_id = ?", (user_id,))
        return c.fetchall()
