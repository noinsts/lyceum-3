import pytz
from datetime import datetime


class WeekFormat:
	@staticmethod
	def week() -> int:
		"""Функція виводить номер тижня"""
		return 0 if datetime.now(pytz.timezone("Europe/Kyiv")).isocalendar().week % 2 == 0 else 1

	def student(self, name: str, teacher: str) -> tuple[str, str] | tuple[None, None]:
		if '|' in name:
			name = name.split(" | ")[self.week()]
			teacher = teacher.split(" | ")[self.week()]

		name = None if not name or name.strip().lower() == "none" else name
		teacher = None if not teacher or teacher.strip().lower() == "none" else teacher

		return name, teacher


	def teacher(self, subject: str, teacher: str, tn: str) -> tuple[str, str] | tuple[None, None]:
		"""
		Повертає предмет і вчителя на поточному тижні, тільки якщо tn є в розкладі на цей тиждень.

		Args:
			subject (str): Назва предмета (може містити " | ").
			teacher (str): Ім’я/імена вчителя (може містити " | ").
			tn (str): Ім’я цільового вчителя (того, хто переглядає розклад).

		Returns:
			tuple[str, str] або (None, None), якщо tn не викладає цього предмета цього тижня.
		"""

		week = self.week()

		if "|" in teacher:
			try:
				teacher = teacher.split("|")[week].strip()
				subject = subject.split("|")[week].strip()
			except IndexError:
				return None, None
		else:
			teacher = teacher.strip()
			subject = subject.strip()

		# Чистимо і перевіряємо, чи tn є в полі teacher
		if tn.strip() not in [t.strip() for t in teacher.split(",")]:
			return None, None

		subject = None if not subject or subject.lower() == "none" else subject
		teacher = None if not teacher or teacher.lower() == "none" else teacher

		return subject, teacher
