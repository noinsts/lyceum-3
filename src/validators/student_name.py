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


def validate_student_name(student_name: str) -> bool:
    """
    Валідує ім'я студенту, наприклад (Остапенко Михайло)

    Args:
        student_name (str): ім'я студента

    Returns:
        True якщо формат вірний, False інакше
    """

    if not isinstance(student_name, str):
        return False

    return bool(STUDENT_NAME_PATTERN.match(student_name.strip()))
