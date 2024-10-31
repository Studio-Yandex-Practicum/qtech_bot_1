import os
from pathlib import Path

from pydantic_settings import BaseSettings

BASE_DIR: str = Path(__file__).resolve().parent.parent
STATIC_ROOT: str = os.path.join(BASE_DIR, 'static')
MEDIA_ROOT: str = os.path.join(STATIC_ROOT, 'media')
PICTURE_ROOT: str = os.path.join(MEDIA_ROOT, 'pics')
DOC_ROOT: str = os.path.join(MEDIA_ROOT, 'docs')


class Settings(BaseSettings):
    app_title: str = 'Input title in .env'
    database_url: str = 'sqlite+aiosqlite:///./Qtech_bot.db'
    secret: str = 'SECRET'
    SECRET_KEY: str = "secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    COOKIE_NAME: str = "access_token"
    database_url: str
    BACKEND_URL: str = "'http://127.0.0.1:8000"

    BOT_TOKEN: str = '0000000:AAAAAAbbbbbbbb88888hhhhhhhhh'

    BOT_DATABASE_URL: str = 'sqlite:///../Qtech_bot.db'
    POSTGRES_DB: str = 'lorabot'
    POSTGRES_USER: str = 'lorabot'
    POSTGRES_PASSWORD: str = 'lorabot'
    POSTGRES_HOST: str = 'localhost'
    POSTGRES_PORT: str = '5432'
    ANALYTICS_PASSWORD: str = 'lrbt'
    ANALYTICS_CALL: str = 'lrbt'
    TG_BOT_NAME: str = 'Test_VLN_Bot'


    class Config:
        env_file = '.env'


settings = Settings()
