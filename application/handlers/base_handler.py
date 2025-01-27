from telegram.ext import ContextTypes
from telegram import Update

class BaseHandler:
    def __init__(self):
        pass

    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        raise NotImplementedError("Subclasses must implement handle method")