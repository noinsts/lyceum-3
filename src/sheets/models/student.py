from typing import Any
from datetime import datetime

from .base import BaseSheet
from src.utils import JSONLoader


class StudentSheet(BaseSheet):
    def get_today(self, day: str, form: str) -> list[tuple[int, str | None, str | None]] | None:
        all_rows = self.get_all()
        results = []

        for row in all_rows:
            if len(row) < 7:
                continue

            lesson_id, day_of_week, lesson_number, time_period, sheet_form, subject, teacher = row[:7]
            if day_of_week == day and sheet_form == form:
                try:
                    results.append((int(lesson_number), subject, teacher))
                except ValueError:
                    continue

        return results


    def all_week(self, form: str) -> list[tuple[str, int, str | None, str | None]] | None:
        results = []

        for row in self.get_all():
            if len(row) < 7:
                continue

            _, day_of_week, lesson_number, _, sheet_form, subject, teacher = row[:7]

            if sheet_form != form:
                continue

            try:
                results.append((day_of_week, int(lesson_number), subject, teacher))
            except ValueError:
                continue

        results.sort(key=lambda r: (JSONLoader()._config.get(str(r[0].upper()), 99), r[1]))

        return results


    def next_lesson(self, day: str, form: str, time: datetime.time) -> tuple[str, int | Any, str, str] | None:
        today = datetime.today().date()
        now_dt = datetime.combine(today, time)

        for row in sorted(self.get_all(), key=lambda r: self.parse_start_time(r[3])):
            if len(row) < 7:
                continue

            _, day_of_week, lesson_number, time_period, sheet_form, subject, teacher = row[:7]

            if sheet_form == form and day_of_week == day:
                start_time = self.parse_start_time(time_period)
                lesson_dt = datetime.combine(today, start_time)
                if lesson_dt > now_dt:
                    return lesson_number, lesson_dt - now_dt, subject, teacher
        return None
