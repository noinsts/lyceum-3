from .base import BaseSheet


class TeacherSheet(BaseSheet):
    def get_lessons_today(self, day: str, tn: str) -> list[tuple[int, str, str]] | None:
        results = []
        for row in self.get_all():
            if len(row) < 7:
                continue

            _, day_of_week, lesson_number, _, form, subject, teacher = row[:7]

            if teacher == tn and day_of_week == day:
                try:
                    results.append((int(lesson_number), subject, form))
                except ValueError:
                    continue

        return results
