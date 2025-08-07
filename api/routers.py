from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from api import crud, schemas
from api.dependencies import get_async_session

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"]
)


@router.get(
    "/{task_id}",
    response_model=schemas.TaskInDB,
    response_model_exclude_unset=True,
    summary="Получить задачу по ID"
)
async def get_task(task_id: int, db: AsyncSession = Depends(get_async_session)):
    task = await crud.get_task(db, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    return task


@router.get(
    "/",
    response_model=list[schemas.TaskInDB],
    summary="Получить список всех задач"
)
async def get_all_tasks(
    db: AsyncSession = Depends(get_async_session),
    user_id: int | None = Query(default=None, description="ID пользователя (опционально)")
):
    return await crud.get_tasks(db, user_id=user_id)


@router.post(
    "/",
    response_model=schemas.TaskInDB,
    status_code=201,
    summary="Создать задачу"
)
async def create_task(task: schemas.TaskCreate, db: AsyncSession = Depends(get_async_session)):
    return await crud.create_task(db, task)


@router.put(
    "/{task_id}",
    response_model=schemas.TaskInDB,
    summary="Обновить задачу",
    status_code=status.HTTP_200_OK
)
async def update_task(
    task_id: int,
    task_data: schemas.TaskUpdate,
    db: AsyncSession = Depends(get_async_session)
):
    task = await crud.update_task(db, task_id, task_data)
    if task is None:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    return task


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить задачу"
)
async def delete_task(task_id: int, db: AsyncSession = Depends(get_async_session)):
    result = await crud.delete_task(db, task_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    return None
