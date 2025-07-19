from typing import Optional

from pydantic import BaseModel

from src.enums import DBUserType


class AddUserSchema(BaseModel):
    user_id: int
    full_name: Optional[str] = None
    username: Optional[str] = None
    user_type: DBUserType
    form: Optional[str] = None
    teacher_name: Optional[str] = None
    student_name: Optional[str] = None
