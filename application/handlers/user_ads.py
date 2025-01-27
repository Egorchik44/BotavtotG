import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from application.db.database_cars import get_car_info
from application.db.database_users import fetch_user_ad_ids


MAX_PHOTOS = 10
async def my_ad(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    ad_ids = await fetch_user_ad_ids(user_id)

    if not ad_ids:
        await update.message.reply_text('Нет активных объявлений.')
        return

    context.user_data['ad_ids'] = ad_ids
    context.user_data['ad_page'] = 0

    await send_ad_page(update, context)



async def send_ad_page(update: Update, context: ContextTypes.DEFAULT_TYPE, query: Update.callback_query = None) -> None:
    user_id = update.effective_user.id
    ad_ids = context.user_data.get('ad_ids', [])
    ad_page = context.user_data.get('ad_page', 0)
    
    if not ad_ids:
        await (query.message if query else update.message).reply_text("У вас нет активных объявлений.")
        return

    car_id = ad_ids[ad_page]
    car_info, _ = await get_car_info(car_id)

    caption = format_car_info(car_info)

    keyboard = [[InlineKeyboardButton("Снять Объявление", callback_data=f"mark_as_sold_{car_id}")]]
    navigation_buttons = get_navigation_buttons(ad_page, len(ad_ids))

    if navigation_buttons:
        keyboard.append(navigation_buttons)

    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        if query:
            await query.message.edit_text(text=caption, reply_markup=reply_markup)
        else:
            await update.message.reply_text(text=caption, reply_markup=reply_markup)
    except Exception as e:
        logging.error(f"Error sending message for car_id {car_id}: {e}")
        await update.message.reply_text('Произошла ошибка при отправке объявления.')

def format_car_info(car_info):
    caption_parts = [
        f'Марка: {car_info[1]}' if car_info[1] != "Не указано" else '',
        f'Модель: {car_info[2]}' if car_info[2] != "Не указано" else '',
        f'Год: {car_info[3]}' if car_info[3] != "Не указано" else '',
        f'Пробег: {car_info[4]}' if car_info[4] != "Не указано" else '',
        f'Цена: {car_info[5]}' if car_info[5] != "Не указано" else '',
        f'Местоположение: {car_info[6]}' if car_info[6] != "Не указано" else '',
        f'Описание: {car_info[7]}' if car_info[7] != "Не указано" else '',
    ]
    return '\n'.join(part for part in caption_parts if part)

def get_navigation_buttons(ad_page, total_ads):
    buttons = []
    if ad_page > 0:
        buttons.append(InlineKeyboardButton("Назад", callback_data=f"previous_{ad_page}"))
    if ad_page < total_ads - 1:
        buttons.append(InlineKeyboardButton("Вперед", callback_data=f"next_{ad_page}"))
    return buttons


