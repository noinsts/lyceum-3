from typing import Tuple, Optional
import re

from src.db.connector import DBConnector

#: Патерн для повного ПІБ вчителя: Прізвище Імʼя По батькові.
#: Дозволяє українські літери, апострофи, дефіси.
TEACHER_NAME_PATTERN = re.compile(
    r"^([А-ЯІЇЄа-яіїє'`\-]+)\s+([А-ЯІЇЄа-яіїє'`\-]+)\s+([А-ЯІЇЄа-яіїє'`\-]+)$"
)
"""
TEACHER_NAME_PATTERN:
Матчить повне ім’я вчителя: "Прізвище Ім’я По батькові".
- Кожна частина може мати апостроф (ʼ), зворотний апостроф (`) або дефіс (-).
- Має бути рівно 3 слова, розділені пробілами.
Наприклад: "Іваненко Олег Петрович", "Донченко-Гнатюк Іван-Петро Іванович"
"""


async def validate_teacher_name(teacher_name: str, db: DBConnector) -> Tuple[bool, Optional[str]]:
    """
    Валідує ім'я вчителя, наприклад (Іванов Іван Іванович)

    Args:
        teacher_name (str): ім'я вчителя
        db (DBConnector): бд з якої буде вестись перевірка на наявність вчителя

    Returns:
        Tuple:
            bool: чи проходить аргумент перевірка
            reason: примітки, щодо валідації
    """

    if len(teacher_name) < 3:
        return False, "Довжина імені має бути більше 3 символів"

    if len(teacher_name) > 50:
        return False, "Довжина імені має бути менше 50 символів"

    match = TEACHER_NAME_PATTERN.match(teacher_name.strip())

    if not isinstance(teacher_name, str) or not match:
        return False, "Використовуйте формат \"Прізвище ім'я по-батькові\""

    if not await db.register.teacher_is_exists(teacher_name):
        return False, (
            "🚫 Такого ПІП немає в нашому списку вчителів. "
            "Можливо, ви ввели з помилкою або ще не додані до бази.\n"
            "Спробуйте ще раз або зверніться до @noinsts 👨‍💻"
        )

    return True, ""
