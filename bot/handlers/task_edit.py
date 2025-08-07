import logging
from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from bot.states import EditTaskStates
from api.dependencies import get_async_session
from bot.services import update_task_title, get_task, format_task_message, task_keyboard
from .common import safe_delete

router = Router()
logger = logging.getLogger(__name__)


@router.callback_query(lambda c: c.data.startswith("edit_"))
async def start_edit_task(callback: CallbackQuery, state: FSMContext):
    task_id = int(callback.data.split("_")[1])
    prompt_msg = await callback.message.answer("✏️ Отправь новый текст для задачи")

    await state.set_state(EditTaskStates.waiting_for_new_title)
    await state.update_data(
        task_id=task_id,
        message_id=callback.message.message_id,
        prompt_message_id=prompt_msg.message_id
    )
    await callback.answer()


@router.message(EditTaskStates.waiting_for_new_title)
async def process_new_title(message: Message, state: FSMContext):
    data = await state.get_data()
    task_id = data.get("task_id")
    msg_id = data.get("message_id")
    prompt_id = data.get("prompt_message_id")
    new_title = message.text.strip()

    if not new_title:
        await message.answer("❗ Текст задачи не может быть пустым.")
        return

    try:
        async with get_async_session() as db:
            task = await update_task_title(db, task_id, new_title)
            if not task:
                await message.answer("❌ Задача не найдена.")
                return

        await message.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=msg_id,
            text=format_task_message(task),
            reply_markup=task_keyboard(task)
        )
        await safe_delete(message)
        await message.bot.delete_message(chat_id=message.chat.id, message_id=prompt_id)

    except Exception as e:
        logger.error(f"Ошибка при обновлении задачи {task_id}: {e}")
        await message.answer("❗ Не удалось обновить задачу.")
    finally:
        await state.clear()
