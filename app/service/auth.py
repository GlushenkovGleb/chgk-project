from typing import Optional

from aioredis import Redis
from fastapi import Depends
from passlib.hash import bcrypt
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .. import models
from ..database import create_session, get_redis
from ..tables import User
from .utils import CURRENT_USER


class AuthService:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return bcrypt.verify(plain_password, hashed_password)

    @staticmethod
    def hash_password(password: str) -> str:
        return bcrypt.hash(password)

    @classmethod
    async def get_current_user(
        cls,
        redis_db: Redis = Depends(get_redis),
        session: Session = Depends(create_session),
    ) -> Optional[models.User]:

        user_json = await redis_db.get(CURRENT_USER)

        if user_json is not None:
            user_data = models.User.parse_raw(user_json)
            user = session.query(User).filter(User.id == user_data.id).first()
            return models.User.from_orm(user)

        return None

    @classmethod
    async def logout_before_leaving(cls) -> None:  # pragma: no cover
        # DI works strange with events
        redis_db = Redis()

        await redis_db.delete(CURRENT_USER)
        await redis_db.close()

    def __init__(
        self,
        session: Session = Depends(create_session),
        redis_db: Redis = Depends(get_redis),
    ):
        self.session = session
        self.redis_db = redis_db

    async def register(self, user_data: models.UserCreate) -> models.PageData:
        """Adds new user to database"""
        error = None

        user = User(
            name=user_data.name,
            password_hash=self.hash_password(user_data.password),
        )
        self.session.add(user)

        try:
            self.session.flush()
            self.session.commit()
        except IntegrityError:
            error = 'User with that name already exists'

        return models.PageData(error=error)

    async def login(self, user_data: models.UserCreate) -> models.PageData:
        error = None

        user = self.session.query(User).filter(User.name == user_data.name).first()

        if user is None or not self.verify_password(
            user_data.password, user.password_hash
        ):
            error = 'Incorrect username or password'
            user = None
        else:
            user_model = models.User.from_orm(user)
            await self.redis_db.set(CURRENT_USER, user_model.json())

        return models.PageData(user=user, error=error)

    async def logout(self) -> None:
        await self.redis_db.delete(CURRENT_USER)
