from datetime import datetime


def parse_date(date_str: str) -> datetime.strptime:
    """Парсить аргумент в форматі datetime.strptime, DD-MM-YYYY"""
    return datetime.strptime(date_str, "%d-%m-%Y").date()
