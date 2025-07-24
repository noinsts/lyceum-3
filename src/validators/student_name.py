from typing import Tuple, Optional
import re

#: Патерн для імені учня: Прізвище Імʼя (без по батькові).
STUDENT_NAME_PATTERN = re.compile(
    r"^([А-ЯІЇЄа-яіїє'`\-]+)\s+([А-ЯІЇЄа-яіїє'`\-]+)$"
)
"""
STUDENT_NAME_PATTERN:
Матчить ім’я учня у форматі "Прізвище Ім’я".
- Дозволяє апострофи, дефіси, зворотні апострофи.
- Рівно два слова.
Наприклад: "Коваленко Андрій", "ОʼНіл Джон"
"""


def validate_student_name(student_name: str) -> Tuple[bool, Optional[str]]:
    """
    Валідує ім'я студенту, наприклад (Остапенко Михайло)

    Args:
        student_name (str): ім'я студента

    Returns:
        Tuple:
            bool: чи проходить аргумент перевірка
            reason: примітки, щодо валідації
    """

    if len(student_name) < 3:
        return False, "Довжина імені має бути більше 3 символів"

    if len(student_name) > 50:
        return False, "Довжина імені має бути менше 50 символів"

    match = STUDENT_NAME_PATTERN.match(student_name.strip())

    if not isinstance(student_name, str) or not match:
        return False, "Використовуйте формат: \"Прізвище ім'я\""

    return True, ""
