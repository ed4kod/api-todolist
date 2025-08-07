from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TaskBase(BaseModel):
    title: str


class TaskCreate(TaskBase):
    user_id: int
    done_by: Optional[str] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None
    done_by: Optional[str] = None


class TaskInDB(TaskBase):
    id: int
    done: bool
    user_id: int
    done_by: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
