from enum import Enum


class UserType(str, Enum):
    ADMIN = "ADMIN"
    DEVELOPER = "DEVELOPER"
    STUDENT = "STUDENT"
    TEACHER = "TEACHER"
    UNKNOWN = "UNKNOWN"
