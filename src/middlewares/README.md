# Middlewares

Тут зібрана інформація про всі мілдвейри проекту

## RoleAccessMiddleware

Middleware для контролю доступу до хендлерів по ролях.

### Фабричні методи

```python
RoleAccessMiddleware.for_students(**kwargs)      # middleware для студентів
RoleAccessMiddleware.for_teachers(**kwargs)      # middleware для вчителів
RoleAccessMiddleware.for_developers(**kwargs)    # middleware для розробників
RoleAccessMiddleware.for_admins(**kwargs)        # middleware для адміністраторів
```

## LoggingMiddleware

Щасливий сон любого DevOps'у, використовується для логування подій

### Його фішки

- Генерує **унікальний request_id** для кожного запиту.
- Логує **вхідні повідомлення**, тип події, дані та час обробки.
- Ловить помилки і логування трейсбеку лише для серйозних винятків.
- Спробує повідомити користувача про помилку.
- Підтримує Message, CallbackQuery та InlineQuery.
- Додатково обрізає довгі тексти для зручності логів.

## DBMiddleware

Використовується для лінивого прокидування DBConnector в хендлери

Спрацьовує тільки тоді, коли в сигнатурі обробника вказаний `db: DBConnector`

## AntiSpamMiddleware

Контролює щоб користувач не заспамив бота
