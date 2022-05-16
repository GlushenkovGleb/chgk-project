from typing import Any, Union

from fastapi import APIRouter, BackgroundTasks, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from .. import models
from ..database import get_unsafe_redis, get_unsafe_session, init_redis_db
from ..service.auth import AuthService
from ..service.game import GameController
from ..service.utils import add_request

router = APIRouter()

templates = Jinja2Templates(directory='templates')


# This is very bad(Don't know how to start background task at the beginning):
@router.get('/')
async def init(
    background_tasks: BackgroundTasks,
) -> RedirectResponse:  # pragma: no cover
    await init_redis_db()
    # get redis here, cause it works strange with DI
    redis_db = get_unsafe_redis()
    session = get_unsafe_session()
    controller = GameController(redis_db, session)
    background_tasks.add_task(controller.process_question_timing)
    return RedirectResponse('/home')


@router.get('/questions/{question_id}')
async def play_question(
    request: Request,
    question_id: int,
    current_user: models.User = Depends(AuthService.get_current_user),
    controller: GameController = Depends(),
) -> Union[RedirectResponse, Any]:
    if current_user is None:
        return RedirectResponse('/auth/login')
    page_data = await controller.play_question(question_id, current_user)
    if page_data is None:
        return RedirectResponse('/')
    page_dict = add_request(request, page_data.dict())
    return templates.TemplateResponse('question_play.html', page_dict)


@router.post('/questions/{question_id}')
async def process_answer(
    request: Request,
    question_id: int,
    current_user: models.User = Depends(AuthService.get_current_user),
    controller: GameController = Depends(),
    answer: str = Form(...),
) -> Any:
    if current_user is None:
        return RedirectResponse('/auth/login')

    page_data = await controller.process_answer(question_id, answer, current_user)
    if page_data is None:
        return RedirectResponse('/auth/login')

    page_dict = add_request(request, page_data.dict())
    return templates.TemplateResponse('question_over.html', page_dict)
