from typing import List, Tuple, Optional

from .base import BaseSheet
from src.utils import JSONLoader, WeekFormat

class TeacherSheet(BaseSheet):
    def get_lessons(self, tn: str, day: Optional[str] = None) -> List[Tuple] | None: 

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

        for row in self.get_all():
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
