from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from bot.keyboards import main_menu_keyboard
from .common import safe_delete
from aiogram.fsm.context import FSMContext

router = Router()


@router.message(Command("start"))
async def handle_start(message: Message, state: FSMContext):
    msg = await message.answer("Привет! Выбери команду:", reply_markup=main_menu_keyboard())
    data = await state.get_data()
    all_ids = data.get("all_bot_message_ids", [])
    all_ids.append(msg.message_id)
    await state.update_data(all_bot_message_ids=all_ids)
    await safe_delete(message)
