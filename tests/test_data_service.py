import pytest

from app import models
from app.service.data import DataHandler


@pytest.mark.asyncio
async def test_create_question(client_test, session_test, current_user):
    question_data = models.QuestionCreate(
        title='title',
        desc='description1',
        cost='1000',
        answer='answer',
    )
    handler = DataHandler(session=session_test)
    page_data = handler.create_question(current_user, question_data)

    assert page_data.error is not None
    assert 'Error' not in page_data.error


@pytest.mark.asyncio
async def test_create_question_error(client_test, session_test, current_user):
    question_data = models.QuestionCreate(
        title='tittle1',
        desc='description1',
        cost='9999999',
        answer='answer',
    )
    handler = DataHandler(session=session_test)
    page_data = handler.create_question(current_user, question_data)

    assert page_data.error is not None
    assert 'Error' in page_data.error


@pytest.mark.asyncio
async def test_get_data_home_user(client_test, session_test, current_user):
    handler = DataHandler(session=session_test)
    current_user.id = 2
    page_data = handler.get_data_home(current_user)

    # doesn't show his own question
    assert page_data.questions is not None
    assert len(page_data.questions) == 1


@pytest.mark.asyncio
async def test_get_data_home_no_user(client_test, session_test):
    handler = DataHandler(session=session_test)
    page_data = handler.get_data_home(current_user=None)

    assert page_data.questions is not None
    assert len(page_data.questions) == 1


@pytest.mark.asyncio
async def test_question_author(client_test, session_test, current_user):
    handler = DataHandler(session=session_test)
    page_data = handler.get_questions_author(current_user)

    # shows just his own question
    assert page_data.questions is not None
    assert len(page_data.questions) == 1


@pytest.mark.asyncio
async def test_question_player(client_test, session_test, current_user):
    handler = DataHandler(session=session_test)
    page_data = handler.get_questions_player(current_user)

    # shows just one played question
    assert page_data.questions is not None
    assert len(page_data.questions) == 1
