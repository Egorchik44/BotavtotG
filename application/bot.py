import logging
import os
import asyncio
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler, Defaults
import tracemalloc

tracemalloc.start()

from application.handlers.start import start
from application.handlers.newad import new_ad
from application.handlers.profile import user_profile
from application.handlers.photo import handle_photo
from application.handlers.message import handle_user_input
from application.utils.menu import show_main_menu
from application.handlers.admin_handler import view_ad, mark_as_sold
from application.handlers.user_ads import my_ad
from application.handlers.button_callback import button_callback
from application.utils.database_update import run_updates
from application.button.button_menu import handle_text_input
from application.utils.rate_limiter import rate_limit_decorator
from application.db.database import init_db

load_dotenv()
token = os.getenv('BOT_TOKEN')

logging.basicConfig(filename='bot.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def periodic_task(interval_minutes):
    while True:
        try:
            await run_updates()
            logging.info("Periodic update completed successfully.")
        except Exception as e:
            logging.error(f"Error in periodic task: {e}")
        await asyncio.sleep(interval_minutes * 60)


def main() -> None:
    logging.info("Starting bot...")
    init_db()


    defaults = Defaults(parse_mode='HTML')
    app = ApplicationBuilder().token(token).defaults(defaults).build()

    app.add_handler(CommandHandler("start", rate_limit_decorator(start)))
    app.add_handler(CommandHandler("newad", rate_limit_decorator(new_ad)))
    app.add_handler(CommandHandler("profile", rate_limit_decorator(user_profile)))
    app.add_handler(CommandHandler("menu", rate_limit_decorator(show_main_menu)))
    app.add_handler(CommandHandler("view", rate_limit_decorator(view_ad)))
    app.add_handler(CommandHandler("skip", rate_limit_decorator(handle_user_input)))
    app.add_handler(CommandHandler("mark_as_sold", rate_limit_decorator(mark_as_sold)))
    app.add_handler(CommandHandler("myad", rate_limit_decorator(my_ad)))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_input))
    app.add_handler(MessageHandler(filters.PHOTO, rate_limit_decorator(handle_photo)))
    app.add_handler(CallbackQueryHandler(rate_limit_decorator(button_callback)))

    # Start periodic task
    interval_minutes = 10
    loop = asyncio.get_event_loop()
    loop.create_task(periodic_task(interval_minutes))

    # Start the bot
    app.run_polling()


if __name__ == '__main__':
    main()
