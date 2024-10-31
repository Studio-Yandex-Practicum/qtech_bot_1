"""Модуль движка, модели и соединения с БД."""
import datetime
import os

from dotenv import load_dotenv
from sqlalchemy import (Boolean, Column, DateTime, Integer, String, Text,
                        create_engine)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy_utils import URLType

load_dotenv()

engine = create_engine(
    os.getenv('BOT_DATABASE_URL'),
    echo=True,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

Base = declarative_base()


class Button(Base):
    """Класс модели кнопки в БД."""
    __tablename__ = 'button'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    is_moscow = Column(Boolean, default=True)
    text = Column(Text())
    picture = Column(URLType, nullable=True)
    file = Column(URLType, nullable=True)
    is_department = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    created_date = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))


Session = scoped_session(sessionmaker(bind=engine))
session = Session()
