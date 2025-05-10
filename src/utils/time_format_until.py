class TimeFormat():
    def format_time_until(self, time_delta):
        """
        Форматує timedelta в читабельний формат (дні, години, хвилини).
        Показує тільки необхідні компоненти часу.
        
        Args:
            time_delta: datetime.timedelta об'єкт
            
        Returns:
            str: Форматований рядок часу
        """
        if not time_delta:
            return ""
        
        days = time_delta.days
        hours = time_delta.seconds // 3600
        minutes = (time_delta.seconds % 3600) // 60
        
        time_parts = []
        
        # Додаємо дні, якщо є
        if days > 0:
            day_str = f"{days} {'день' if days == 1 else 'дні' if 1 < days < 5 else 'днів'}"
            time_parts.append(day_str)
        
        # Додаємо години, якщо є
        if hours > 0:
            hour_str = f"{hours} {'година' if hours == 1 else 'години' if 1 < hours < 5 else 'годин'}"
            time_parts.append(hour_str)
        
        # Додаємо хвилини, якщо є, або якщо немає днів і годин
        if minutes > 0 or not time_parts:
            minute_str = f"{minutes} {'хвилина' if minutes == 1 else 'хвилини' if 1 < minutes < 5 else 'хвилин'}"
            time_parts.append(minute_str)
        
        # Формуємо фінальний рядок
        time_str = ", ".join(time_parts)
        
        return f"Урок почнеться через <b>{time_str}</b>"
