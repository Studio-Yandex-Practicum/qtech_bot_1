import datetime as dt
import re
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.exceptions import HTTPException
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2, OAuth2PasswordRequestForm
from fastapi.security.utils import get_authorization_scheme_param
from fastapi.templating import Jinja2Templates
from jose import JWTError, jwt
from jwt import ExpiredSignatureError
from passlib.context import CryptContext
from rich.console import Console
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db import get_async_session
from app.core.user import UserManager, fastapi_users, get_user_manager
from app.crud.user import get_all_users, get_user, user_crud
from app.models.user import User
from app.schemas.user import UserCreate, UserRead, UserUpdate

console = Console()

templates = Jinja2Templates(directory="app/templates")
router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix='/auth',
    tags=['auth'],
)


class OAuth2PasswordBearerWithCookie(OAuth2):
    def __init__(
            self,
            tokenUrl: str,
            scheme_name: Optional[str] = None,
            scopes: Optional[Dict[str, str]] = None,
            description: Optional[str] = None,
            auto_error: bool = True,
    ):
        if not scopes:
            scopes = {}
        flows = OAuthFlowsModel(password={"tokenUrl": tokenUrl, "scopes": scopes})
        super().__init__(
            flows=flows,
            scheme_name=scheme_name,
            description=description,
            auto_error=auto_error,
        )

    async def __call__(self, request: Request) -> Optional[str]:
        authorization: str = request.cookies.get(settings.COOKIE_NAME)
        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                return None
        return param


oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="token")


def create_access_token(data: Dict) -> str:
    to_encode = data.copy()
    expire = dt.datetime.utcnow() + dt.timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


async def authenticate_user(email: str, plain_password: str, session: AsyncSession) -> Optional[User]:
    user = await get_user(email, session)
    if not user:
        return None
    if not pwd_context.verify(plain_password, user.hashed_password):
        return None
    return user


async def decode_token(token: str, session: AsyncSession) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials."
    )
    token = token.removeprefix("Bearer").strip()
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("email")
        if email is None:
            raise credentials_exception
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired."
        )
    except JWTError:
        raise TypeError

    user = await get_user(email, session)
    if user is None:
        raise credentials_exception
    return user


async def get_current_user_from_token(request: Request,
                                      token: str = Depends(oauth2_scheme),
                                      session: AsyncSession = Depends(get_async_session), ) -> User:
    try:
        user = await decode_token(token, session)
        return user
    except TypeError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )


async def get_current_user_from_cookie(request: Request, session: AsyncSession = Depends(get_async_session)) -> User:
    token = request.cookies.get(settings.COOKIE_NAME)
    user = await decode_token(token, session)
    return user


async def get_current_superuser(
        user: User = Depends(get_current_user_from_token)
) -> User:
    if not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Доступно только суперпользователю'
        )
    return user


@router.post("/token")
async def login_for_access_token(
        response: Response,
        form_data: OAuth2PasswordRequestForm = Depends(),
        session: AsyncSession = Depends(get_async_session)
) -> Dict[str, str]:
    user = await authenticate_user(form_data.email, form_data.password, session)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    access_token = create_access_token(data={"email": user.email})

    response.set_cookie(
        key=settings.COOKIE_NAME,
        value=f"Bearer {access_token}",
        httponly=True
    )
    return {settings.COOKIE_NAME: access_token, "token_type": "bearer"}


class LoginForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.email: Optional[str] = None
        self.password: Optional[str] = None

    async def load_data(self):
        form = await self.request.form()
        self.email = form.get("email")
        self.password = form.get("password")

    async def is_valid(self):
        if not self.email or not (self.email.__contains__("@")):
            self.errors.append("Email is required")
        if not self.password or not len(self.password) >= 4:
            self.errors.append("A valid password is required")
        if not self.errors:
            return True
        return False


@router.get("/auth/login", response_class=HTMLResponse)
def login_get(request: Request):
    context = {
        "request": request,
    }
    return templates.TemplateResponse("login.html", context)


@router.post("/auth/login", response_class=HTMLResponse)
async def login_post(request: Request, session: AsyncSession = Depends(get_async_session)):
    form = LoginForm(request)
    await form.load_data()
    if await form.is_valid():
        try:
            response = RedirectResponse("/", status.HTTP_302_FOUND)
            await login_for_access_token(response=response, form_data=form, session=session)
            form.__dict__.update(msg="Login Successful!")
            console.log("[green]Login successful!!!!")
            return response
        except HTTPException:
            form.__dict__.update(msg="")
            form.__dict__.get("errors").append("Неправильная почта или пароль. Попробуйте снова.")
            return templates.TemplateResponse("login.html", {"request": request, **form.__dict__})
    return templates.TemplateResponse("login.html", {"request": request, **form.__dict__})


