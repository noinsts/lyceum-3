from typing import Set, List, Tuple

from src.exceptions import ValidationError

def validate_multiple_forms(raw: str, dataset: Set[str], forms: List[str]) -> Tuple[str, Set[str]]:
    """
    Метод валідує введений клас та оновлює множину обраних класів.

    Args:
        raw (str): Введений користувачем клас.
        dataset (Set[str]): Набір уже обраних класів.
        forms (List[str]): Список доступних для вибору класів.

    Returns:
        Tuple:
            str: Повідомлення для користувача.
            Set[str]: Оновлена множина обраних класів.

    Raises:
        ValidationError: в разі помилки валідації
    """
    if raw not in forms:
        raise ValidationError("❌ Такого класу не існує")

    if raw in dataset:
        dataset.remove(raw)
        return f"Ви видалили {raw} з списку класів.", dataset

    dataset.add(raw)
    return f"Ви додали {raw} до списку класів", dataset
