import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from application.db.database_cars import add_car_photo, get_ad_status

from application.utils.yandex_disk import YandexDiskAPI

api=os.getenv('APi_Yandex')
yandex_disk = YandexDiskAPI(api)



async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        if not update.message or not update.message.photo:
            logging.info('Received non-photo update: %s', update)
            return

        car_id = context.user_data.get('car_id')
        if not car_id:
            logging.error('Car ID is missing in user_data.')
            await update.message.reply_text('Произошла ошибка при обработке фото. Пожалуйста, попробуйте снова.')
            return

        status = await get_ad_status(car_id)
        if status == 'published':
            logging.info(f'Ad with car ID {car_id} is already published.')
            await update.message.reply_text('Это объявление уже опубликовано и не может быть изменено.')
            return

        user_id = context.user_data.get('user_id')
        if not user_id:
            logging.error('User ID is missing in user_data.')
            await update.message.reply_text('Произошла ошибка при обработке фото. Пожалуйста, попробуйте снова.')
            return

        car_info = context.user_data.get('car_info', {})
        make = car_info.get('make')
        model = car_info.get('model')
        if not make or not model:
            logging.error('Make or model is missing in car_info.')
            await update.message.reply_text('Произошла ошибка при обработке фото. Пожалуйста, попробуйте снова.')
            return

        photo_count = context.user_data.get('photo_count', 0)
        max_photos = 10

        if photo_count >= max_photos:
            logging.info(f'User {user_id} attempted to upload more than {max_photos} photos for car ID {car_id}.')
            await update.message.reply_text('Вы достигли максимального количества фото для этого объявления. Больше фото не принимаются.')
            return

        photo = update.message.photo[-1]
        file = await context.bot.get_file(photo.file_id)

        file_name = f'{car_id}_{user_id}_{make}_{model}_{photo_count}.jpg'
        file_data = await file.download_as_bytearray()

        file_path = await yandex_disk.upload_to_disk(file_data, file_name)
        logging.info(f'Photo uploaded to Yandex Disk with path: {file_path}')

        public_link = await yandex_disk._get_public_link(file_path)
        logging.info(f'Public link for the uploaded file: {public_link}')

        await add_car_photo(car_id, public_link)
        context.user_data['photo_count'] = photo_count + 1

        progress_bar = '📸' * (photo_count + 1) + '⚪' * (max_photos - (photo_count + 1))

        message_text = (
            f'Фото добавлено. Загружено {photo_count + 1} из {max_photos} фото.\n'
            f'{progress_bar}\n'
            'Вы можете добавить еще фото или нажать "Готово".'
        )
        reply_markup = InlineKeyboardMarkup.from_button(InlineKeyboardButton("Готово", callback_data="finish_photos_"))

        last_message_id = context.user_data.get('last_message_id')
        if last_message_id:
            try:
                logging.info(f"Editing message with ID {last_message_id} in chat {update.message.chat_id}")
                await context.bot.edit_message_text(
                    text=message_text,
                    chat_id=update.message.chat_id,
                    message_id=last_message_id,
                    reply_markup=reply_markup
                )
            except Exception as e:
                logging.error(f"Error editing the message: {e}")
                message = await update.message.reply_text(message_text, reply_markup=reply_markup)
                context.user_data['last_message_id'] = message.message_id
        else:
            message = await update.message.reply_text(message_text, reply_markup=reply_markup)
            context.user_data['last_message_id'] = message.message_id
    except Exception as e:
        logging.error(f"Error in handle_photo handler: {e}")
        await update.message.reply_text('Произошла ошибка при обработке вашего фото. Пожалуйста, попробуйте позже.')

