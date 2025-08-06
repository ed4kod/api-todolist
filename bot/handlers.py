import logging
from aiogram.filters import Command
import asyncio

from aiogram.types import Message

from api.crud import get_tasks
from bot.services import get_task_text, format_task_message, create_task, delete_task, get_task
from bot.keyboards import task_keyboard, main_menu_keyboard
from config import setup_logging
from api.dependencies import get_async_session
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram import types, F, Router

setup_logging()
router = Router()
logger = logging.getLogger(__name__)


class EditTaskStates(StatesGroup):
    waiting_for_new_title = State()


class AddTaskStates(StatesGroup):
    waiting_for_task_text = State()


@router.message(Command("start"))
async def handle_start(message: types.Message, state: FSMContext):
    try:
        msg = await message.answer(
            "Привет! Выбери команду:",
            reply_markup=main_menu_keyboard()
        )
        await state.update_data(start_message_id=msg.message_id)

        try:
            await message.delete()
        except Exception as e:
            logger.warning(f"Не удалось удалить /start сообщение: {e}")

    except Exception as e:
        logger.error(f"Ошибка в handle_start: {e}")


@router.message(Command("get_task"))
async def handle_get_task(message: types.Message):
    try:
        parts = message.text.split()
        if len(parts) < 2:
            await message.answer("❗ Укажи ID задачи после команды, например: /get_task 123")
            return

        task_id = int(parts[1])

        async with get_async_session() as db:
            title, keyboard = await get_task_text(db, task_id)
            if title is None:
                await message.answer(f"Задача с ID {task_id} не найдена.")
            else:
                await message.answer(title, reply_markup=keyboard)
    except ValueError:
        await message.answer("❗ ID задачи должен быть числом, например: /get_task 123")
    except Exception as e:
        logger.error(f"Ошибка в handle_get_task: {e}")
        await message.answer("❗ Произошла ошибка при обработке запроса. Попробуйте позже.")


@router.message(Command("get_tasks"))
async def handle_get_all_tasks(message: types.Message, state: FSMContext):
    data = await state.get_data()
    task_message_ids = data.get("task_message_ids", [])
    for msg_id in task_message_ids:
        try:
            await message.chat.delete_message(msg_id)
        except Exception as e:
            # Игнорируем ошибку, если сообщение уже удалено
            if "message to delete not found" not in str(e).lower():
                logger.warning(f"Не удалось удалить старое сообщение со списком задач: {e}")
    try:
        async with get_async_session() as db:
            tasks = await get_tasks(db)
        if not tasks:
            msg = await message.answer("Задач нет.")
            await state.update_data(task_message_ids=[msg.message_id])
            # Удаляем команду пользователя после отправки
            try:
                await message.delete()
            except Exception:
                pass
            return
        new_message_ids = []
        for task in tasks:
            text = format_task_message(task)
            keyboard = task_keyboard(task)
            sent_msg = await message.answer(text, reply_markup=keyboard)
            new_message_ids.append(sent_msg.message_id)
        await state.update_data(task_message_ids=new_message_ids)
        try:
            await message.delete()
        except Exception:
            pass
    except Exception as e:
        logger.error(f"Ошибка в handle_get_all_tasks: {e}")
        await message.answer("❗ Произошла ошибка при получении задач. Попробуйте позже.")


@router.message(lambda message: message.text == "➕ Добавить задачу")
async def start_add_task(message: types.Message, state: FSMContext):
    msg = await message.answer("✍️ Просто напиши текст задачи")
    await state.set_state(AddTaskStates.waiting_for_task_text)
    await state.update_data(
        invite_message_id=msg.message_id,
        trigger_message_id=message.message_id
    )


@router.message(AddTaskStates.waiting_for_task_text)
async def process_task_text(message: types.Message, state: FSMContext):
    data = await state.get_data()
    invite_message_id = data.get("invite_message_id")
    trigger_message_id = data.get("trigger_message_id")

    task_title = message.text.strip()
    if not task_title:
        await message.answer("❗ Текст задачи не может быть пустым. Попробуй еще раз.")
        return

    try:
        async with get_async_session() as db:
            task = await create_task(db, task_title)
            msg = await message.answer(f"✅ Задача создана: #{task.id} — {task.title}")
            await asyncio.sleep(1)
            await msg.delete()
    except Exception as e:
        logger.error(f"Ошибка при создании задачи: {e}")
        await message.answer("❗ Произошла ошибка при создании задачи. Попробуйте позже.")

    try:
        if invite_message_id:
            await message.chat.delete_message(invite_message_id)
        if trigger_message_id:
            await message.chat.delete_message(trigger_message_id)
        await message.delete()
    except Exception as e:
        logger.warning(f"Не удалось удалить сообщение: {e}")

    # Сперва обновляем список (удаляем старый + выводим новый)
    await handle_get_all_tasks(message, state)

    # Потом чистим состояние
    await state.clear()


@router.callback_query(F.data.startswith("delete:"))
async def handle_delete(callback: types.CallbackQuery):
    task_id = int(callback.data.split(":")[1])
    async with get_async_session() as db:
        task = await delete_task(db, task_id)
    if task:
        await callback.message.edit_text("🗑 Задача удалена")
        await asyncio.sleep(1)
        await callback.message.delete()
    else:
        await callback.answer("❌ Задача не найдена", show_alert=True)


@router.callback_query(F.data.startswith("done_") | F.data.startswith("undone_"))
async def handle_toggle_done(callback: types.CallbackQuery):
    action, task_id_str = callback.data.split("_")
    task_id = int(task_id_str)

    async with get_async_session() as db:
        task = await get_task(db, task_id)
        if not task:
            await callback.answer("Задача не найдена", show_alert=True)
            return

        task.done = True if action == "done" else False
        await db.commit()
        await db.refresh(task)

        text = format_task_message(task)
        keyboard = task_keyboard(task)
        await callback.message.edit_text(text, reply_markup=keyboard)
        await callback.answer("Статус задачи обновлен")


@router.callback_query(F.data.startswith("edit_"))
async def start_edit_task(callback: types.CallbackQuery, state: FSMContext):
    task_id = int(callback.data.split("_")[1])
    await state.update_data(task_id=task_id)
    await callback.message.answer("✏️ Отправь новый текст для задачи")
    await state.set_state(EditTaskStates.waiting_for_new_title)
    await callback.answer()

    @router.message(AddTaskStates.waiting_for_task_text)
    async def process_task_text(message: types.Message, state: FSMContext):
        data = await state.get_data()
        invite_message_id = data.get("invite_message_id")

        task_title = message.text.strip()
        if not task_title:
            err = await message.answer("❗ Текст задачи не может быть пустым. Попробуй еще раз.")
            await safe_delete(err, delay=3)
            return
        try:
            async with get_async_session() as db:
                task = await create_task(db, task_title)
            notify = await message.answer(f"✅ Задача создана: #{task.id} — {task.title}")
            await safe_delete(notify, delay=2)
        except Exception as e:
            logger.error(f"Ошибка при создании задачи: {e}")
            err = await message.answer("❗ Произошла ошибка при создании задачи. Попробуйте позже.")
            await safe_delete(err, delay=3)
        if invite_message_id:
            try:
                await message.chat.delete_message(invite_message_id)
            except Exception as e:
                logger.warning(f"Не удалось удалить invite-сообщение: {e}")

        await safe_delete(message)
        await state.clear()


async def safe_delete(message: Message, delay: float = 0):
    try:
        if delay:
            await asyncio.sleep(delay)
        await message.delete()
    except Exception as e:
        logger.warning(f"Не удалось удалить сообщение (id={message.message_id}): {e}")
