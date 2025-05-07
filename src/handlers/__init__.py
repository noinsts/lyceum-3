from .register import RegisterHandler
from .common import CommonHandler
from .student import StudentHandler
from .teacher import TeacherHandler
from .stats import StatsHandler
from .all import AllHandler

__all__ = [
    "RegisterHandler",
    "CommonHandler",
    "StudentHandler",
    "TeacherHandler",
    "StatsHandler",
    "AllHandler"
]
