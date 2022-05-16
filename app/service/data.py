from decimal import Decimal
from typing import Optional

import sqlalchemy.orm as so
from fastapi import Depends
from sqlalchemy import and_

from .. import models
from ..database import create_session
from ..models import Status
from ..tables import QuestionAuthor, QuestionPlayer, User


class DataHandler:
    @staticmethod
    def compare_money(current_money: str, required_money: str) -> bool:
        return Decimal(current_money) >= Decimal(required_money)

    @staticmethod
    def substr_money(current_money: str, required_money: str) -> str:
        money_dec = Decimal(current_money) - Decimal(required_money)
        return f'{money_dec:.2f}'

    def __init__(self, session: so.Session = Depends(create_session)):
        self.session = session

    def get_data_home(self, current_user: Optional[models.User]) -> models.PageData:
        # making query
        if current_user is not None:
            query = self.session.query(QuestionAuthor).filter(  # pragma: no cover
                and_(
                    QuestionAuthor.status == Status.WAITING,
                    QuestionAuthor.user_id != current_user.id,
                )
            )
        else:
            query = self.session.query(QuestionAuthor).filter(
                QuestionAuthor.status == Status.WAITING
            )
        questions_orm = query.all()

        questions = list(map(models.Question.from_orm, questions_orm))
        return models.PageData(questions=questions, user=current_user)

    def create_question(
        self, current_user: models.User, question_data: models.QuestionCreate
    ) -> models.PageData:
        error = None

        if self.compare_money(current_user.money, question_data.cost):
            user_money = self.substr_money(current_user.money, question_data.cost)
            current_user.money = user_money
            self.session.query(User).filter(User.id == current_user.id).update(
                {'money': user_money}
            )

            question_data.user_id = current_user.id
            question = QuestionAuthor(**question_data.dict())
            self.session.add(question)

            error = 'Question is posted successfully!'

            self.session.commit()

        else:
            error = "Error: you don't have enough money for posting this question!"

        return models.PageData(user=current_user, error=error)

    def get_questions_author(self, current_user: models.User) -> models.PageData:
        query = self.session.query(QuestionAuthor).filter(
            QuestionAuthor.user_id == current_user.id
        )

        questions_orm = query.all()
        questions = list(map(models.Question.from_orm, questions_orm))

        return models.PageData(questions=questions, user=current_user)

    def get_questions_player(self, current_user: models.User) -> models.PageData:
        query = (
            self.session.query(QuestionPlayer.status, QuestionAuthor)
            .filter(QuestionPlayer.user_id == current_user.id)
            .join(QuestionPlayer)
        )

        quest_data = query.all()

        # change status to user's
        questions = []
        for status, question_orm in quest_data:
            question = models.Question.from_orm(question_orm)
            question.status = status
            questions.append(question)

        return models.PageData(user=current_user, questions=questions)
