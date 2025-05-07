import os
from dotenv import load_dotenv

from src.sheets.models import *

load_dotenv()

SHEET_ID = os.getenv("SHEET_ID")

class Sheet:
    def __init__(self):
        self.student = StudentSheet(
            spreadsheet_id=SHEET_ID,
            range_prefix="schedule!"
        )

        self.teacher = TeacherSheet(
            spreadsheet_id=SHEET_ID,
            range_prefix="schedule!"
        )
