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
                teacher_name TEXT,
                student_name TEXT
            )"""
        )

        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS olymps (
                form TEXT NOT NULL,
                student_name TEXT NOT NULL,
                teacher_name TEXT NOT NULL,
                subject TEXT NOT NULL,
                stage_olymp TEXT NOT NULL,
                date TEXT NOT NULL,
                note TEXT
            )"""
        )

        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS teachers_verification (
                user_id INTEGER PRIMARY KEY,
                teacher_name TEXT NOT NULL,
                is_verified INTEGER CHECK (is_verified IN (0, 1)) DEFAULT 0 
            )"""
        )
