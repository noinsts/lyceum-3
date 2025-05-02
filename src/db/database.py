from .base import DatabaseConnection
from .models import *

class Database:
    def __init__(self):
        self.connection = DatabaseConnection()

        self.register = RegisterModel(self.connection)
        self.student = StudentModel(self.connection)
        self.teacher = TeacherModel(self.connection)

    def close(self):
        self.connection.close()
