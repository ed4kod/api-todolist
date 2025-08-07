import json
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def task_keyboard(task):
    buttons = [
        InlineKeyboardButton(
            text="❌ Отменить" if task.done else "✅ Выполнить",
            callback_data=f"{'undone' if task.done else 'done'}_{task.id}"
        ),
        InlineKeyboardButton(text="✏️ Редактировать", callback_data=f"edit_{task.id}"),
        InlineKeyboardButton(text="🗑 Удалить", callback_data=f"delete:{task.id}")
    ]
    return InlineKeyboardMarkup(inline_keyboard=[buttons])  # или [[b] for b in buttons]


def final_action_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="➕ Добавить", callback_data="add_task"),
        InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_tasks")
    ]])


def markup_to_json(markup: InlineKeyboardMarkup) -> str:
    return json.dumps({
        "inline_keyboard": [
            [button.to_python() for button in row]
            for row in markup.inline_keyboard
        ]
    }, sort_keys=True)


def markups_equal(m1: InlineKeyboardMarkup, m2: InlineKeyboardMarkup) -> bool:
    return markup_to_json(m1) == markup_to_json(m2)
