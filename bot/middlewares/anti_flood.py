import time
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from collections import defaultdict


class AntiFloodMiddleware(BaseMiddleware):
    def __init__(self, rate_limit: float = 1.0):
        self.rate_limit = rate_limit
        self.last_time = defaultdict(float)

    async def __call__(self, handler, event: TelegramObject, data: dict):
        user_id = getattr(event.from_user, "id", None)
        if user_id is None:
            return await handler(event, data)

        now = time.time()
        if now - self.last_time[user_id] < self.rate_limit:
            if hasattr(event, "answer"):
                await event.answer("⏱ Не торпись, голубчик!", show_alert=True)
            return

        self.last_time[user_id] = now
        return await handler(event, data)
