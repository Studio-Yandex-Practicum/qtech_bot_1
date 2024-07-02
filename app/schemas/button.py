from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


"""
class ButtonBase(BaseModel):
    id: int
    name: str
    location: bool
    message: str
    picture: str
    is_active: bool
    created_date: datetime

    class Config:
        orm_mode = True
"""


class ButtonDatabase(BaseModel):
    id: int
    name: str
    is_moscow: bool = True
    text: str
    picture: str = None
    file: str = None
    is_department: bool = True
    is_active: bool = True
    created_date: Optional[datetime] = (
        Field(example=datetime.now().isoformat(timespec='minutes'))
    )

    class Config:
        orm_mode = True


class ButtonCreation(BaseModel):
    name: str
    location: bool
    message: str
