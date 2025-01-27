import os
import logging
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import ContextTypes, CallbackQueryHandler, CommandHandler


from application.db.database_cars import update_ad_status, get_car_info, update_message_id, get_message_id, get_media_count
from application.db.database_users import get_username_by_user_id, get_admins, update_user_ads_count



from application.utils.yandex_disk import YandexDiskAPI

load_dotenv()

channel = os.getenv('CHANNEL_ID')

MAX_PHOTOS = 10

yandex_disk = YandexDiskAPI('--------')



async def handle_approve_action(update: Update, context: ContextTypes.DEFAULT_TYPE, car_id: int, car_info: tuple):
    user_id = car_info[0]
    user_username = await get_username_by_user_id(user_id) or 'Неизвестный пользователь'

    
    caption_parts = [
        f'🚘 В продаже 🚘',
        f'Марка: {car_info[1]}' if car_info[1] != "Не указано" else '',
        f'Модель: {car_info[2]}' if car_info[2] != "Не указано" else '',
        f'Год: {car_info[3]}' if car_info[3] != "Не указано" else '',
        f'Пробег: {car_info[4]}' if car_info[4] != "Не указано" else '',
        f'Цена: {car_info[5]}' if car_info[5] != "Не указано" else '',
        f'Местоположение: {car_info[6]}' if car_info[6] != "Не указано" else '',
        f'Описание: {car_info[7]}' if car_info[7] != "Не указано" else '',
        f'ID Объявления: {car_id}',
        f'☎️Связь: @{user_username}'
    ]
    
    caption = '\n'.join(part for part in caption_parts if part)
    media_group = await prepare_media_group(car_id, caption)

    try:
        if media_group:
            logging.info(f"Sending media group for car_id {car_id}")
            sent_messages = await context.bot.send_media_group(chat_id=channel, media=media_group)
            context.user_data['media_message_ids'] = [msg.message_id for msg in sent_messages]
        else:
            logging.info(f"Sending text message for car_id {car_id}")
            sent_message = await context.bot.send_message(chat_id=channel, text=caption)
            context.user_data['media_message_ids'] = [sent_message.message_id]
        
        await update_user_ads_count(user_id)
        await update_ad_status(int(car_id), 'in_sale', 'approved')
        
        # Update the message_id in the database
        await update_message_id(car_id, context.user_data['media_message_ids'][0])
        
        if update.callback_query:
            await context.bot.delete_message(chat_id=update.callback_query.message.chat_id, message_id=update.callback_query.message.message_id)
            await update.callback_query.message.reply_text(f'Объявление {car_id} одобрено и опубликовано.')
        else:
            logging.error("Callback query is None")
        
        await context.bot.send_message(chat_id=user_id, text=f'✅ Ваше объявление "{car_info[1]} {car_info[2]} {car_info[3]}" опубликовано.')

    except Exception as e:
        logging.error(f"Error sending media group or message for car_id {car_id}: {e}")
        if update.callback_query:
            await update.callback_query.message.reply_text('Произошла ошибка при публикации объявления. Пожалуйста, попробуйте снова.')


async def handle_reject_action(update: Update, context: ContextTypes.DEFAULT_TYPE, car_id: int):
    try:
        await update_ad_status(int(car_id), 'not_in_sale', 'rejected')
        
        message_id = await get_message_id(car_id)
        
        if message_id:
            logging.info(f"Attempting to delete message with ID {message_id} for rejected ad {car_id} in channel {channel}")
            try:
                await context.bot.delete_message(chat_id=channel, message_id=message_id)
                logging.info(f"Successfully deleted message with ID {message_id} for rejected ad {car_id}")
            except Exception as e:
                logging.error(f"Error deleting message with ID {message_id} for rejected ad {car_id}: {e}")
        else:
            logging.warning(f"No message ID found for car_id {car_id}")

        media_count = await get_media_count(car_id)
        if media_count > 0:
            logging.info(f"Attempting to delete {media_count} media messages for rejected ad {car_id}")
            for i in range(media_count):
                media_message_id = message_id + i
                logging.info(f"Attempting to delete media message with ID {media_message_id}")
                try:
                    await context.bot.delete_message(chat_id=channel, message_id=media_message_id)
                    logging.info(f"Successfully deleted media message with ID {media_message_id} for rejected ad {car_id}")
                except Exception as e:
                    logging.error(f"Error deleting media message with ID {media_message_id} for rejected ad {car_id}: {e}")

        car_info, _ = await get_car_info(car_id)
        user_id = car_info[0]
        await context.bot.send_message(chat_id=user_id, text=f'❌ Ваше объявление "{car_info[1]} {car_info[2]} {car_info[3]}" отклонено.')
        
        await update.callback_query.message.reply_text(f'Объявление {car_id} отклонено.')

        if update.callback_query:
            try:
                await context.bot.delete_message(chat_id=update.callback_query.message.chat_id, message_id=update.callback_query.message.message_id)
                logging.info(f"Successfully deleted admin message with ID {update.callback_query.message.message_id} for rejected ad {car_id}")
            except Exception as e:
                logging.error(f"Error deleting admin message with ID {update.callback_query.message.message_id} for rejected ad {car_id}: {e}")
        else:
            logging.error("Callback query is None")
            
    except Exception as e:
        logging.error(f"Error in handle_reject_action for car_id {car_id}: {e}")
        await update.callback_query.message.reply_text('Произошла ошибка при отклонении объявления. Пожалуйста, попробуйте снова.')


async def prepare_media_group(car_id: int, caption: str):
    photos = await yandex_disk.get_yandex_disk_photos(car_id)
    media_group = []
    if photos:
        for photo_url in photos[:MAX_PHOTOS]:  
            media_group.append(InputMediaPhoto(media=photo_url, caption=caption if len(media_group) == 0 else None))
    return media_group

