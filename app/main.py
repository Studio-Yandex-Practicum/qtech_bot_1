from fastapi import FastAPI, HTTPException, Request
from fastapi.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles

from app.api.button import router as button
from app.api.render import router as render
from app.api.user import router as user
from app.core.config import settings

app = FastAPI(title=settings.app_title)
templates = Jinja2Templates(directory="app/templates")

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    if exc.detail == "Not authenticated":
        return templates.TemplateResponse("login.html", {"request": request}, status_code=401)
    return exc


app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(user)
app.include_router(button)
app.include_router(render)
