from typing import List, Tuple, Optional, Literal

from .base import BaseSheet
from src.utils import JSONLoader, WeekFormat
from ...parsers.backend import ScheduleParsers


class TeacherSheet(BaseSheet):
    """
    Клас оброблює методи розкладу для вчителів
    """

    async def my_forms_or_subjects(
            self,
            teacher_name: str,
            return_type: Literal["form", "subject"] = "form"
    ) -> Optional[List[str]]:
        """
        Метод пошуку класів, у яких веде вчитель

        Args:
            teacher_name (str): Повне ім'я вчителя (наприклад, "Іванов Іван Іванович")
            return_type (Literal["form", "subject"]): Визначає що саме повертати.

        Returns:
            List[str]: Унікальні назви класів, у яких веде вчитель
        """

        data = await self.get_all_new()

        if data is None or len(data) < 5:
            return []

        results = set()
        parser = ScheduleParsers()

        teachers_row = data[2]
        teacher_col_index = -1

        for i, name in enumerate(teachers_row):
            if name and name.strip().lower() == teacher_name.strip().lower():
                teacher_col_index = i
                break

        if teacher_col_index == -1:
            return []

        for row in data[3:]:
            if teacher_col_index >= len(row):
                continue

            cell_value = row[teacher_col_index].strip()

            if not cell_value:
                continue

            parsed_data = parser.parse_cell_value(cell_value)

            value = parsed_data.get(return_type)
            if value and value.strip():
                results.add(value.strip())

        return list(results)

    async def get_lessons(self, teacher_name: str, day: Optional[str] = None) -> Optional[List[Tuple]]:
        """
        Повертає розклад для вказаного вчителя.

        Args:
            teacher_name (str): ім'я вчителя (наприклад, "Білецька Світлана Володимирівна")
            day (Optional[str]): день тижня (наприклад, "ПОНЕДІЛОК"). За замовчуванням - None

        Returns:
            List[Tuple]: список кортежів з інформацією про уроки.
                - Якщо day вказаний: [(номер_уроку, предмет, клас), ...]
                - Якщо day не вказаний: [(день, номер_уроку, предмет, клас), ...]
        """
        data = await self.get_all_new()

        if not data or len(data) < 5:
            return []

        results = []

        header = data[2]
        curr_day = None
        parser = ScheduleParsers()

        teacher_index = -1

        for i, name in enumerate(header):
            if name and teacher_name.strip().lower() == name.strip().lower():
                teacher_index = i
                break

        if teacher_index == -1:
            return []

        for row in data[3:]:
            if len(row) > 0 and row[0].strip():
                curr_day = row[0].strip()

            if day is not None and curr_day.upper() != day.upper():
                continue

            try:
                lesson_number = int(float(row[1]))
            except (ValueError, IndexError):
                continue

            try:
                cell_value = row[teacher_index] if teacher_index < len(row) else ""

                if not cell_value.strip():
                    continue

                parsed_data = parser.parse_cell_value(cell_value)

                if not parsed_data or not parsed_data.get("form") or not parsed_data.get("subject"):
                    continue

                subject = parsed_data["subject"]
                form = parsed_data["form"]

                if day:
                    results.append((lesson_number, subject, form))
                else:
                    results.append((curr_day, lesson_number, subject, form))

            except (IndexError, ValueError):
                continue

        if not day:
            week_order = JSONLoader("settings/ukranian_weekname.json")
            results.sort(key=lambda r: (week_order.get(str(r[0].upper()), 99), r[1]))

        return results
