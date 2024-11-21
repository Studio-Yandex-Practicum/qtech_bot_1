import os

from fastapi import APIRouter, Request, Form, UploadFile, Depends, File
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.responses import RedirectResponse

from app.api.user import get_current_user_from_cookie, get_current_user_from_token
from app.core.config import settings

from app.core.db import get_async_session
from app.api.button import (create_button, get_all_buttons,
                            get_button_detail_by_id, delete_button)
from app.models import User
from app.utils.auxiliary import object_upload
from app.forms.button import ButtonForm

router = APIRouter(tags=['Render Bottons'])

templates = Jinja2Templates(directory="app/templates")

IMAGE_FILE_FORMAT = {'jpeg', 'png', 'webp', 'tiff', 'svg', 'gif', 'heif', 'jpg'}


@router.get("/", response_class=HTMLResponse)
async def render_all_buttons(
        request: Request,
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(get_current_user_from_token)):
    buttons = await get_all_buttons(session)
    user = None
    try:
        user = await get_current_user_from_cookie(request, session)
    except Exception as e:
        print(f"Error retrieving user from cookie: {e}")

    context = {
        "request": request,
        "buttons": buttons,
        "user": user
    }
    return templates.TemplateResponse("index.html", context)


@router.get("/create", response_class=HTMLResponse)
async def get_button_form(request: Request,
                          user: User = Depends(get_current_user_from_token)
                          ):
    return templates.TemplateResponse("form.html", {"request": request,
                                                    "context": None,
                                                    'user': user})


@router.post("/create")
async def post_button_form(
        request: Request,
        name: str = Form(...),
        is_moscow: bool = Form(...),
        text: str = Form(''),
        is_department: bool = Form(...),
        is_active: bool = Form(...),
        file_pic: list[UploadFile] = None,
        file_doc: list[UploadFile] = None,
        user: User = Depends(get_current_user_from_token),
        session: AsyncSession = Depends(get_async_session),
):
    form = ButtonForm(request)
    errors = []
    if (len(file_pic)+len(file_doc)) > 20:
            errors.append('Количество картинок и файлов не должно быть более 20')
    if file_pic[0].filename != '':
            for pic in file_pic:
                if pic.filename.split('.')[-1].lower() not in IMAGE_FILE_FORMAT:
                    if 'В разделе картинки нужно прикрепить верный файл с расширениями: jpeg, png, webp, tiff, svg, gif, heif, jpg' not in errors:
                        errors.append('В разделе картинки нужно прикрепить верный файл с расширениями: jpeg, png, webp, tiff, svg, gif, heif, jpg')
    
    if errors != []:
        context = {
            'name': name,
            'is_moscow': is_moscow,
            'text': text,
            'is_department': is_department,
            'is_active': is_active,
            'file_pic': file_pic,
            'file_doc': file_doc,
            'user': user,
        }
        return templates.TemplateResponse("form.html", {"request": request,
                                                        "errors": errors,
                                                        "context": context,
                                                        }
                                          )
    else:
        await form.load_data()
        if await form.is_valid():
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
        else:
            errors = form.errors
            context = {
            'name': name,
            'is_moscow': is_moscow,
            'text': text,
            'is_department': is_department,
            'is_active': is_active,
            'file_pic': file_pic,
            'file_doc': file_doc,
            'user': user,
            }
            return templates.TemplateResponse("form.html", {"request": request,
                                                        "errors": errors,
                                                        "context": context,
                                                        }
                                          )


@router.get("/{button_id}", response_class=HTMLResponse)
async def get_button_detail(request: Request,
                            button_id: int,
                            session: AsyncSession = Depends(get_async_session),
                            user: User = Depends(get_current_user_from_token)
                            ):
    context = await get_button_detail_by_id(button_id, session)

    if context.picture:
        context.picture = context.picture.split(' ')

    if context.file:
        context.file = context.file.split(' ')

    return templates.TemplateResponse("button_detail.html",
                                      {"request": request,
                                       "context": context,
                                       'user': user
                                       },
                                      )


@router.get("/update/{button_id}", response_class=HTMLResponse)
async def update_button_form(request: Request,
                             button_id: int,
                             session: AsyncSession = Depends(get_async_session),
                             user: User = Depends(get_current_user_from_token)
                             ):
    context = await get_button_detail_by_id(button_id, session)

    if context.picture:
        context.picture = context.picture.split(' ')

    if context.file:
        context.file = context.file.split(' ')

    return templates.TemplateResponse("form_patch.html", {"request": request,
                                                          "context": context,
                                                          'button_id': button_id,
                                                          'user': user
                                                          }
                                      )


@router.post("/update/{button_id}")
async def update_button_form(
        button_id: int,
        name: str = Form(...),
        is_moscow: bool = Form(...),
        text: str = Form(...),
        is_department: bool = Form(...),
        is_active: bool = Form(...),
        file_pic: list[UploadFile] = File(...),
        file_doc: list[UploadFile] = File(...),
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(get_current_user_from_token)
):
    button = await get_button_detail_by_id(button_id, session)
    button.name = name
    button.is_moscow = is_moscow
    button.text = text
    button.is_department = is_department
    button.is_active = is_active

    if file_pic[0].filename != '':
        picture = ' '.join(object_upload(settings.PICTURE_ROOT, settings.BASE_DIR, file_pic))
        if button.picture:
            button.picture = f'{str(button.picture)} {picture}'
        else:
            button.picture = picture

    if file_doc[0].filename != '':
        file = ' '.join(object_upload(settings.DOC_ROOT, settings.BASE_DIR, file_doc))
        if button.file:
            button.file = f'{str(button.file)} {file}'
        else:
            button.file = file

    await session.commit()
    return RedirectResponse(router.url_path_for('get_button_detail', button_id=button_id),
                            status_code=status.HTTP_303_SEE_OTHER)


@router.post(
    '/delete_picture/{button_id}/{picture}',
)
async def del_button_picture(
        button_id: int,
        picture: str,
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(get_current_user_from_token)
):
    button = await get_button_detail_by_id(button_id, session)

    picture_list = button.picture.split(' ')

    new_pic_list = []
    for pic_url in picture_list:
        if picture != pic_url.split('\\')[-1]:
            new_pic_list.append(pic_url)

    button.picture = ' '.join(new_pic_list)
    await session.commit()
    await session.refresh(button)

    delete_patch = os.path.join(settings.PICTURE_ROOT, picture)
    os.remove(delete_patch)

    return RedirectResponse(router.url_path_for('update_button_form', button_id=button_id),
                            status_code=status.HTTP_303_SEE_OTHER)


@router.post(
    '/delete_file/{button_id}/{file}',
)
async def del_button_file(
        button_id: int,
        file: str,
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(get_current_user_from_token)
):
    button = await get_button_detail_by_id(button_id, session)

    file_list = button.file.split(' ')

    new_file_list = []
    for file_url in file_list:
        if file != file_url.split('\\')[-1]:
            new_file_list.append(file_url)

    button.file = ' '.join(new_file_list)
    await session.commit()
    await session.refresh(button)

    delete_patch = os.path.join(settings.DOC_ROOT, file)
    os.remove(delete_patch)

    return RedirectResponse(router.url_path_for('update_button_form', button_id=button_id),
                            status_code=status.HTTP_303_SEE_OTHER)


@router.post(
    '/delete/{button_id}',
)
async def delete_item(
        button_id: int,
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(get_current_user_from_token)
):
    await delete_button(button_id=button_id, session=session)

    return RedirectResponse(router.url_path_for('render_all_buttons'),
                            status_code=status.HTTP_303_SEE_OTHER)
