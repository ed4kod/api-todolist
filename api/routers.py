from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from api import crud, schemas
from api.dependencies import get_db

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"]
)


@router.get(
    "/{task_id}",
    response_model=schemas.TaskInDB,
    summary="Получить задачу по ID"
)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = crud.get_task(db, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    return task


@router.get(
    "/",
    response_model=list[schemas.TaskInDB],
    summary="Получить список всех задач")
def get_all_tasks(db: Session = Depends(get_db)):
    return crud.get_tasks(db)


@router.post(
    "/",
    response_model=schemas.TaskInDB,
    status_code=201,
    summary="Создать задачу"
)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    return crud.create_task(db, task)


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить задачу"
)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = crud.delete_task(db, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    return None

@router.put(
    "/{task_id}",
    response_model=schemas.TaskInDB,
    summary="Обновить задачу",
    status_code=status.HTTP_200_OK
)
def update_task(
    task_id: int,
    task_data: schemas.TaskUpdate,
    db: Session = Depends(get_db)
):
    task = crud.update_task(db, task_id, task_data)
    if task is None:
        raise HTTPException(
            status_code=404, detail= "Задача не найдена")
    return task

