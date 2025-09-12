from typing import List, Dict

from .base import SpecialListHandler
from settings.admins import Admins


class AdminListHandler(SpecialListHandler):
    @property
    def triggers(self) -> Dict[str, str]:
        return {
            "hub": "dev_hub",
            "handler": "dev_admin_list"
        }

    @property
    def user_type(self) -> str:
        return "адміністраторів"

    @property
    def user_ids(self) -> List[int]:
        return Admins.ADMINS
