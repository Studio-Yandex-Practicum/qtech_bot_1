import os

from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db import get_async_session
from app.core.user import current_user
from app.crud.button import button_crud
from app.models import User
from app.schemas.button import ButtonBase
from app.utils.auxiliary import object_delete, object_upload

router = APIRouter(
    tags=['API Bottons']
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/jwt/login")


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
    picture = ' '.join(object_upload(settings.PICTURE_ROOT, settings.BASE_DIR, file_pic))
    file = ' '.join(object_upload(settings.DOC_ROOT, settings.BASE_DIR, file_doc))

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


@router.delete(
    '/api/delete/{button_id}',
    response_model_exclude_none=True,
)
async def delete_button(
        button_id: int,
        session: AsyncSession = Depends(get_async_session),
) -> None:
    button = await button_crud.get(button_id, session)

    if button.picture:
        print(settings.PICTURE_ROOT)
        print(button.picture)
        object_delete(settings.PICTURE_ROOT, button.picture)

    if button.file:
        object_delete(settings.DOC_ROOT, button.file)

    return await button_crud.remove(
        button, session
    )
