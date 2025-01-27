import logging
from telegram import Update
from telegram.ext import ContextTypes
from application.db.database_users import add_user
from application.utils.admin_check import update_user_status_based_on_admin
from application.utils.menu import show_main_menu


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        user_id = update.message.from_user.id
        user_username = update.message.from_user.username
        await add_user(user_id, user_username)  
        await update_user_status_based_on_admin(user_id)
        await update.message.reply_text('Добро пожаловать! Доступные команды:\n - Создать новое объявление\n - Просмотреть профиль')
    except Exception as e:
        logging.error(f"Error in start handler: {e}")
        await update.message.reply_text('Произошла ошибка при выполнении команды. Пожалуйста, попробуйте позже.')
    await show_main_menu(update, context)

