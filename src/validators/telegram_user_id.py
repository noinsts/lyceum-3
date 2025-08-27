from src.exceptions import ValidationError


def validate_user_id(uid) -> bool:
    """
    Валідує Telegram User ID

    Args:
        uid: User ID

    Returns:
        bool: чи пройдена валідація

    Raises:
        ValidateError: якщо валідація не пройдена
    """
    if isinstance(uid, str):
        if not uid.isdigit():
            raise ValidationError("❌ User ID має бути числом або рядком з цифр")
        uid = int(uid)

    if not isinstance(uid, int):
        raise ValidationError("❌ User ID має бути цілим числом")

    if uid <= 0:
        raise ValidationError("❌ User ID має бути додатнім числом")

    max_64bit_int = 2**63 - 1

    if uid > max_64bit_int:
        raise ValidationError("❌ User ID перевищує максимальне допустиме значення")

    return True
