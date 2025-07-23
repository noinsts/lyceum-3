import re
from datetime import datetime

#: Патерн для дати у форматі ДД-ММ-РРРР (наприклад, 22-07-2025)
DATE_PATTERN = re.compile(
    r"^(\d{2})-(\d{2})-(\d{4})$"
)
"""
DATE_PATTERN:
Матчить дату у форматі "ДД-ММ-РРРР".
- \d{2} — день (наприклад, "01", "22")
- \d{2} — місяць (наприклад, "07", "12")
- \d{4} — рік (наприклад, "2025")
"""


def validate_date(date: str) -> bool:
    """
    Валідує дату в форматі DD-MM-YYYY

    Args:
        date (str): сама дата

    Returns:
        True, якщо формат вірний, False інакше
    """

    if not isinstance(date, str):
        return False

    match = DATE_PATTERN.match(date.strip())

    if not match:
        return False

    try:
        day, month, year = map(int, match.groups())
        datetime(year, month, day)
        return True
    except ValueError:
        return False
