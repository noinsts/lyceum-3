from typing import Dict, Optional
from datetime import datetime

import pytz


class ScheduleParsers:
    @staticmethod
    def _week() -> int:
        """
        Функція повертає номер тижня

        Returns:
            int 0: для непарного тижня (чисельник)
            int 1: для парного тижня (знаменник)

        """
        return 0 if datetime.now(pytz.timezone("Europe/Kyiv")).isocalendar().week % 2 != 0 else 1

    def parse_cell_value(self, cell_value: str) -> Dict[str, Optional[str]]:
        """
        Парсинг значення клітинки з уроком.
        Чудово підходить для методів обчислення уроків за днем

        Args:
            cell_value (str): значення клітинки

        Returns:
            Dict: {
                'form': '8-A',
                'subject': 'Алгебра'
            }
        """

        result = {
            'form': None,
            'subject': None
        }

        if not cell_value or not cell_value.strip():
            return result

        cell_value = cell_value.strip()

        if '|' in cell_value:
            parts = cell_value.split('|', 1)
            part = parts[self._week()].strip() if self._week() < len(parts) else ""
        else:
            part = cell_value

        if ', ' in part:
            form, subject = part.split(', ', 1)
            result['form'] = form
            result['subject'] = subject
        else:
            result['subject'] = part.strip()

        return result
