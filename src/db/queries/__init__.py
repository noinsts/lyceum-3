from .register import RegisterQueries
from .olymp import OlympQueries
from .verification import TeacherVerificationQueries
from .qualification import QualificationQueries
from .card import CardQueries
from .interesting import InterestingQueries
from .shortened import ShortenedQueries

__all__ = [
    "TeacherVerificationQueries",
    "RegisterQueries",
    "OlympQueries",
    "QualificationQueries",
    "CardQueries",
    "InterestingQueries",
    "ShortenedQueries"
]
