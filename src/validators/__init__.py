from .form import validate_form
from .teacher_name import validate_teacher_name
from .student_name import validate_student_name
from .date import validate_date
from .telegram_user_id import validate_user_id
from .multiply_forms import validate_multiple_forms

__all__ = [
    "validate_form",
    "validate_teacher_name",
    "validate_student_name",
    "validate_date",
    "validate_user_id",
    "validate_multiple_forms"
]
