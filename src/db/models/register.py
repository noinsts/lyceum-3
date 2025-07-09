from aiogram import types

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

    def add_user(self, user_id: int, user_type: str, full_name: str, username: str | None,
                 form: str | None = None, teacher_name: str | None = None) -> None:

        """
        Додає або оновлює користувача в базі даних.

        Args:
            user_id: Унікальний ідентифікатор користувача
            user_type: Тип користувача ('student' або 'teacher')
            full_name: Повне ім'я користувача (з Telegram)
            username: Username користувача (може бути None)
            form: Клас учня (None для вчителів)
            teacher_name: ПІБ вчителя (None для учнів)
        """
        # Встановлюємо значення відповідно до типу користувача
        if user_type == 'student':
            teacher_name = None
        elif user_type == 'teacher':
            form = None

        # Якщо користувач вже є — оновлюємо дані
        if self.checker(user_id):
            self.cursor.execute(
                """
                UPDATE users
                SET type = ?, class = ?, teacher_name = ?, full_name = ?, username = ?
                WHERE user_id = ?
                """,
                (user_type, form, teacher_name, full_name, username, user_id)
            )
        else:
            self.cursor.execute(
                """
                INSERT INTO users (user_id, type, class, teacher_name, full_name, username)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (user_id, user_type, form, teacher_name, full_name, username)
            )
        self.conn.commit()

    def update_udata(self, user: types.User):
        self.cursor.execute("""
            UPDATE users
            SET full_name = ?, username = ?
            WHERE user_id = ?
        """, (user.full_name, user.username, user.id))
        self.conn.commit()

    def teacher_checker(self, teacher_name: str) -> bool:
        self.cursor.execute("SELECT 1 FROM teacher_qualification WHERE teacher_name = ?", (teacher_name, ))
        return bool(self.cursor.fetchone())

    def teacher_is_verif(self, user_id: int, teacher_name: str) -> bool:
        """Getter верифікації вчителя"""
        self.cursor.execute("""
            SELECT is_verified 
            FROM teachers_verification
            WHERE user_id = ? AND teacher_name = ?
        """, (user_id, teacher_name))
        return bool(self.cursor.fetchone())

    def teacher_is_exists(self, user_id: int) -> str | None:
        """Перевірка наявності вчителя за user_id"""
        self.cursor.execute("""
            SELECT teacher_name
            FROM teachers_verification
            WHERE user_id = ?
        """, (user_id, ))

        results = self.cursor.fetchone()
        return results[0] if results else None

    def add_verif_teacher(self, user_id: int, teacher_name: str) -> None:
        """Setter верифікації вчителя"""
        self.cursor.execute("""
            INSERT INTO teachers_verification (user_id, teacher_name, is_verified)
            VALUES (?, ?, 1)
            ON CONFLICT(user_id) DO UPDATE SET 
                teacher_name = EXCLUDED.teacher_name,
                is_verified = 1
        """, (user_id, teacher_name))
        self.conn.commit()
