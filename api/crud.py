from typing import Optional
from sqlalchemy.orm import Session
from api import models, schemas
from .models import Task


def get_task(db: Session, task_id: int) -> Optional[Task]:
    return db.query(Task).filter(Task.id == task_id).first()


def get_tasks(db: Session) -> list[type[Task]]:
    return db.query(Task).all()


def create_task(db: Session, task: schemas.TaskCreate) -> Task:
    db_task = Task(title=task.title)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def update_task(db: Session, task_id: int, data: schemas.TaskUpdate) -> Optional[models.Task]:
    task = get_task(db, task_id)
    if not task:
        return None
    update_data = data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)
    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, task_id: int) -> Optional[Task]:
    task = get_task(db, task_id)
    if task:
        db.delete(task)
        db.commit()
    return task
