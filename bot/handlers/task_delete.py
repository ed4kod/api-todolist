import asyncio
from aiogram import Router
from aiogram.types import CallbackQuery
from api.dependencies import get_async_session
from bot.services import delete_task

router = Router()


@router.callback_query(lambda c: c.data.startswith("delete:"))
async def handle_delete(callback: CallbackQuery):
    task_id = int(callback.data.split(":")[1])
    async with get_async_session() as db:
        task = await delete_task(db, task_id)

    if task:
        await callback.message.edit_text("🗑 Задача удалена")
        await asyncio.sleep(1)
        await callback.message.delete()
    else:
        await callback.answer("❌ Задача не найдена", show_alert=True)
