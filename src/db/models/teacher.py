class TeacherModel:
    def __init__(self, connection):
        self.conn = connection.conn
        self.cursor = connection.cursor

    def get_post(self, day_week: str, teacher_name: str) -> str | None:
        self.cursor.execute("""
            SELECT post_number
            FROM duty_teachers
            WHERE day_week = ? AND name = ?
        """, (day_week, teacher_name))
        result = self.cursor.fetchone()
        return result[0] if result else None
