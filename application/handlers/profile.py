import logging
from telegram import Update
from telegram.ext import ContextTypes
from application.db.database_users import get_user_info, get_username_by_user_id
from application.utils.admin_check import update_user_status_based_on_admin

async def user_profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        user_id = update.message.from_user.id
        user_first_name = update.message.from_user.first_name
        user_last_name = update.message.from_user.last_name
        
        await update_user_status_based_on_admin(user_id)

        user_info = await get_user_info(user_id)
        logging.debug(f"user_info: {user_info}")
        user_username = await get_username_by_user_id(user_id) or 'Не указан'
        logging.debug(f"user_username: {user_username}")
        
        if user_info:
            await update.message.reply_text(
                f"🌟 <b>Ваш Профиль</b> 🌟\n"
                f"━━━━━━━━━━━━━\n"
                f"👤 <b>Имя:</b> <i>{user_first_name} {user_last_name}</i>\n"
                f"🆔 <b>ID:</b> <code>{user_info[0]}</code>\n"
                f"📊 <b>Статус:</b> <i>{user_info[3]}</i>\n"
                f"📋 <b>Объявления:</b> <i>{user_info[2]} шт.</i>\n"
                f"🔗 <b>Профиль:</b> <a href='https://t.me/{user_username}'>@{user_username}</a>\n"
                f"━━━━━━━━━━━━━\n"
                f"🎉 Спасибо, что вы с нами!",
                parse_mode='HTML',
                disable_web_page_preview=True
            )
            
        else:
            await update.message.reply_text('Произошла ошибка при получении данных. Пожалуйста, попробуйте снова.')
    except Exception as e:
        logging.error(f"Error in user_profile handler: {e}")
        await update.message.reply_text('Произошла ошибка при обработке вашего запроса. Пожалуйста, попробуйте позже.')

