import os
import sqlite3

from .schema import Schema


class DatabaseConnection:
    def __init__(self, db_name='database.db'):
        db_path = os.path.join(os.path.dirname(__file__), "..", "..", "db", db_name)
        self.db_name = os.path.abspath(db_path)
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()

        Schema(self.cursor).create_tables()

    def close(self):
        self.conn.close()
