import asyncio
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from bot.states import AddTaskStates
from api.dependencies import get_async_session
from bot.services import create_task
from .task_view import handle_get_all_tasks

router = Router()


@router.message(lambda msg: msg.text == "➕ Добавить задачу")
async def start_add_task(message: Message, state: FSMContext):
    msg = await message.answer("✍️ Просто напиши текст задачи")
    await state.set_state(AddTaskStates.waiting_for_task_text)
    await state.update_data(
        invite_message_id=msg.message_id,
        trigger_message_id=message.message_id
    )


@router.callback_query(F.data == "add_task")
async def handle_add_task_callback(callback: CallbackQuery, state: FSMContext):
    msg = await callback.message.answer("✍️ Просто напиши текст задачи")
    await state.set_state(AddTaskStates.waiting_for_task_text)
    await state.update_data(
        invite_message_id=msg.message_id,
        trigger_message_id=callback.message.message_id
    )
    await callback.answer()


@router.message(AddTaskStates.waiting_for_task_text)
async def process_task_text(message: Message, state: FSMContext):
    data = await state.get_data()
    invite_id = data.get("invite_message_id")
    trigger_id = data.get("trigger_message_id")

    task_title = message.text.strip()
    if not task_title:
        await message.answer("❗ Текст задачи не может быть пустым.")
        return

    try:
        async with get_async_session() as db:
            task = await create_task(db, task_title, message.from_user.id)
        msg = await message.answer(f"✅ Задача создана: #{task.id} — {task.title}")
        await asyncio.sleep(1)
        await msg.delete()
    except Exception:
        await message.answer("❗ Не удалось создать задачу.")
    finally:
        for mid in [invite_id, trigger_id, message.message_id]:
            if mid:
                try:
                    await message.chat.delete_message(mid)
                except Exception:
                    pass

        # Вызываем обновление задач *до* очистки состояния
        await handle_get_all_tasks(message, state)

        # Теперь можно очистить состояние или оставить task_message_ids, если нужно
        # await state.clear()  # либо
        # await state.update_data(task_message_ids=[])
