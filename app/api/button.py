import shutil

from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.button import ButtonBase
from app.core.db import get_async_session
from app.crud.button import button_crud
import os

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
        file_pic: UploadFile = File(...),
        file_doc: UploadFile = File(...),
        session: AsyncSession = Depends(get_async_session),
):
    if file_pic.filename:
        with open(current_working_directory + '/app/static/media/pics/' + file_pic.filename, 'wb') as image:
            shutil.copyfileobj(file_pic.file, image)
        picture = str(current_working_directory + '/app/static/media/pics/' + file_pic.filename)
    else:
        picture = None

    if file_doc.filename:
        with open(current_working_directory + '/app/static/media/docs/' + file_doc.filename, 'wb') as file:
            shutil.copyfileobj(file_doc.file, file)
        file = str(current_working_directory + '/app/static/media/docs/' + file_doc.filename)
    else:
        file = None

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
