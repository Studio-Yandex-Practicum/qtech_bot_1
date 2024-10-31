import datetime

from sqlalchemy import Boolean, Column, DateTime, String, Text
from sqlalchemy_utils import URLType

from app.core.db import Base


class Button(Base):
    name = Column(String(100), nullable=False)
    is_moscow = Column(Boolean,  default=True)
    text = Column(Text())
    picture = Column(URLType, nullable=True)
    file = Column(URLType, nullable=True)
    is_department = Column(Boolean,  default=True)

    is_active = Column(Boolean, default=True)
    created_date = Column(DateTime, default=datetime.datetime.utcnow)
