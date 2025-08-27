import os
import json


class JSONLoader:
    def __init__(self, config_path: str | None = None):
        self._config = {}
        if config_path:
            self.load(config_path)

    def load(self, config_path: str) -> None:
        abs_path = os.path.abspath(config_path)
        if not os.path.isfile(abs_path):
            raise FileNotFoundError(f"Файл не знайдено: {abs_path}")
        with open(abs_path, 'r', encoding='utf-8') as f:
            self._config = json.load(f)

    def __getattr__(self, name):
        return self._config.get(name)

    def get(self, key, default=None):
        return self._config.get(key, default)

    def get_next_day(self, current_day: str) -> str | None:
        days = list(self._config.values())
        try:
            index = days.index(current_day)
            next_index = (index + 1) % len(days)
            return days[next_index]
        except ValueError:
            return None
