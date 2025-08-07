from aiogram import Router
from aiogram.types import CallbackQuery
from api.dependencies import get_async_session
from bot.services import get_task, format_task_message, task_keyboard

router = Router()


@router.callback_query(lambda c: c.data.startswith("done_") or c.data.startswith("undone_"))
async def handle_toggle_done(callback: CallbackQuery):
    action, task_id_str = callback.data.split("_")
    task_id = int(task_id_str)
    user = callback.from_user

    async with get_async_session() as db:
        task = await get_task(db, task_id)
        if not task:
            await callback.answer("Задача не найдена", show_alert=True)
            return

        if action == "done":
            task.done = True
            task.done_by = user.username or f"{user.first_name} {user.last_name or ''}".strip()
        else:
            task.done = False
            task.done_by = None

        await db.commit()
        await db.refresh(task)

    new_text = format_task_message(task)
    new_markup = task_keyboard(task)

    if new_text != callback.message.text or callback.message.reply_markup != new_markup:
        await callback.message.edit_text(new_text, reply_markup=new_markup)

    await callback.answer("Статус задачи обновлён")
