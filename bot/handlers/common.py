import asyncio
import logging
from aiogram.types import Message

logger = logging.getLogger(__name__)


async def clear_old_messages(message: Message, state):
    data = await state.get_data()
    all_ids = data.get("all_bot_message_ids", [])
    keep_ids = []

    for msg_id in all_ids:
        try:
            await message.chat.delete_message(msg_id)
        except Exception as e:
            if "message to delete not found" not in str(e).lower():
                logger.warning(f"Не удалось удалить сообщение id={msg_id}: {e}")
                keep_ids.append(msg_id)

    await state.update_data(all_bot_message_ids=keep_ids)


async def safe_delete(message: Message, delay: float = 0):
    try:
        if delay:
            await asyncio.sleep(delay)
        await message.delete()
    except Exception as e:
        logger.warning(f"Не удалось удалить сообщение (id={message.message_id}): {e}")


async def safe_delete_message(chat, message_id):
    try:
        await chat.delete_message(message_id)
    except Exception as e:
        if "message to delete not found" not in str(e).lower():
            logger.warning(f"Не удалось удалить сообщение id={message_id}: {e}")
