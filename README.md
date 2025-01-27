# Telegram-бот для управления объявлениями

Этот проект представляет собой Telegram-бота, предназначенного для создания и модерации объявлений. Бот включает функции управления пользователями, создания объявлений и интеграции с Яндекс.Диском для хранения файлов.

## Установка

1. **Установите зависимости**:
   Убедитесь, что у вас установлен Python, затем установите необходимые зависимости:
   ```bash
   pip install -r requirements.txt
   ```

2. **Настройте переменные окружения**:
   Создайте файл `.env` в корневой директории и укажите необходимые переменные:
   ```
   CHANNEL_ID=ваш_id_канала
   BOT_TOKEN=ваш_токен_бота
   YANDEX_DISK_TOKEN=ваш_токен_яндекс_диска
   ```

## Использование

1. **Запустите бота**:
   Запустите бота, выполнив главный скрипт:
   ```bash
   python main.py
   ```

2. **Взаимодействуйте с ботом**:
   Откройте Telegram, найдите своего бота и используйте доступные команды для создания и модерации объявлений.

## Структура проекта

- **`application/db`**: Работа с базой данных (пользователи, объявления).
- **`application/handlers`**: Обработчики команд Telegram.
- **`application/utils`**: Вспомогательные утилиты (интеграция с Яндекс.Диском).
- **`bot.py`**: Точка входа для запуска бота.

---