from typing import Optional
from datetime import date

from pydantic import BaseModel


class AddOlymp(BaseModel):
    form: str
    student_name: str
    teacher_name: str
    subject: str
    stage_olymp: str
    date: date
    note: Optional[str] = None
