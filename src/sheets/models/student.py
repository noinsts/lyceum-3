from typing import Any, List, Tuple, Optional
import datetime

from .base import BaseSheet
from src.utils import JSONLoader
from src.parsers.backend import ScheduleParsers


class StudentSheet(BaseSheet):
    LENGTH_SHEET = 7

    def get_lessons(self, form: str, day: Optional[str] = None) -> List[Tuple]:
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

        data = self.get_all_new()

        if not data or len(data) < 5:
            return []

        results = []
        header = data[2]  # тут зберігаються ПІП вчителів
        curr_day = None
        parser = ScheduleParsers()

        # проходимось по всіх рядках розкладу, починаючи з четвертого
        for row in data[3:]:
            # оновлюємо поточний день
            # якщо в першій колонці є текст, то це новий день
            if len(row) > 0 and row[0].strip():
                curr_day = row[0].strip()

            # якщо користувач вказав конкретний день, пропускаємо інші
            if day is not None and curr_day != day:
                continue

            # отримуємо номер уроку
            try:
                lesson_number = int(float(row[1]))
            except (IndexError, ValueError):
                continue

            # проходимось по всхі колонках з вчителями
            for col_index in range(2, len(row)):  # починаємо з третьої колонки
                try:
                    cell_value = row[col_index] if col_index < len(row) else ""

                    # пропуск порожніх клітинок
                    if not cell_value.strip():
                        continue

                    # парсимо клітинку
                    parsed_data = parser.parse_cell_value(cell_value)

                    if not parsed_data or not parsed_data.get('form') or not parsed_data.get('subject'):
                        continue

                except (IndexError, ValueError):
                    continue

                # перевіряємо чи це урок нашого класу
                if form.strip().lower() == parsed_data['form'].strip().lower():
                    subject = parsed_data['subject']
                    # отримуємо ім'я вчителя з заголовку
                    teacher = header[col_index] if col_index < len(header) and header[col_index] else "Невідомо"

                    if day:
                        results.append((lesson_number, subject, teacher))
                    else:
                        results.append((curr_day, lesson_number, subject, teacher))

        if not day:
            week_order = JSONLoader("settings/ukranian_weekname.json")
            results.sort(key=lambda r: (week_order.get(str(r[0].upper()), 99), r[1]))

        return results

    """
    дальше бога нет.
    (та документації теж)
    """

    def next_lesson(self, day: str, form: str, time: datetime.time) -> tuple[str, int | Any, str, str]:
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
                    return lesson_number, lesson_dt - now_dt, subject, teacher
        """Рекурсивно викликаємо функцію в випадку, якщо не знайдено жодного уроку"""
        day = JSONLoader("settings/ukranian_weekname.json").get_next_day(day)
        day = "ПОНЕДІЛОК" if not day else day
        return self.get_first_lesson(day, form, time)

    @staticmethod
    def get_date_from_day_string(day_string: str) -> datetime.date | None:
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

    def get_first_lesson(self, day: str, form: str, time: datetime.time) -> tuple[str, int | Any, str, str]:
        today = datetime.date.today()
        now_dt = datetime.datetime.combine(today, time)

        for row in self.get_all():
            if len(row) < 7:
                continue

            _, day_of_week, lesson_number, time_period, sheet_form, subject, teacher = row[:7]

            if day_of_week == day and sheet_form == form:
                start_time = self.parse_start_time(time_period)
                lesson_date = self.get_date_from_day_string(day_of_week)

                if not lesson_date:
                    continue

                lesson_dt = datetime.datetime.combine(lesson_date, start_time)

                return lesson_number, lesson_dt - now_dt, subject, teacher
