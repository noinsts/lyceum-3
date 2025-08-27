from typing import Optional

from pydantic import BaseModel


class AddUserSchema(BaseModel):
    user_id: int
    full_name: Optional[str] = None
    username: Optional[str] = None
    user_type: str
    form: Optional[str] = None
    teacher_name: Optional[str] = None
    student_name: Optional[str] = None
