import re

from src.db.connector import DBConnector
from src.exceptions import ValidationError

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


async def validate_teacher_name(teacher_name: str) -> bool:
    """
    Валідує ім'я вчителя, наприклад (Іванов Іван Іванович)

    Args:
        teacher_name (str): ім'я вчителя
        db (DBConnector): бд з якої буде вестись перевірка на наявність вчителя

    Returns:
        bool: чи проходить валідація

    Raised:
        ValidateError: якщо валідація не пройшла
    """

    if len(teacher_name) < 3:
        raise ValidationError("Довжина імені має бути більше 3 символів")

    if len(teacher_name) > 50:
        raise ValidationError("Довжина імені має бути менше 50 символів")

    match = TEACHER_NAME_PATTERN.match(teacher_name.strip())

    if not isinstance(teacher_name, str) or not match:
        raise ValidationError("Використовуйте формат \"Прізвище ім'я по-батькові\"")

    return True
