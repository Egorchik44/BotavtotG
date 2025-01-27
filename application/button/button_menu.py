from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters


from application.handlers.newad import new_ad
from application.handlers.profile import user_profile
from application.handlers.user_ads import my_ad
from application.handlers.message import  handle_user_input
from application.handlers.admin_handler import view_ad, mark_as_sold
from application.utils.menu import show_main_menu


CHOOSING, TYPING_NUMBER = range(2)

async def handle_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text

    if context.user_data.get('waiting_for_number'):
        choice = context.user_data.get('choice')
        context.user_data['waiting_for_number'] = False
        
        try:
            number = int(text)
            context.args = [str(number)]
            
            if choice == 'view_ad':
                await view_ad(update, context)
            elif choice == 'mark_as_sold':
                await mark_as_sold(update, context)
        except ValueError:
            await update.message.reply_text("Пожалуйста, введите корректный номер объявления.")
        
        await show_main_menu(update, context)
        return CHOOSING

    if text == "Новое объявление📝":
        await new_ad(update, context)
    elif text == "Профиль👤":
        await user_profile(update, context)
    elif text == "Мои объявления🗂":
        await my_ad(update, context)
    elif text == "Просмотр объявлений⚙️":
        context.user_data['choice'] = 'view_ad'
        context.user_data['waiting_for_number'] = True
        await update.message.reply_text("Введите номер объявления для просмотра:")
        return TYPING_NUMBER
    elif text == "Снятие с продажи⚙️":
        context.user_data['choice'] = 'mark_as_sold'
        context.user_data['waiting_for_number'] = True
        await update.message.reply_text("Введите номер объявления для снятия с продажи:")
        return TYPING_NUMBER
    else:
        await handle_user_input(update, context)
    
    return CHOOSING
