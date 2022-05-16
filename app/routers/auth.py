from typing import Any, Union

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from ..models import UserCreate
from ..service.auth import AuthService
from ..service.utils import add_request

router = APIRouter(prefix='/auth')
templates = Jinja2Templates(directory='./templates')


@router.get('/register', response_class=HTMLResponse)
async def show_register(request: Request) -> Any:
    return templates.TemplateResponse('register.html', {'request': request})


@router.post('/register')
async def register_user(
    request: Request,
    user_data: UserCreate = Depends(UserCreate.from_form),
    auth: AuthService = Depends(),
) -> Union[Any, RedirectResponse]:
    page_data = await auth.register(user_data)
    if page_data.error:
        page_dict = add_request(request, page_data.dict())
        return templates.TemplateResponse('register.html', page_dict)

    return RedirectResponse('/auth/login', status_code=status.HTTP_302_FOUND)


@router.get('/login', response_class=HTMLResponse)
async def show_login_user(
    request: Request,
) -> Union[Any, RedirectResponse]:
    return templates.TemplateResponse('login.html', {'request': request})


@router.post('/login')
async def login_user(
    request: Request,
    user_data: UserCreate = Depends(UserCreate.from_form),
    auth: AuthService = Depends(),
) -> Union[Any, RedirectResponse]:
    page_data = await auth.login(user_data)
    if page_data.error:
        page_dict = add_request(request, page_data.dict())
        return templates.TemplateResponse('login.html', page_dict)

    return RedirectResponse('/home', status_code=status.HTTP_302_FOUND)


@router.get('/logout', response_class=RedirectResponse)
async def logout_user(auth: AuthService = Depends()) -> RedirectResponse:
    await auth.logout()
    return RedirectResponse('/auth/login')


@router.on_event('shutdown')
async def logout() -> None:  # pragma: no cover
    await AuthService.logout_before_leaving()
