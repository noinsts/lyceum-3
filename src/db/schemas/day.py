import datetime

from pydantic import BaseModel


class DaySchema(BaseModel):
    is_shortened: bool
    call_schedule: str
    date: datetime.date
