import time
import asyncio

class RateLimiter:
    def __init__(self, rate, per):
        self.rate = rate  # tokens added per period
        self.per = per  # period in seconds
        self.tokens = rate
        self.updated_at = time.time()

    async def acquire(self, update, context):
        now = time.time()
        elapsed = now - self.updated_at
        self.updated_at = now
        self.tokens += elapsed * (self.rate / self.per)
        if self.tokens > self.rate:
            self.tokens = self.rate

        if self.tokens >= 1:
            self.tokens -= 1
            return True
        else:
            await update.message.reply_text("Превышен лимит запросов. Пожалуйста, попробуйте позже.")
            return False

def rate_limit_decorator(func):
    async def wrapper(update, context, *args, **kwargs):
        if await RateLimiter(10, 1).acquire(update, context):
            return await func(update, context, *args, **kwargs)
    return wrapper