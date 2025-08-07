from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from aiogram.types import InlineKeyboardMarkup
from api.crud import delete_task
from bot.keyboards import task_keyboard
from api.models import Task


def format_task_message(task):
    text = f"🗂 Задача # {task.id}\n\n"
    text += f"📝 {task.title}\n"

    if not task.done:
        text += "\n⏳ Статус: не выполнена"
    elif task.done and task.done_by:
        text += f"\n✅ Выполнил: @{task.done_by}"

    return text


async def get_task(db: AsyncSession, task_id: int) -> Task | None:
    result = await db.execute(select(Task).where(Task.id == task_id))
    return result.scalars().first()


async def get_task_text(db: AsyncSession, task_id: int) -> tuple[str | None, InlineKeyboardMarkup | None]:
    task = await get_task(db, task_id)
    if not task:
        return None, None
    return format_task_message(task), task_keyboard(task)


async def get_all_tasks(db: AsyncSession, user_id: int) -> list[Task]:
    result = await db.execute(select(Task).where(Task.user_id == user_id))
    return list(result.scalars().all())


async def create_task(db: AsyncSession, title: str, user_id: int) -> Task:
    task = Task(title=title, user_id=user_id)
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


async def update_task_title(db: AsyncSession, task_id: int, new_title: str):
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        return None
    task.title = new_title
    await db.commit()
    await db.refresh(task)
    return task


async def delete_current_task(db: AsyncSession, task_id: int) -> Optional[Task]:
    return await delete_task(db, task_id)


