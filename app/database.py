import os
from pathlib import Path
from typing import AsyncGenerator, Generator

import sqlalchemy.orm as so
from aioredis import Redis
from sqlalchemy import create_engine

from .settings import settings
from .tables import Base

engine = create_engine(
    settings.database_url,
    connect_args={'check_same_thread': False},
)

Session = so.sessionmaker(
    engine,
    autocommit=False,
    autoflush=False,
)


def create_session() -> Generator[so.Session, None, None]:  # pragma: no cover
    new_session = Session()
    try:
        yield new_session
    except Exception:
        new_session.rollback()
        raise
    finally:
        new_session.close()


async def get_redis() -> AsyncGenerator[Redis, None]:  # pragma: no cover
    redis_db = await Redis(
        port=settings.redis_port, host=settings.redis_host, decode_responses=True
    )
    await redis_db.config_set('notify-keyspace-events', 'KEA')
    try:
        yield redis_db
    finally:
        await redis_db.close()


async def init_redis_db() -> None:  # pragma: no cover
    redis_db = Redis(port=settings.redis_port, host=settings.redis_host)
    await redis_db.config_set('notify-keyspace-events', 'KEA')


def init_db() -> None:  # pragma: no cover
    data_path = Path(settings.database_url.replace('sqlite:///', ''))
    if not data_path.exists():
        try:
            os.mkdir('isinstance')
        except OSError:
            pass

        Base.metadata.create_all(engine)


def get_unsafe_redis() -> Redis:  # pragma: no cover
    return Redis(
        port=settings.redis_port, host=settings.redis_host, decode_responses=True
    )


def get_unsafe_session() -> so.Session:  # pragma: no cover
    return Session()
