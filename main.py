import asyncio
import uvicorn
from api.main import app          # FastAPI приложение
from bot.main import dp, bot      # aiogram Dispatcher и Bot

async def start_bot():
    await dp.start_polling(bot)

async def start_api():
    config = uvicorn.Config(app=app, host="0.0.0.0", port=8000, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()

async def main():
    await asyncio.gather(
        start_api(),
        start_bot(),
    )

if __name__ == "__main__":
    asyncio.run(main())
