from datetime import datetime
from pydantic import BaseModel


class ButtonBase(BaseModel):
    name: str
    location: bool
    message: str
    picture: str
    is_active: bool
    created_date: datetime

    class Config:
        orm_mode = True


class ButtonCreation(BaseModel):
    name: str
    location: bool
    message: str
