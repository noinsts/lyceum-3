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

    async def legacy_get_lessons(self, tn: str, day: Optional[str] = None) -> List[Tuple] | None:
        # OLD SCHEDULE

        """
                Метод пошуку розкладу вчителя за днем або тижнем.

                Args:
                    tn (str): Повне ім'я вчителя (наприклад, "Іванов Іван Іванович").
                    day (Optional[str]): День тижня (наприклад, "ПОНЕДІЛОК"). Якщо None — повертається весь тиждень.

                Returns:
                    List[Tuple]:
                        Якщо задано день: [(номер_уроку, предмет, клас), ...]
                        Якщо без дня:     [(день_тижня, номер_уроку, предмет, клас), ...]
                """

        results = []

        for row in await self.get_all():
            if len(row) < self.LENGTH_SHEET:
                continue

            (
                _,
                day_of_week,
                lesson_number,
                _,
                form,
                subject,
                teacher
            ) = row[:7]

            if day is not None and day.strip().upper() != day_of_week.strip().upper():
                continue

            # парсимо данні для коректного відображення чисельник / знаменник
            corr_subject, corr_teacher = WeekFormat().teacher(subject, teacher, tn)

            if corr_teacher:
                try:
                    results.append((day_of_week, int(lesson_number), corr_subject, form))
                except ValueError:
                    continue

        if day is not None:
            # якщо пошук за днем, то видаляємо з results інформацію про день тижня
            return [(lesson_number, subject, form) for (_, lesson_number, subject, form) in results]

        # в разі пошуку за тижнем
        # сортуємо для обробки розкладу на тиждень
        results.sort(key=lambda r: (JSONLoader("settings/ukranian_weekname.json").get(str(r[0].upper()), 99), r[1]))
        return results
