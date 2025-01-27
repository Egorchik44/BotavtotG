import os
import logging
from dotenv import load_dotenv
from telegram import Bot
from telegram.error import TelegramError
from application.db.database_users import update_user_status


load_dotenv()

token = os.getenv('BOT_TOKEN')
channel = os.getenv('CHANNEL_ID')

async def is_admin(user_id: int) -> bool:
    bot = Bot(token=token)
    try:
        chat_admins = await bot.get_chat_administrators(channel)
        admin_ids = [admin.user.id for admin in chat_admins]
        is_user_admin = user_id in admin_ids
        return is_user_admin
    except TelegramError as e:
        logging.error(f'Error when getting the list of administrators: {e}')
        return False

async def is_subscribed(user_id: int) -> bool:
    bot = Bot(token=token)
    try:
        user_status = await bot.get_chat_member(channel, user_id)
        return user_status.status in ['member', 'administrator', 'creator']
    except TelegramError as e:
        logging.error(f'Error checking the subscription of the user {user_id} to the channel: {e}')
        return False

async def update_user_status_based_on_admin(user_id: int):
    if await is_admin(user_id):
        await update_user_status(user_id, 'admin')
    elif await is_subscribed(user_id):
        await update_user_status(user_id, 'user')
    else:
        await update_user_status(user_id, 'no_user')

