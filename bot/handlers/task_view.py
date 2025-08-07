import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from bot.services import get_task_text, format_task_message
from bot.keyboards import task_keyboard, final_action_keyboard
from api.crud import get_tasks
from api.dependencies import get_async_session
from aiogram.fsm.context import FSMContext

router = Router()
logger = logging.getLogger(__name__)


@router.message(Command("get_task"))
async def handle_get_task(message: Message):
    try:
        parts = message.text.split()
        if len(parts) < 2:
            await message.answer("❗ Укажи ID задачи, например: /get_task 123")
            return

        task_id = int(parts[1])
        async with get_async_session() as db:
            title, keyboard = await get_task_text(db, task_id)

        if title:
            await message.answer(title, reply_markup=keyboard)
        else:
            await message.answer("❌ Задача не найдена.")

    except ValueError:
        await message.answer("❗ ID задачи должен быть числом.")
    except Exception as e:
        logger.error(f"Ошибка в handle_get_task: {e}")
        await message.answer("❗ Ошибка при обработке запроса.")


@router.message(lambda msg: msg.text == "📋 Показать задачи")
async def handle_show_tasks(message: Message, state: FSMContext):
    await handle_get_all_tasks(message, state)


@router.callback_query(F.data == "refresh_tasks")
async def handle_refresh_tasks(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await handle_get_all_tasks(callback.message, state, user_id=callback.from_user.id)


async def handle_get_all_tasks(message: Message, state: FSMContext, user_id: int | None = None):
    if user_id is None:
        user_id = message.from_user.id

    data = await state.get_data()
    to_delete = data.get("all_bot_message_ids", [])
    for msg_id in to_delete:
        try:
            await message.chat.delete_message(msg_id)
        except Exception:
            pass

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

        await state.update_data(all_bot_message_ids=new_message_ids, displayed_tasks=displayed_tasks)
        try:
            await message.delete()
        except Exception:
            pass

    except Exception as e:
        logger.error(f"Ошибка в handle_get_all_tasks: {e}")
        await message.answer("❗ Произошла ошибка при получении задач. Попробуй позже.")
