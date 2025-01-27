from telegram.ext import ContextTypes
from telegram import Update, ReplyKeyboardRemove

async def new_ad(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    context.user_data['in_ad_form'] = True
    context.user_data['car_data'] = {}
    context.user_data['step'] = 'make'

    await update.message.reply_text(
        'Заполните форму, пожалуйста\nЕсли не хотите указывать какой-либо параметр, нажмите /skip',
        reply_markup=ReplyKeyboardRemove()
    )
    await update.message.reply_text('Введите марку 🚗')
