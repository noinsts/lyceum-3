class StudentModel:
    def __init__(self, connection):
        self.conn = connection.conn
        self.cursor = connection.cursor

    def get_today(self, day: str, user_class: str) -> list[tuple[int, str, str]] | None:
        self.cursor.execute("""
            SELECT lesson_number, subject, teacher 
            FROM schedule 
            WHERE class = ? AND day_of_week = ?
        """, (user_class, day))
        results = self.cursor.fetchall()
        return results

    def get_all_week(self, user_class: str) -> list[tuple[str, int, str, str]] | None:
        self.cursor.execute("""
            SELECT day_of_week, lesson_number, subject, teacher
            FROM schedule
            WHERE class = ?
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
        """, (user_class, ))
        results = self.cursor.fetchall()
        return results
