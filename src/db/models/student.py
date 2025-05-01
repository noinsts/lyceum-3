class StudentModel:
    def __init__(self, connection):
        self.conn = connection.conn
        self.cursor = connection.cursor

    def get_today(self, day: str, user_class: str) -> str:
        self.cursor.execute("SELECT subject FROM schedule WHERE class = ? AND day_of_week = ?", (user_class, day))
        results = self.cursor.fetchall()
        return results