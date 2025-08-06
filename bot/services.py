from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from aiogram.types import InlineKeyboardMarkup

from api.crud import delete_task
from bot.keyboards import task_keyboard
from api.models import Task


def format_task_message(task: Task) -> str:
    status = "✅ Выполнено" if task.done else "❌ Не выполнено"
    return f"#{task.id} — {task.title}\n📌 Статус: {status}"


async def get_task(db: AsyncSession, task_id: int) -> Task | None:
    result = await db.execute(select(Task).where(Task.id == task_id))
    return result.scalars().first()


async def get_task_text(db: AsyncSession, task_id: int) -> tuple[str | None, InlineKeyboardMarkup | None]:
    task = await get_task(db, task_id)
    if not task:
        return None, None
    return format_task_message(task), task_keyboard(task)


async def get_all_tasks(db: AsyncSession) -> list[Task]:
    result = await db.execute(select(Task))
    return list(result.scalars().all())


async def create_task(db: AsyncSession, title: str) -> Task:
    task = Task(title=title)
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


async def delete_current_task(db: AsyncSession, task_id: int) -> Optional[Task]:
    return await delete_task(db, task_id)
