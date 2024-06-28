from fastapi import APIRouter, Request, Form, UploadFile, Depends, File
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.responses import RedirectResponse

from app.core.db import get_async_session
from app.api.button import (create_button, get_all_buttons,
                            get_button_detail_by_id, delete_button)

router = APIRouter(tags=['Render Bottons'])

templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def render_all_buttons(request: Request,
                             session: AsyncSession = Depends(get_async_session)
                             ):
    context = await get_all_buttons(session)

    return templates.TemplateResponse("index.html", {"request": request,
                                                     "context": context,
                                                     }
                                      )


@router.get("/create", response_class=HTMLResponse)
async def get_button_form(request: Request,
                          ):
    return templates.TemplateResponse("form.html", {"request": request,
                                                    }
                                      )


@router.post("/create")
async def post_button_form(name: str = Form(...),
                           is_moscow: bool = Form(...),
                           text: str = Form(...),
                           is_department: bool = Form(...),
                           is_active: bool = Form(...),
                           file_pic: list[UploadFile] = None,
                           file_doc: list[UploadFile] = None,
                           session: AsyncSession = Depends(get_async_session),
                           ):
    await create_button(name=name,
                        is_moscow=is_moscow,
                        text=text,
                        is_department=is_department,
                        is_active=is_active,
                        file_pic=file_pic,
                        file_doc=file_doc,
                        session=session
                        )
    return RedirectResponse(router.url_path_for('render_all_buttons'), status_code=status.HTTP_303_SEE_OTHER)


@router.get("/{button_id}", response_class=HTMLResponse)
async def get_button_detail(request: Request,
                            button_id: int,
                            session: AsyncSession = Depends(get_async_session)
                            ):
    context = await get_button_detail_by_id(button_id, session)

    if context.picture:
        context.picture = context.picture.split(' ')

    if context.file:
        context.file = context.file.split(' ')

    return templates.TemplateResponse("button_detail.html",
                                      {"request": request,
                                       "context": context,
                                       }
                                      )

# delete button: В работе
