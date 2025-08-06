from pydantic import BaseModel
from typing import Optional


class TaskBase(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None
    done_by: Optional[str] = None


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None
    done_by: Optional[str] = None


class TaskInDB(TaskBase):
    id: int

    class Config:
        from_attributes = True
