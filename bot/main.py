from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from bot.handlers import routers
from bot.middlewares.anti_flood import AntiFloodMiddleware  # <--- добавили

from config import settings

bot = Bot(
    token=settings.telegram_bot_token,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher()

dp.message.middleware(AntiFloodMiddleware(rate_limit=1.5))
dp.callback_query.middleware(AntiFloodMiddleware(rate_limit=1.0))


def setup_handlers(dp: Dispatcher):
    for router in routers:
        dp.include_router(router)


setup_handlers(dp)
