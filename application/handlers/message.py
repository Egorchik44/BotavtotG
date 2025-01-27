import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from application.db.database_cars import add_car
from application.db.database_users import get_user_status
from application.utils.admin_check import update_user_status_based_on_admin



async def handle_user_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        if not update.message:
            logging.info('Received non-message update: %s', update)
            return

        user_id = update.message.from_user.id
        message_text = update.message.text
        logging.info(f"Received message from user {user_id}: {message_text}")

        if context.user_data.get('in_ad_form'):
            await handle_new_ad_input(update, context)
        else:
            await update.message.reply_text("Я не понимаю эту команду 🥺. \nВведите /menu")


    except Exception as e:
        logging.error(f"Error in handle_user_input handler: {e}")
        await update.message.reply_text('Произошла ошибка при обработке вашего запроса. Пожалуйста, попробуйте позже.')
        

async def handle_new_ad_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        if not update.message:
            logging.info('Received non-message update: %s', update)
            return

        user_id = update.message.from_user.id
        message_text = update.message.text

        await update_user_status_based_on_admin(user_id)
        user_status = await get_user_status(user_id)
        if user_status == 'no_user':
            await update.message.reply_text('Вы не подписаны на канал. Пожалуйста, подпишитесь, чтобы продолжить.')
            return

        if 'car_data' not in context.user_data:
            context.user_data['car_data'] = {}

        car_data = context.user_data['car_data']
        step = context.user_data.get('step', 'make')

        steps = {
            'make': '🚗 Марка авто (например, Ford, Toyota):',
            'model': '📋 Модель (например, Focus, Corolla):',
            'year': '📅 Год выпуска (или /skip):',
            'price': '💲 Цена (в рублях):',
            'mileage': '🛣️ Пробег (в км, или /skip):',
            'place': '📍 Местонахождение (город или /skip):',
            'description': '📝 Краткое описание (состояние, особенности или /skip):'
        }

        if message_text.lower() != '/skip':
            car_data[step] = message_text
            logging.info(f"User {update.message.from_user.id} entered {step}: {message_text}")
        else:
            car_data[step] = "Не указано"
            logging.info(f"User {update.message.from_user.id} skipped {step}")

        step_keys = list(steps.keys())
        current_index = step_keys.index(step)
        next_step = step_keys[current_index + 1] if current_index + 1 < len(step_keys) else None

        if next_step:
            context.user_data['step'] = next_step
            await update.message.reply_text(steps[next_step])
            logging.info(f"Prompting user {update.message.from_user.id} for {next_step}")
        else:
            make = car_data.get('make')
            model = car_data.get('model')
            year = car_data.get('year')
            mileage = car_data.get('mileage')
            price = car_data.get('price')
            place = car_data.get('place')
            description = car_data.get('description')

            car_id = await add_car(user_id, make, model, year, mileage, price, place, description)
            logging.info(f"Car ad created with ID {car_id} for user {user_id}")

            context.user_data['car_id'] = car_id
            context.user_data['car_info'] = car_data
            context.user_data['photo_count'] = 0
            context.user_data['user_id'] = user_id
            del context.user_data['car_data']
            del context.user_data['step']
            context.user_data['in_ad_form'] = False

            message = await update.message.reply_text(
                'Хотите ли приложить фото к объявлению?',
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("✅ Да", callback_data="add_photos_")],
                    [InlineKeyboardButton("❌ Нет", callback_data="finish_photos_")]
                ])
            )
            context.user_data['last_message_id'] = message.message_id
            logging.info(f"Prompted user {update.message.from_user.id} to add photos")

    except Exception as e:
        logging.error(f"Error in handle_new_ad_input handler: {e}")
        await update.message.reply_text('Произошла ошибка при обработке вашего запроса. Пожалуйста, попробуйте позже.')


