from enum import Enum


class DBUserType(str, Enum):
    """
    Це enum з всіма можливими варіантами заповнення колонки type в таблиці users
    """

    STUDENT = "student"
    TEACHER = "teacher"
