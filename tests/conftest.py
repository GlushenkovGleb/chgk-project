# type: ignore

from typing import AsyncGenerator, Generator

import pytest
from fakeredis.aioredis import FakeRedis
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app import models
from app.app import app
from app.database import create_session, get_redis
from app.service.auth import AuthService
from app.tables import Base, QuestionAuthor, QuestionPlayer, User

engine = create_engine(
    'sqlite:///./test.sqlite3', connect_args={'check_same_thread': False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(engine)


def create_session_test() -> Generator[Session, None, None]:
    new_session = TestingSessionLocal()
    try:
        yield new_session
    except Exception:
        new_session.rollback()
        raise
    finally:
        new_session.close()


async def get_redis_test() -> AsyncGenerator[Session, None]:
    redis_db = FakeRedis(decode_responses=True)
    try:
        yield redis_db
    finally:
        await redis_db.flushall()
        await redis_db.close()


def get_current_user() -> models.User:
    return models.User(
        id=1,
        name='user1',
        password_hash=AuthService.hash_password('user1'),
        money='1000',
    )


def get_no_user() -> None:
    return None


app.dependency_overrides[create_session] = create_session_test
app.dependency_overrides[get_redis] = get_redis_test


def init_db():
    # creating users:
    test_session = TestingSessionLocal()
    test_session.add_all(
        [
            User(name='user1', password_hash=AuthService.hash_password('user1')),
            User(name='user2', password_hash=AuthService.hash_password('user2')),
            User(name='user3', password_hash=AuthService.hash_password('user3')),
        ]
    )
    # creating questions:
    test_session.add_all(
        [
            QuestionAuthor(
                user_id=1,
                title='user1_title',
                desc='user1_desc',
                cost='100',
                answer='user1',
            ),
            QuestionAuthor(
                user_id=2,
                title='user2_title',
                desc='user2_desc',
                cost='200',
                answer='user2',
                status=models.Status.DEFEAT,
            ),
            QuestionAuthor(
                user_id=3,
                title='user3_title',
                desc='user3_desc',
                cost='300',
                answer='answer3',
                status=models.Status.PLAYING,
            ),
        ]
    )
    # creating records about player's questions:
    test_session.add_all(
        [QuestionPlayer(user_id=1, question_id=2, status=models.Status.WIN)]
    )
    test_session.commit()
    test_session.close()


@pytest.fixture()
async def client_test():
    Base.metadata.create_all(engine)
    init_db()
    await FakeRedis(decode_responses=True).flushall()
    app.dependency_overrides[AuthService.get_current_user] = get_no_user
    client = TestClient(app)

    yield client

    Base.metadata.drop_all(engine)


@pytest.fixture()
async def client_user(current_user):
    Base.metadata.create_all(engine)
    init_db()
    await FakeRedis(decode_responses=True).flushall()
    app.dependency_overrides[AuthService.get_current_user] = get_current_user
    client = TestClient(app)

    yield client

    Base.metadata.drop_all(engine)


@pytest.fixture()
def session_test():
    return next(create_session_test())


@pytest.fixture()
def redis_test():
    return FakeRedis(decode_responses=True)


@pytest.fixture()
def current_user():
    return models.User(
        id=1,
        name='user1',
        money='1000',
        password_hash=AuthService.hash_password('user1'),
    )
