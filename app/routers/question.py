from typing import Any, Optional

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from ..models import QuestionCreate, User
from ..service.auth import AuthService
from ..service.data import DataHandler
from ..service.utils import add_request

router = APIRouter()

templates = Jinja2Templates(directory='templates')


@router.get('/home', response_class=HTMLResponse)
async def get_home(
    request: Request,
    handler: DataHandler = Depends(),
    current_user: User = Depends(AuthService.get_current_user),
) -> Any:
    page_data = handler.get_data_home(current_user)
    page_dict = add_request(request, page_data.dict())
    return templates.TemplateResponse('home.html', page_dict)


@router.get('/questions/create', response_class=HTMLResponse)
async def get_form_question(
    request: Request,
    current_user: Optional[User] = Depends(AuthService.get_current_user),
) -> Any:
    if current_user is None:
        return RedirectResponse('/auth/login')
    return templates.TemplateResponse(
        'create.html', {'request': request, 'user': current_user.dict()}
    )


@router.post('/questions/create', response_class=HTMLResponse)
async def create_question(
    request: Request,
    handler: DataHandler = Depends(),
    current_user: User = Depends(AuthService.get_current_user),
    question_data: QuestionCreate = Depends(QuestionCreate.from_form),
) -> Any:
    page_data = handler.create_question(current_user, question_data)
    page_dict = add_request(request, page_data.dict())
    return templates.TemplateResponse('create.html', page_dict)


@router.get('/questions/written', response_class=HTMLResponse)
async def get_written_questions(
    request: Request,
    handler: DataHandler = Depends(),
    current_user: User = Depends(AuthService.get_current_user),
) -> Any:
    if current_user is None:
        return RedirectResponse('/auth/login')
    page_data = handler.get_questions_author(current_user)
    page_dict = add_request(request, page_data.dict())
    return templates.TemplateResponse('author.html', page_dict)


@router.get('/questions/played', response_class=HTMLResponse)
async def get_played_questions(
    request: Request,
    handler: DataHandler = Depends(),
    current_user: Optional[User] = Depends(AuthService.get_current_user),
) -> Any:
    if current_user is None:
        return RedirectResponse('/auth/login')

    page_data = handler.get_questions_player(current_user)
    page_dict = add_request(request, page_data.dict())
    return templates.TemplateResponse('played.html', page_dict)
