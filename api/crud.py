from typing import Optional, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from api import schemas
from .models import Task


async def get_task(db: AsyncSession, task_id: int) -> Optional[Task]:
    result = await db.execute(select(Task).where(Task.id == task_id))
    return result.scalar_one_or_none()


async def get_tasks(db: AsyncSession, user_id: int) -> list[Task]:
    result = await db.execute(select(Task).where(Task.user_id == user_id))
    return list(result.scalars().all())


async def create_task(db: AsyncSession, task: schemas.TaskCreate) -> Task:
    db_task = Task(
        title=task.title,
        user_id=task.user_id,  # ⬅ добавили user_id
        done_by=task.done_by if hasattr(task, "done_by") else None  # опционально
    )
    db.add(db_task)
    await db.commit()
    await db.refresh(db_task)
    return db_task


async def update_task(db: AsyncSession, task_id: int, data: schemas.TaskUpdate) -> Optional[Task]:
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        return None

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(task, key, value)

    await db.commit()
    await db.refresh(task)
    return task


async def delete_task(db: AsyncSession, task_id: int) -> Optional[Task]:
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if task:
        await db.delete(task)
        await db.commit()
    return task
