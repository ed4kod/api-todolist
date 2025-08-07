import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from bot.services import format_task_message
from bot.keyboards import task_keyboard, final_action_keyboard
from api.crud import get_tasks
from api.dependencies import get_async_session
from aiogram.fsm.context import FSMContext

router = Router()
logger = logging.getLogger(__name__)

import asyncio


async def handle_get_all_tasks(event: Message | CallbackQuery, state: FSMContext, user_id: int | None = None):
    message = event.message if isinstance(event, CallbackQuery) else event
    user_id = user_id or message.from_user.id

    data = await state.get_data()
    old_task_ids = data.get("task_message_ids", [])

    delete_tasks = [
        message.bot.delete_message(chat_id=message.chat.id, message_id=msg_id)
        for msg_id in old_task_ids
    ]
    if delete_tasks:
        await asyncio.gather(*delete_tasks, return_exceptions=True)

    # Обнуляем список сообщений в состоянии, чтобы не копились старые ID
    await state.update_data(task_message_ids=[])

    try:
        async with get_async_session() as db:
            tasks = await get_tasks(db, user_id)

        new_message_ids = []
        displayed_tasks = {}

        if not tasks:
            msg = await message.answer("📭 У тебя пока нет задач.")
            new_message_ids.append(msg.message_id)
        else:
            for task in tasks:
                sent = await message.answer(
                    format_task_message(task),
                    reply_markup=task_keyboard(task)
                )
                new_message_ids.append(sent.message_id)
                displayed_tasks[task.id] = sent.message_id

        final = await message.answer("🛠 Инструменты", reply_markup=final_action_keyboard())
        new_message_ids.append(final.message_id)

        # Обновляем состояние новыми ID сообщений
        await state.update_data(
            task_message_ids=new_message_ids,
            displayed_tasks=displayed_tasks
        )

        if isinstance(event, Message):
            try:
                await event.delete()
            except Exception:
                pass

    except Exception as e:
        logger.error(f"Ошибка в handle_get_all_tasks: {e}")
        await message.answer("❗ Произошла ошибка при получении задач. Попробуй позже.")


@router.message(F.text == "📋 Показать задачи")
async def handle_show_tasks(message: Message, state: FSMContext):
    await handle_get_all_tasks(message, state)


@router.callback_query(F.data == "refresh_tasks")
async def handle_refresh_tasks(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await handle_get_all_tasks(callback, state, user_id=callback.from_user.id)
