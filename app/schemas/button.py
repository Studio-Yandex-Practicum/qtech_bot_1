"""Модуль с классами схем."""
from datetime import datetime

from pydantic import BaseModel


class ButtonBase(BaseModel):
    """Базовая класс схемы кнопки бота"""
    name: str
    location: bool
    message: str
    picture: str
    is_active: bool
    created_date: datetime

    class Config:
        """Класс конфигурации класса схемы"""
        from_attributes = True


class ButtonCreation(BaseModel):
    """Класс схемы создания кнопки бота"""
    name: str
    location: bool
    message: str


class ButtonUpdate(BaseModel):
    """Класс схемы создания кнопки бота"""    
    name: str
    is_moscow: bool
    text: str
    is_department: bool
    is_active: bool
