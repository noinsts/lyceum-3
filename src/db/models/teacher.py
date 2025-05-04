class TeacherModel:
    def __init__(self, connection):
        self.conn = connection.conn
        self.cursor = connection.cursor

    def get_post(self, day_week: str, teacher_name: str) -> str | None:
        self.cursor.execute("""
            SELECT post_number
            FROM duty_teachers
            WHERE day_week = ? AND name LIKE ?
        """, (day_week, f"%{teacher_name}%"))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def get_lessons_today(self, teacher_name: str, week_name: str) -> tuple[int, str, str] | None:
        self.cursor.execute("""
            SELECT lesson_number, subject, class
            FROM schedule
            WHERE day_of_week = ? AND LOWER(teacher) LIKE LOWER(?)
        """, (week_name, f"%{teacher_name.strip()}%"))
        results = self.cursor.fetchall()
        return results if results else None

    def get_all_week(self, teacher: str) -> list[tuple[str, int, str, str]] | None:
        self.cursor.execute("""
            SELECT day_of_week, lesson_number, subject, class
            FROM schedule
            WHERE teacher LIKE ?
            ORDER BY
              CASE day_of_week
                WHEN 'ПОНЕДІЛОК' THEN 1
                WHEN 'ВІВТОРОК' THEN 2
                WHEN 'СЕРЕДА' THEN 3
                WHEN 'ЧЕТВЕР' THEN 4
                WHEN 'П''ЯТНИЦЯ' THEN 5
                WHEN 'СУБОТА' THEN 6
                WHEN 'НЕДІЛЯ' THEN 7
                ELSE 8
              END, lesson_number;
        """, (f"%{teacher}%", ))
        results = self.cursor.fetchall()
        return results
