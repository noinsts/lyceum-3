from typing import Type

from .base_blocker import BaseBlockerAccessHandler
from src.db.connector import DBConnector
from src.states.developer import AccessBlock, AccessUnblock


class UnblockAccessHandler(BaseBlockerAccessHandler):
    def get_curr_state(self) -> Type[AccessBlock | AccessUnblock]:
        return AccessUnblock

    def __init__(self):
        super().__init__()

    def is_verified(self) -> bool:
        return True

    async def get_check_can_process(self, user_id: int, teacher_name: str, db: DBConnector) -> bool:
        return not await db.verification.is_verif(user_id, teacher_name)

    def get_already_processed_message(self) -> str:
        return "⚠️ Користувач вже має доступ"

    def get_success_message(self) -> str:
        return "✅ Доступ розблоковано"

    def get_action_name(self) -> str:
        return "розблокувати"

    def get_cancel_trigger(self) -> str:
        return "cancel_developer_access_unblock"

    def get_submit_trigger(self) -> str:
        return "submit_developer_access_unblock"

    def get_handler_trigger(self) -> str:
        return "dev_access_unblock"
