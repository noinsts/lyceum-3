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
    if isinstance(uid, str):
        if not uid.isdigit():
            return False, "❌ User ID має бути числом або рядком з цифр"
        uid = int(uid)

    if not isinstance(uid, int):
        return False, "❌ User ID має бути цілим числом"

    if uid <= 0:
        return False, "❌ User ID має бути додатнім числом"

    max_64bit_int = 2**63 - 1

    if uid > max_64bit_int:
        return False, "❌ User ID перевищує максимальне допустиме значення"

    return True, None
