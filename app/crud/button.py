import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.encoders import jsonable_encoder

from app.crud.base import CRUDBase
from app.models.button import Button


class CRUDButton(CRUDBase):
    async def create_with_pic(
            self,
            name: str,
            is_moscow: bool,
            text: str,
            picture: str,
            file: str,
            is_department: bool,
            is_active: bool,
            session: AsyncSession,
    ):

        db_obj = self.model(name=name,
                            is_moscow=is_moscow,
                            text=text,
                            picture=picture,
                            file=file,
                            is_department=is_department,
                            is_active=is_active
                            )
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def get_buttons_id_by_name(
        self,
        button_name: str,
        session: AsyncSession,
    ) -> Button:
        return (await session.execute(
            select(self.model.id).where(
                self.model.name == button_name
            )
        )).scalars().first()

    async def remove(
        self,
        db_button,
        session: AsyncSession,
    ):
        await session.delete(db_button)
        await session.commit()
        return db_button


button_crud = CRUDButton(Button)
