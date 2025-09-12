from typing import Dict, List

from .base import SpecialListHandler
from settings.developers import Developers


class DevListHandler(SpecialListHandler):
    @property
    def triggers(self) -> Dict[str, str]:
        return {
            "hub": "dev_hub",
            "handler": "dev_dev_list"
        }

    @property
    def user_type(self) -> str:
        return "розробників"

    @property
    def user_ids(self) -> List[int]:
        return Developers.DEVELOPERS
