class OlympsModel:
    def __init__(self, db_connection):
        self.conn = db_connection.conn
        self.cursor = db_connection.cursor

    def add_member(
            self,
            form: str,
            student_name: str,
            teacher_name: str,
            subject: str,
            stage_olymp: str,
            date: str,
            note: str
    ) -> None:

        query = """
        INSERT INTO olymps (form, student_name, teacher_name, subject, stage_olymp, date, note)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        self.cursor.execute(query, (form, student_name, teacher_name, subject, stage_olymp, date, note))
        self.conn.commit()
