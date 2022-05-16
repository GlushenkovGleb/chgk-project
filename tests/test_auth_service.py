import asyncio
from typing import Any
from unittest.mock import MagicMock

import pytest
from fakeredis.aioredis import FakeRedis

from app import models
from app.service.auth import AuthService


def async_return(result) -> Any:
    f = asyncio.Future()  # type: ignore
    f.set_result(result)
    return f


@pytest.mark.asyncio
async def test_register_user(client_test, session_test, redis_test):
    auth = AuthService(session=session_test, redis_db=redis_test)
    user_data = models.UserCreate(name='user', password='user')
    page_data = await auth.register(user_data)

    assert page_data.error is None


@pytest.mark.asyncio
async def test_register_existing(client_test, session_test, redis_test):
    auth = AuthService(session=session_test, redis_db=redis_test)
    user_data = models.UserCreate(name='user1', password='user1')
    page_data = await auth.register(user_data)

    assert page_data.error is not None


@pytest.mark.asyncio
async def test_login_ok(client_test, session_test, redis_test):
    auth = AuthService(session=session_test, redis_db=redis_test)
    user_data = models.UserCreate(name='user1', password='user1')
    page_data = await auth.login(user_data)

    assert page_data.error is None

    # test current_user
    user_model = await AuthService.get_current_user(
        redis_db=redis_test, session=session_test
    )
    assert user_model is not None
    assert user_model.name == 'user1'


@pytest.mark.asyncio
async def test_login_no_user(client_test, session_test, redis_test):
    auth = AuthService(session=session_test, redis_db=redis_test)
    user_data = models.UserCreate(name='NOUSER', password='user')
    page_data = await auth.login(user_data)

    assert page_data.error is not None

    # test current_user
    user_model = await AuthService.get_current_user(
        redis_db=redis_test, session=session_test
    )
    assert user_model is None


@pytest.mark.asyncio
async def test_login_no_password(client_test, session_test, redis_test):
    auth = AuthService(session=session_test, redis_db=redis_test)
    user_data = models.UserCreate(name='user1', password='no_password')
    page_data = await auth.login(user_data)

    assert page_data.error is not None


@pytest.mark.asyncio
async def test_logout(client_test, session_test):
    redis_db = FakeRedis(decode_responses=True)
    redis_db.delete = MagicMock(return_value=async_return(None))

    auth = AuthService(session=session_test, redis_db=redis_db)
    await auth.logout()

    redis_db.delete.assert_called_once()
