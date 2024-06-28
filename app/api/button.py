import shutil
from typing import List

from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.button import ButtonBase
from app.core.db import get_async_session
from app.crud.button import button_crud
from app.validators.validators import (
    check_buttons_name_duplicate, check_button_exists
)
import os
from pathlib import Path

router = APIRouter(
    tags=['API Bottons']
)

current_working_directory = os.getcwd()


@router.post(
    '/api/create'
)
async def create_button(
        name: str,
        is_moscow: bool,
        text: str,
        is_department: bool,
        is_active: bool,
        file_pic: list[UploadFile] = File(...),
        file_doc: list[UploadFile] = File(...),
        session: AsyncSession = Depends(get_async_session),
):

    picture = []
    Path(current_working_directory + '/app/static/media/pics/').mkdir(parents=True, exist_ok=True)
    for pic in file_pic:
        if pic.filename:
            filename = str(pic.filename).replace(' ', '_')
            with open(current_working_directory + '/app/static/media/pics/' + filename, 'wb') as image:
                shutil.copyfileobj(pic.file, image)
            picture.append('static/media/pics/' + filename)

    picture = ' '.join(picture)
    print(f'{picture=}')
    item = []
    Path(current_working_directory + '/app/static/media/docs/').mkdir(parents=True, exist_ok=True)
    for doc in file_doc:
        if doc.filename:
            filename = str(doc.filename).replace(' ', '_')
            with open(current_working_directory + '/app/static/media/docs/' + filename, 'wb') as file:
                shutil.copyfileobj(doc.file, file)
            item.append('static/media/docs/' + filename)

    file = ' '.join(item)
    print(f'{file=}')
    new_button = await button_crud.create_with_pic(name=name,
                                                   is_moscow=is_moscow,
                                                   text=text,
                                                   picture=picture,
                                                   file=file,
                                                   is_department=is_department,
                                                   is_active=is_active,
                                                   session=session)
    return new_button


@router.get(
    '/api',
    response_model=list[ButtonBase]
)
async def get_all_buttons(
        session: AsyncSession = Depends(get_async_session),
):
    all_buttons = await button_crud.get_multi(session)
    return all_buttons


"""
@router.get(
    '/api/{button_id}',
    response_model=list[ButtonBase]
)
async def get_button_detail_by_id(
        button_id: int,
        session: AsyncSession = Depends(get_async_session),
):
    button_detail = await button_crud.get(button_id, session)
    return button_detail
"""


# test ok
@router.get(
    '/api/{button_id}',
    response_model=ButtonBase,
    response_model_exclude_none=True,
)
async def get_button_detail_by_id(
        button_id: int,
        session: AsyncSession = Depends(get_async_session),
):
    button_detail = await button_crud.get(button_id, session)
    return button_detail


# test ok
@router.delete(
    '/api/{button_id}',
    response_model=ButtonBase,
    response_model_exclude_none=True,
    # dependencies=[Depends(current_superuser)]
)
async def delete_button(
    button_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    """
    - Удалить кнопку.
    - **доступность:** Суперюзер.
    """
    button = await check_button_exists(
       button_id, session
    )
    for file in button.picture, button.file:
        if Path.exists(Path(file)):
            Path.unlink(file)

    return await button_crud.remove(
        button, session
    )
