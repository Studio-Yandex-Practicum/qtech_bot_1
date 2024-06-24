from sqlalchemy.ext.asyncio import AsyncSession

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


button_crud = CRUDButton(Button)
