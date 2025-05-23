class Schema:
    def __init__(self, cursor):
        self.cursor = cursor

    def create_tables(self):
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                full_name TEXT NOT NULL,
                username TEXT NOT NULL,
                type TEXT NOT NULL CHECK(type IN ('teacher', 'student')),
                class TEXT,
                teacher_name TEXT
            )"""
        )
