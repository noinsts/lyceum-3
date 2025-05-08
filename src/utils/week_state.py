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

	        name = None if name == "None" else name
	        teacher = None if teacher == "None" else teacher

	    return name, teacher


	def teacher(self, subject: str) -> str:
		if '|' in subject:
			subject = subject.split(" | ")[self.week()]
		return subject
