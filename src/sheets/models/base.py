import os
from datetime import datetime, time
from typing import List

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build


# Ідемо тільки 2 рівні вверх до кореня (lyceum-3)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# Тепер просто йдемо до creds
CREDENTIALS_PATH = os.path.join(BASE_DIR, "creds", "credentials.json")


class BaseSheet:
    def __init__(self, spreadsheet_id: str, range_prefix: str):
        creds = Credentials.from_service_account_file(
            filename=CREDENTIALS_PATH,
            scopes=["https://www.googleapis.com/auth/spreadsheets"]
        )
        self.service = build("sheets", "v4", credentials=creds)
        self.sheet = self.service.spreadsheets()
        self.spreadsheet_id = spreadsheet_id
        self.range_prefix = range_prefix  # напр. "schedule!"
        self.LENGTH_SHEET = 7


    def get_all(self) -> List[List[str]]:
        result = self.sheet.values().get(
            spreadsheetId=self.spreadsheet_id,
            range=f"{self.range_prefix}A2:G"  # Без заголовка
        ).execute()
        return result.get("values", [])


    def parse_start_time(self, period: str) -> time:
        start_str = period.split('-')[0]
        return datetime.strptime(start_str, "%H%M").time()
