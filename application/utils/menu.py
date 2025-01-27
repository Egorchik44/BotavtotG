# Description: Функция для отображения главного меню
import logging
from telegram import ReplyKeyboardMarkup, KeyboardButton

from application.db.database_users import get_admins

async def show_main_menu(update, context):
    user_id = update.effective_user.id  # Получаем ID пользователя, который вызвал команду
    if user_id in await get_admins():  # Проверяем, является ли пользователь администратором
        # Клавиатура для администраторов
        keyboard = [
            [KeyboardButton("Новое объявление📝"), KeyboardButton("Профиль👤")],
            [KeyboardButton("Мои объявления🗂")],
            [KeyboardButton("Просмотр объявлений⚙️"),KeyboardButton("Снятие с продажи⚙️")]
        ]
    else:
        # Клавиатура для обычных пользователей
        keyboard = [
            [KeyboardButton("Новое объявление📝"), KeyboardButton("Профиль👤")],
            [KeyboardButton("Мои объявления🗂")]
        ]

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
    message = update.message or update.callback_query.message  # Поддержка как обычных сообщений, так и callback_query
    try:
        await message.reply_text(
        "🔽 Выберите действие 🔼",
        reply_markup=reply_markup
        )
    except Exception as e:
        logging.error(f"Error sending main menu: {e}")