@router.get("/auth/logout", response_class=RedirectResponse)
async def logout(request: Request):
    response = RedirectResponse(url="/")
    response.delete_cookie(settings.COOKIE_NAME)
    return response


@router.get('/register', response_class=HTMLResponse)
async def register_get(
        request: Request,
        user: User = Depends(get_current_superuser), ):
    context = {
        'user': user,
        'request': request
    }
    return templates.TemplateResponse("register.html", context)


async def user_create_validator(session, email, password):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if len(password) < 8:
        return 'Пароль должен быть не менее 8 символов'
    elif await get_user(email, session) is not None:
        return 'Пользователь с такой почтой уже существует'
    elif re.match(pattern, email) is None:
        return 'Введите корректную почту'


@router.post("/register", response_class=HTMLResponse)
async def register_post(
        request: Request,
        session: AsyncSession = Depends(get_async_session),
        user_manager: UserManager = Depends(get_user_manager),
        user: User = Depends(get_current_superuser)

):
    form = await request.form()
    email = form.get("email")
    password = form.get("password")
    is_superuser = form.get("is_superuser") == '1'

    error_message = await user_create_validator(session, email, password)
    if error_message:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "errors": [error_message],
            'user': user})
    try:
        user_create = UserCreate(email=email, password=password, is_superuser=is_superuser)
        user = await user_manager.create(user_create)
        return RedirectResponse(url="/all_users", status_code=status.HTTP_302_FOUND)
    except Exception as e:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "errors": [str(e)],
            'user': user})


@router.get('/all_users', response_class=HTMLResponse)
async def all_users(
        request: Request,
        user: User = Depends(get_current_superuser),
        session: AsyncSession = Depends(get_async_session)):
    users = await get_all_users(session=session)

    context = {
        'user': user,
        'request': request,
        'users': users
    }

    return templates.TemplateResponse("users.html", context)


@router.post('/delete_user/{user_id}', response_class=RedirectResponse)
async def delete_user(
        user_id: int,
        request: Request,
        user: User = Depends(get_current_superuser),
        session: AsyncSession = Depends(get_async_session)
):
    current_user = await user_crud.get(user_id, session)
    if not current_user:
        return templates.TemplateResponse("users.html", {
            "request": request,
            "errors": ['Пользователя не существует. Обновите страницу'],
            'user': user, })

    await user_crud.remove(current_user, session)
    users = await get_all_users(session=session)

    context = {
        'user': user,
        'request': request,
        'users': users
    }
    return templates.TemplateResponse("users.html", context)


@router.get('/change_password', response_class=RedirectResponse)
async def change_password(
        request: Request,
        user: User = Depends(get_current_user_from_token),
        session: AsyncSession = Depends(get_async_session)):
    context = {
        'user': user,
        'request': request
    }
    return templates.TemplateResponse("change_password.html", context)


async def user_update_validator(
        user: User,
        old_password: str,
        new_password: str,
        confirm_password: str) -> str:
    if not pwd_context.verify(old_password, user.hashed_password):
        return "Старый пароль неверен"
    if new_password != confirm_password:
        return "Новый и старый пароли не совпадают"
    if len(new_password) < 8:
        return 'Пароль должен быть не менее 8 символов'


@router.post('/change_password', response_class=RedirectResponse)
async def change_password_post(
        request: Request,
        user_manager: UserManager = Depends(get_user_manager),
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(get_current_user_from_token)
):
    form = await request.form()
    old_password = form.get("old_password")
    new_password = form.get("new_password")
    confirm_password = form.get("confirm_password")

    error_message = await user_update_validator(user, old_password, new_password, confirm_password)
    if error_message:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "errors": [error_message],
            'user': user})
    try:
        user_update = UserUpdate(password=new_password)
        user = await user_manager.update(user_update, user=user)
        return templates.TemplateResponse("change_password.html", {
            "request": request,
            "successful_password_change": ['Пароль изменён'],
            'user': user})
    except Exception as e:
        return templates.TemplateResponse("change_password.html", {
            "request": request,
            "errors": [str(e)],
            'user': user})
