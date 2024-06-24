from fastapi import FastAPI

# Импортируем роутер.
from starlette.staticfiles import StaticFiles

from app.api.button import router as button
from app.api.render import router as render

from app.core.config import settings

app = FastAPI(title=settings.app_title)

app.mount("/static", StaticFiles(directory="app/static"), name="static")


app.include_router(button)
app.include_router(render)


