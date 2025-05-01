class RegisterModel:
    def __init__(self, db_connection):
        self.conn = db_connection.conn
        self.cursor = db_connection.cursor

    def checker(self, user_id: int) -> str | None:
        self.cursor.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id, ))
        result = self.cursor.fetchone()
        return result is not None

    def get_type(self, user_id: int) -> str:
        self.cursor.execute("SELECT type FROM users WHERE user_id = ?", (user_id, ))
        result = self.cursor.fetchone()
        return result[0]

    def get_class(self, user_id: int) -> str:
        self.cursor.execute("SELECT class FROM users WHERE user_id = ?", (user_id, ))
        result = self.cursor.fetchone()
        return result[0]

    def get_teacher_name(self, user_id: int) -> str:
        self.cursor.execute("SELECT teacher_name FROM users WHERE user_id = ?", (user_id, ))
        result = self.cursor.fetchone()
        return result[0]

    def clone_teacher(self, name: str) -> bool:
        """Перевірка, чи є такий вчитель"""
        self.cursor.execute("SELECT 1 FROM users WHERE teacher_name = ?", (name, ))
        result = self.cursor.fetchone()
        return result is not None


    def add_user(self, user_id: int, user_type: str, form: str | None = None, teacher_name: str | None = None) -> None:
        """
        Додає або оновлює користувача в базі даних.

        Args:
            user_id: Унікальний ідентифікатор користувача
            user_type: Тип користувача ('student' або 'teacher')
            form: Клас учня (None для вчителів)
            teacher_name: ПІБ вчителя (None для учнів)
        """
        # Встановлюємо значення відповідно до типу користувача
        if user_type == 'student':
            # Для учня - форма класу обов'язкова, ПІБ вчителя - пустий
            teacher_name = None
        elif user_type == 'teacher':
            # Для вчителя - клас пустий, ПІБ обов'язковий
            form = None

        # Перевіряємо наявність користувача та оновлюємо або додаємо
        if self.checker(user_id):
            self.cursor.execute(
                """
                UPDATE users
                SET type = ?, class = ?, teacher_name = ?
                WHERE user_id = ?
                """,
                (user_type, form, teacher_name, user_id)
            )
        else:
            self.cursor.execute(
                """
                INSERT INTO users (user_id, type, class, teacher_name)
                VALUES (?, ?, ?, ?)
                """,
                (user_id, user_type, form, teacher_name)
            )
        self.conn.commit()
