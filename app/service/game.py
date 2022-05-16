from decimal import Decimal
from typing import Optional, Union

import sqlalchemy.orm as so
from aioredis import Redis
from fastapi import Depends

from .. import models
from ..database import create_session, get_redis
from ..models import Status
from ..tables import QuestionAuthor, QuestionPlayer, User
from .utils import PLAY_TIME


class GameController:
    @staticmethod
    def compare_money(money: str, required_money: str) -> bool:
        return Decimal(money) >= Decimal(required_money)

    @staticmethod
    def subtract_money(money: str, required_money: str) -> str:
        money_dec = Decimal(money) - Decimal(required_money)
        return f'{money_dec:.2f}'

    @staticmethod
    def check_answer(answer: str, correct_answer: str) -> bool:
        answer = answer.strip().lower()
        correct_answer = correct_answer.strip().lower()
        return answer == correct_answer

    @staticmethod
    def calculate_win(user_money: Union[str, Decimal], cost: str) -> str:
        money_dec = Decimal(user_money) + 2 * Decimal(cost)
        return f'{money_dec:.2f}'

    def __init__(
        self,
        redis_db: Redis = Depends(get_redis),
        session: so.Session = Depends(create_session),
    ):
        self.redis_db = redis_db
        self.session = session

    async def play_question(
        self, question_id: int, current_user: models.User
    ) -> Optional[models.QuestionData]:
        question = (
            self.session.query(QuestionAuthor)
            .filter(QuestionAuthor.id == question_id)
            .first()
        )

        # question is available:
        if question is None or question.status != Status.WAITING:
            return None

        # user has enough money to play:
        if not self.compare_money(current_user.money, question.cost):
            return None

        question.status = Status.PLAYING

        # update user's money
        user_money = self.subtract_money(current_user.money, question.cost)
        current_user.money = user_money
        user = self.session.query(User).filter(User.id == current_user.id).first()
        user.money = user_money

        self.session.flush()
        self.session.commit()

        user = self.session.query(User).filter(User.id == current_user.id).first()

        # add to expire queue
        expire_json = models.Expire(
            question_id=question_id, player_id=current_user.id
        ).json()
        await self.redis_db.setex(expire_json, PLAY_TIME, b'expire')

        question = models.Question.from_orm(question)
        return models.QuestionData(question=question, user=current_user)

    async def process_answer(
        self, question_id: int, answer: str, current_user: models.User
    ) -> Optional[models.QuestionData]:
        msg = None

        question = (
            self.session.query(QuestionAuthor)
            .filter(QuestionAuthor.id == question_id)
            .first()
        )

        if question is None:
            return None

        if question.status != Status.PLAYING:  # expire
            msg = 'Time is over!'
        elif self.check_answer(answer, question.answer):  # right answer
            msg = 'You win!'

            # change user's money
            money_win = self.calculate_win(current_user.money, question.cost)
            current_user.money = money_win
            self.session.query(User).update({'money': money_win})

            # change author's question status
            question.status = Status.DEFEAT

            question_player = QuestionPlayer(
                user_id=current_user.id,
                status=Status.WIN,
                question_id=question_id,
            )

            self.session.add(question_player)
        else:  # wrong answer
            msg = 'You lose!'

            # change author's money
            author = (
                self.session.query(User).filter(User.id == question.user_id).first()
            )
            money_win = self.calculate_win(author.money, question.cost)
            author.money = money_win

            # change author's question status
            question.status = Status.WIN

            # add to Question Played table
            question_player = QuestionPlayer(
                user_id=current_user.id,
                status=Status.DEFEAT,
                question_id=question_id,
            )

            self.session.add(question_player)

        # delete data id from expiring
        expire_json = models.Expire(
            question_id=question_id, player_id=current_user.id
        ).json()
        await self.redis_db.delete(expire_json)

        self.session.commit()

        return models.QuestionData(
            question=models.Question.from_orm(question), user=current_user, msg=msg
        )

    async def process_question_timing(self) -> None:
        pub = self.redis_db.pubsub()
        await pub.subscribe('__keyevent@0__:expired')

        async for msg in pub.listen():
            if msg['type'] == 'subscribe':
                continue
            expire_json = msg['data']
            data = models.Expire.parse_raw(expire_json)

            question = (
                self.session.query(QuestionAuthor)
                .filter(QuestionAuthor.id == data.question_id)
                .first()
            )

            if question.status == Status.PLAYING:
                # change author's data:
                question.status = Status.WIN

                author = (
                    self.session.query(User).filter(User.id == question.user_id).first()
                )
                money_win = self.calculate_win(author.money, question.cost)
                author.money = money_win

                # change user's data:
                question_player = QuestionPlayer(
                    user_id=data.player_id,
                    status=Status.DEFEAT,
                    question_id=data.question_id,
                )

                self.session.add(question_player)

                self.session.commit()