async def finish_photos(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    car_id = context.user_data.get('car_id')
    
    if car_id:
        car_info = context.user_data['car_info']
        user_id = context.user_data['user_id']
        user_username = await get_username_by_user_id(user_id) or 'Неизвестный пользователь'
        caption = (
            f'ID Объявления: {car_id}\n'
            f'Автор объявления: @{user_username}\n\n'
            f'Текст объявления: \n'
            f'Марка: {car_info["make"]}\n'
            f'Модель: {car_info["model"]}\n'
            f'Пробег: {car_info["mileage"]}\n'
            f'Год: {car_info["year"]}\n'
            f'Местоположение: {car_info["place"]}\n'
            f'Цена: {car_info["price"]}\n'
            f'Описание: {car_info["description"]}\n')
        
        
        try:
            media_group = await prepare_media_group(car_id, caption)

            admins = await get_admins()
            for admin in admins:
                if media_group:
                    await context.bot.send_media_group(chat_id=admin, media=media_group)
                else:
                    await context.bot.send_message(chat_id=admin, text=caption)

                await context.bot.send_message(
                    chat_id=admin,
                    text=f'Пожалуйста, рассмотрите объявление:',
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("✅Одобрить", callback_data=f"approve_{car_id}"),InlineKeyboardButton("❌Отклонить", callback_data=f"reject_{car_id}")],
                        # []
                    ])
                )

            if update.callback_query:
                await update.callback_query.message.reply_text('Объявление отправлено на проверку.')
            
            await update_ad_status(car_id, 'pending')
        except Exception as e:
            logging.error(f"Error occurred when sending a message to the administrator: {e}")
            if update.callback_query:
                await update.callback_query.message.reply_text('Произошла ошибка при отправке на проверку. Пожалуйста, попробуйте снова.')
    else:
        if update.callback_query:
            await update.callback_query.message.reply_text('Произошла ошибка при обработке объявления. Пожалуйста, попробуйте снова.')



async def view_ad(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    admins = await get_admins()
    if user_id not in admins:
        if update.message:
            await update.message.reply_text("У вас нет прав для выполнения этой команды.")
        return

    try:
        car_id = int(context.args[0])
    except (IndexError, ValueError):
        if update.message:
            await update.message.reply_text("Пожалуйста, укажите корректный ID объявления.")
        return

    car_info, photos = await get_car_info(car_id)
    if not car_info:
        if update.message:
            await update.message.reply_text("Объявление с указанным ID не найдено.")
        return

    context.user_data['car_id'] = car_id
    context.user_data['car_info'] = {
        "make": car_info[1],
        "model": car_info[2],
        "mileage": car_info[4],
        "year": car_info[3],
        "place": car_info[6],
        "price": car_info[5],
        "description": car_info[7]
    }
    context.user_data['user_id'] = car_info[0]
    
    await finish_photos(update, context)

async def mark_as_sold(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    car_id = int(context.args[0]) if context.args else None

    if not car_id:
        if update.effective_message:
            await update.effective_message.reply_text("Пожалуйста, укажите корректный ID объявления.")
        return

    car_info, _ = await get_car_info(car_id)
    message_id = await get_message_id(car_id)

    if not car_info or message_id is None:
        if update.effective_message:
            await update.effective_message.reply_text("Объявление с указанным ID не найдено или не опубликовано.")
        return

    ad_author_id = car_info[0]  
    admins = await get_admins()

    if user_id not in admins and user_id != ad_author_id:
        if update.effective_message:
            await update.effective_message.reply_text("У вас нет прав для выполнения этой команды.")
        return

    user_username = await get_username_by_user_id(ad_author_id) or 'Неизвестный пользователь'

    caption_parts = [
        f'ПРОДАНО',
        f'Марка: {car_info[1]}' if car_info[1] != "Не указано" else '',
        f'Модель: {car_info[2]}' if car_info[2] != "Не указано" else '',
        f'Год: {car_info[3]}' if car_info[3] != "Не указано" else '',
        f'Пробег: {car_info[4]}' if car_info[4] != "Не указано" else '',
        f'Цена: {car_info[5]}' if car_info[5] != "Не указано" else '',
        f'Местоположение: {car_info[6]}' if car_info[6] != "Не указано" else '',
        f'Описание: {car_info[7]}' if car_info[7] != "Не указано" else '',
        f'☎️Связь: @{user_username}'
    ]

    caption = '\n'.join(part for part in caption_parts if part)

    try:
        if _:
            media_group = await prepare_media_group(car_id, caption)
            if media_group:
                try:
                    await context.bot.edit_message_media(chat_id=channel, message_id=message_id, media=media_group[0])
                except Exception as e:
                    logging.error(f"Error editing media message {message_id} for car_id {car_id}: {e}")

                if len(media_group) > 1:
                    for i in range(1, len(media_group)):
                        try:
                            await context.bot.edit_message_media(chat_id=channel, message_id=message_id + i, media=media_group[i])
                        except Exception as e:
                            logging.error(f"Error editing additional media message {message_id + i} for car_id {car_id}: {e}")
        else:
            try:
                await context.bot.edit_message_text(chat_id=channel, message_id=message_id, text=caption)
            except Exception as e:
                logging.error(f"Error editing text message {message_id} for car_id {car_id}: {e}")

        await update_ad_status(car_id, 'not_in_sale', 'sold')
        if update.effective_message:
            await update.effective_message.reply_text(f'Объявление {car_id} отмечено как "снято с продажи".')

    except Exception as e:
        logging.error(f"Error processing car_id {car_id}: {e}")
        if update.effective_message:
            await update.effective_message.reply_text('Произошла ошибка при изменении статуса объявления. Пожалуйста, попробуйте снова.')


