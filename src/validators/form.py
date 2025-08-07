import re

from src.exceptions import ValidationError

#: Патерн для перевірки назви класу у форматі "7-А", "11-Б" тощо.
#: Складається з однієї або двох цифр, дефісу, та однієї української літери.
FORM_PATTERN = re.compile(
    r'^(\d{1,2})-([А-ЯІЇЄа-яіїє])$'
)
"""
FORM_PATTERN:
Матчить шкільні класи у форматі "Число-Літера", наприклад: "5-А", "11-Б".
- (\d{1,2}) — номер класу (від 1 до 99, але очікувано 1-11)
- ([А-ЯІЇЄа-яіїє]) — літера українського алфавіту (наприклад, "А", "Б", "В")
"""


def validate_form(form: str) -> bool:
    """
    Валідує формат класу (наприклад: 8-А, 10-Б)

    Args:
        form (str): рядок з класом

    Returns:
        True якщо формат вірний

    Raises:
        ValidationError: якщо валідація не пройшла
    """

    if not isinstance(form, str):
        raise ValidationError("Значення має бути рядком")

    match = FORM_PATTERN.match(form.strip())

    if not match:
        raise ValidationError("Формат класу має бути у вигляді '7-А', '10-Б' тощо")

    grade = int(match.group(1))

    if not (5 <= grade <= 11):
        raise ValidationError(f"Допустимий номер класу — від 5 до 11, отримано: {grade}")

    return True
