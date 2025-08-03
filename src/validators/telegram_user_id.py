from typing import Tuple, Optional


def validate_user_id(uid) -> Tuple[bool, Optional[str]]:
    """
    Валідує Telegram User ID

    Args:
        uid: User ID

    Returns:
        Tuple[bool, Optional[str]]:
            - bool: чи валідний ID
            - Optional[str]: причина, якщо не валідний
    """
    if not isinstance(uid, int):
        return False, "❌ User ID має бути числом"

    if uid <= 0:
        return False, "❌ User ID має бути додатнім числом"

    if uid > 2_147_483_647:
        return False, "❌ User ID перевищує максимальне допустиме значення"

    return True, None
