from typing import List, Tuple, Optional

from .base import BaseSheet
from src.utils import JSONLoader
from src.parsers.backend import ScheduleParsers


class StudentSheet(BaseSheet):
    LENGTH_SHEET = 7

    async def get_lessons(self, form: str, day: Optional[str] = None) -> List[Tuple]:
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

        data = await self.get_all_new()

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
