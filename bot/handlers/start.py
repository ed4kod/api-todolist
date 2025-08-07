import asyncio

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from .common import safe_delete
from bot.handlers.task_view import handle_get_all_tasks

router = Router()

@router.message(Command("start"))
async def handle_start(message: Message, state: FSMContext):
    # Отправляем стикер
    msg_sticker = await message.answer_sticker(
        "CAACAgIAAxkBAAEPGJpolR7VUjpv1CRGM6-2I22ipnzg-gACU2sAAq1WkEjC846dllxnvjYE"
    )

    # Ждём 2 секунды
    await asyncio.sleep(2)

    # Удаляем стикер
    try:
        await message.chat.delete_message(msg_sticker.message_id)
    except Exception:
        pass

    # Делаем небольшую паузу — например 1 секунда
    await asyncio.sleep(1)

    # Показываем задачи
    await handle_get_all_tasks(message, state)

    # Удаляем командное сообщение пользователя, чтобы чат был чище
    await safe_delete(message)
