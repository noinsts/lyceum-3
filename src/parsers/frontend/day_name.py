from typing import Optional
from datetime import datetime, timedelta
from pytz import timezone

from src.utils import JSONLoader


def parse_day_name(offset: int = 0) -> Optional[str]:
    """
    Повертає українську назву дня зі врахуванням зміщення

    Args:
        offset (int): зміщення відносно поточного дня

    Returns:
        Optional[str]: Назва дня тижня українською

    """
    kyiv_timezone = timezone("Europe/Kyiv")
    current_date = datetime.now(kyiv_timezone) + timedelta(days=offset)
    day_num = current_date.weekday()

    day_name = JSONLoader("settings/ukranian_weekname.json").get(str(day_num))
    return day_name
