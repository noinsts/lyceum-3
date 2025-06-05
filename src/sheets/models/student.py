from typing import Any, List, Tuple, Optional
import datetime

from .base import BaseSheet
from src.utils import JSONLoader


class StudentSheet(BaseSheet):
    LENGTH_SHEET = 7

    
    def get_lessons(self, form: str, day: Optional[str] = None) -> List[Tuple] | None:

        """
        Повертає розклад для вказаного класу.

        Якщо вказано день — повертає розклад тільки на цей день.
        Інакше — повертає розклад на весь тиждень, відсортований по днях та номерах уроків.

        Args:
            form (str): клас (наприклад, "10-А")
            day (Optional[str], optional): день тижня (наприклад, "MONDAY"). За замовчуванням — None.

        Returns:
            List[Tuple]: список кортежів з інформацією про уроки.
                - Якщо day вказаний: [(номер_уроку, предмет, вчитель), ...]
                - Якщо day не вказаний: [(день, номер_уроку, предмет, вчитель), ...]
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
                sheet_form, 
                subject, 
                teacher
            ) = row[:7]

            if day is not None and day.upper() != day_of_week.upper():
                # перевіряємо день в бд тільки за умови того, що він вказаний в аргументах
                continue

            if sheet_form != form:
                continue

            try:
                results.append((day_of_week, int(lesson_number), subject, teacher))
            except ValueError:
                continue
                
        if day is not None:
            # опрацьовуємо варіант пошуку за днем
            # відкидуємо з кортежа інформацію про день
            return [(lesson_number, subject, teacher) for (_, lesson_number, subject, teacher) in results]
        
        # сортування для обробки розкладу на тиждень
        results.sort(key=lambda r: (JSONLoader()._config.get(str(r[0].upper()), 99), r[1]))
        return results

        
    """
    дальше бога нет.
    (та документації теж)
    """

    def next_lesson(self, day: str, form: str, time: datetime.time) -> tuple[str, str, int | Any, str, str]:
        today = datetime.date.today()
        now_dt = datetime.datetime.combine(today, time)

        for row in sorted(self.get_all(), key=lambda r: self.parse_start_time(r[3])):
            if len(row) < 7:
                continue

            _, day_of_week, lesson_number, time_period, sheet_form, subject, teacher = row[:7]

            if sheet_form == form and day_of_week == day:
                start_time = self.parse_start_time(time_period)
                lesson_dt = datetime.datetime.combine(today, start_time)
                if lesson_dt > now_dt:
                    return day, lesson_number, lesson_dt - now_dt, subject, teacher
        """Рекурсивно викликаємо функцію в випадку, якщо не знайдено жодного уроку"""
        day = JSONLoader().get_next_day(day)
        day = "ПОНЕДІЛОК" if not day else day
        return self.get_first_lesson(day, form, time)


    def get_date_from_day_string(self, day_string: str) -> datetime.date | None:
        today = datetime.date.today()
        days_of_week = ["ПОНЕДІЛОК", "ВІВТОРОК", "СЕРЕДА", "ЧЕТВЕР", "П'ЯТНИЦЯ", "СУБОТА", "НЕДІЛЯ"]
        try:
            day_index = days_of_week.index(day_string.upper())
            current_weekday = today.weekday()  # Понеділок = 0
            days_difference = day_index - current_weekday
            if days_difference <= 0:
                days_difference += 7  # наступний тиждень
            return today + datetime.timedelta(days=days_difference)
        except ValueError:
            return None


    def get_first_lesson(self, day: str, form: str, time: datetime.time) -> tuple[str, str, int | Any, str, str]:
        today = datetime.date.today()
        now_dt = datetime.datetime.combine(today, time)

        for row in self.get_all():
            if len(row) < 7:
                continue

            _, day_of_week, lesson_number, time_period, sheet_form, subject, teacher = row[:7]

            if day_of_week == day and sheet_form == form:
                start_time = self.parse_start_time(time_period)
                lesson_date = self.get_date_from_day_string(day_of_week)
                if lesson_date:
                    lesson_dt = datetime.datetime.combine(lesson_date, start_time)
                    return day, lesson_number, lesson_dt - now_dt, subject, teacher
