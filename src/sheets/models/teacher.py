from typing import List, Tuple, Optional

from .base import BaseSheet
from src.utils import JSONLoader, WeekFormat


class TeacherSheet(BaseSheet):
    # TODO: зробить метод пошуку уроків для нового розкладу

    async def my_classes(self, teacher_name: str) -> Optional[List]:
        """
        Метод пошуку класів, у яких веде вчитель

        Args:
            teacher_name (str): Повне ім'я вчителя (наприклад, "Іванов Іван Іванович")

        Returns:
            List[str]: Унікальні назви класів, у яких веде вчитель

        """

        data = await self.get_all_new()

        if data is None or len(data) < 5:
            return []

        results = set()
        # стартуєм з імен вчителів (особливості таблиці)
        teachers_row = data[2][2:]
        start_column = 2  # тому що стартуємо з другої, класна в нас таблиця просто

        for col_offset, name in enumerate(teachers_row):
            if name.strip() != teacher_name.strip():
                continue

            col_index = start_column + col_offset

            for row in data[3:]:
                if col_index > len(row):
                    continue

                class_name = row[col_index].strip()

                # TODO: зробить парсер, бо в ячеці не тільки клас, а і предмет

                # наприклад повернення масиву з класами, бо там можливо їх декілька

                # це може бути, тоді коли є розділювач |

                if class_name:
                    results.add(class_name)

        return sorted(results)

    async def get_new_lessons(self, teacher_name: str, day: Optional[str] = None) -> Optional[List[Tuple]]:
        pass

    async def get_lessons(self, tn: str, day: Optional[str] = None) -> List[Tuple] | None:
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
