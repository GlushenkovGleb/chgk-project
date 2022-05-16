import asyncio
from typing import Any

import pytest

from app.service.game import GameController
from app.tables import User


def async_return(result) -> Any:
    f = asyncio.Future()  # type: ignore
    f.set_result(result)
    return f


@pytest.mark.asyncio
async def test_play_question(session_test, redis_test, client_test, current_user):
    controller = GameController(session=session_test, redis_db=redis_test)
    question_data = await controller.play_question(1, current_user)

    assert question_data is not None
    assert question_data.question.id == 1


@pytest.mark.asyncio
async def test_play_no_question(session_test, redis_test, client_test, current_user):
    controller = GameController(session=session_test, redis_db=redis_test)
    question_data = await controller.play_question(10000, current_user)

    assert question_data is None


@pytest.mark.asyncio
async def test_play_no_money(session_test, redis_test, client_test, current_user):
    current_user.money = '0'
    current_user.id = 3

    controller = GameController(session=session_test, redis_db=redis_test)
    question_data = await controller.play_question(1, current_user)

    assert question_data is None


@pytest.mark.asyncio
async def test_answer_no_question(session_test, redis_test, client_test, current_user):
    controller = GameController(session=session_test, redis_db=redis_test)
    question_data = await controller.process_answer(1000, 'answer', current_user)

    assert question_data is None


@pytest.mark.asyncio
async def test_answer_played_question(
    session_test, redis_test, client_test, current_user
):
    controller = GameController(session=session_test, redis_db=redis_test)
    question_data = await controller.process_answer(2, 'answer', current_user)

    assert question_data is not None
    assert question_data.msg == 'Time is over!'


@pytest.mark.asyncio
async def test_answer_defeat(session_test, redis_test, client_test, current_user):
    controller = GameController(session=session_test, redis_db=redis_test)
    question_data = await controller.process_answer(3, 'answeasdfasdr3', current_user)
    user = session_test.query(User).filter(User.id == current_user.id).first()

    assert user.money == '1000.00'
    assert question_data is not None
    assert question_data.msg == 'You lose!'


@pytest.mark.asyncio
async def test_answer_win(session_test, redis_test, client_test, current_user):
    controller = GameController(session=session_test, redis_db=redis_test)
    question_data = await controller.process_answer(3, 'answer3', current_user)
    user = session_test.query(User).filter(User.id == current_user.id).first()

    assert user.money == '1600.00'
    assert question_data is not None
    assert question_data.msg == 'You win!'
