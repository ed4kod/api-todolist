from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton


def task_keyboard(task) -> InlineKeyboardMarkup:
    buttons = [
        InlineKeyboardButton(
            text="✅ Выполнено" if not task.done else "❌ Не выполнено",
            callback_data=f"{'done' if not task.done else 'undone'}_{task.id}"
        ),
        InlineKeyboardButton(
            text="✏️ Изменить",
            callback_data=f"edit_{task.id}"
        ),
        InlineKeyboardButton(
            text="🗑 Удалить",
            callback_data=f"delete:{task.id}"
        )
    ]
    return InlineKeyboardMarkup(inline_keyboard=[buttons])



from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_menu_keyboard():
    buttons = [
        KeyboardButton(text="/get_tasks"),
        KeyboardButton(text="➕ Добавить задачу"),
        KeyboardButton(text="/start"),
    ]
    return ReplyKeyboardMarkup(keyboard=[buttons], resize_keyboard=True)

