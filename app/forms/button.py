from typing import Optional, List

from fastapi import Request, UploadFile, File


class ButtonForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.name: Optional[str] = None
        self.is_moscow: Optional[bool] = None
        self.text: Optional[str] = None
        self.is_department: Optional[bool] = None
        self.is_active: Optional[bool] = None
        self.file_pic: list[UploadFile] = File(...)
        self.file_doc: list[UploadFile] = File(...)

    async def load_data(self):
        form = await self.request.form()
        self.name = form.get('name')
        self.is_moscow = form.get('is_moscow')
        self.text = form.get('text')
        self.is_department = form.get('is_department')
        self.is_active = form.get('is_active')
        self.file_pic = form.get('file_pic')
        self.file_doc = form.get('file_doc')

    async def is_valid(self):
        if not self.name or not len(self.name) > 2:
            self.errors.append('Название кнопки должно содержать минимум 5 символов')
        if not self.text or not len(self.name) >= 0:
            self.errors.append('Кнопка должна содержать текст')

        if not self.errors:
            return True
        return False


