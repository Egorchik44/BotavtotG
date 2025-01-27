import logging
from telegram import Update
from telegram.ext import  ContextTypes
from application.utils.admin_check import is_admin
from application.db.database_cars import get_car_info

from application.handlers.admin_handler import handle_approve_action, handle_reject_action
from application.handlers.admin_handler import mark_as_sold, view_ad, finish_photos
from application.handlers.user_ads import send_ad_page


MAX_PHOTOS = 10



async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    data = query.data
    chat_id = query.message.chat_id

    if data   == "finish_photos_":
        await finish_photos(update, context)
        if 'last_message_id' in context.user_data:
            try:
                await context.bot.delete_message(chat_id=chat_id, message_id=context.user_data['last_message_id'])
            except Exception as e:
                logging.error(f"Error deleting a message: {e}")   
    elif data == "add_photos_":
        await query.message.reply_text('Пожалуйста, отправьте до 10 фото для вашего объявления.')
        if 'last_message_id' in context.user_data:
            try:
                await context.bot.delete_message(chat_id=chat_id, message_id=context.user_data['last_message_id'])
            except Exception as e:
                logging.error(f"Error deleting a message: {e}")
        
    elif data.startswith('approve_') or data.startswith('reject_'):
        await handle_admin_actions(update, context)
    elif data.startswith('mark_as_sold_'):
        
        car_id = int(data.split('_')[3])#2
        context.args = [car_id]
        await handle_mark_as_sold(update, context)
    elif data.startswith('next_') or data.startswith('previous_'):
        await handle_ad_navigation(update, context)
    else:
        await query.message.reply_text('Неизвестное действие.')



async def handle_admin_actions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    user_id = query.from_user.id
    action, car_id = query.data.split('_', 1)

    if await is_admin(user_id):
        car_info, _ = await get_car_info(car_id)
        if action == 'approve':
            await handle_approve_action(update, context, car_id, car_info)
        elif action == 'reject':
            await handle_reject_action(update, context, car_id)
    else:
        await query.message.reply_text('У вас нет прав для выполнения этой команды.')

async def handle_mark_as_sold(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await mark_as_sold(update, context)
    await update.callback_query.message.delete()


async def handle_ad_navigation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    data = query.data
    action, page_str = data.split('_', 1)
    user_id = query.from_user.id

    if 'ad_ids' not in context.user_data:
        await query.message.reply_text("Ошибка в данных навигации.")
        return

    ad_ids = context.user_data['ad_ids']
    current_page = context.user_data.get('ad_page', 0)

    if action == 'next':
        new_page = min(len(ad_ids) - 1, current_page + 1)
    elif action == 'previous':
        new_page = max(0, current_page - 1)
    else:
        await query.message.reply_text("Неизвестное действие.")
        return

    context.user_data['ad_page'] = new_page

    await send_ad_page(update, context, query=query)


