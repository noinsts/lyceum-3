from .register import RegisterQueries
from .olymp import OlympQueries
from .verification import TeacherVerificationQueries
from .qualification import QualificationQueries
from .card import CardQueries

__all__ = [
    "TeacherVerificationQueries",
    "RegisterQueries",
    "OlympQueries",
    "QualificationQueries",
    "CardQueries"
]
