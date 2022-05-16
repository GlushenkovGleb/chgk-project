import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base

from .models import Status

Base = declarative_base()  # type: ignore


class User(Base):  # type: ignore
    __tablename__ = 'user'

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(30), unique=True, nullable=False)
    money = sa.Column(sa.String(20), nullable=False, default='1000.00')
    password_hash = sa.Column(sa.String)

    def __repr__(self) -> str:
        return (
            f'User(id: {self.id}, name: {self.name},'
            f' money: {self.money}, password_hash: {self.password_hash})'
        )


class QuestionAuthor(Base):  # type: ignore
    __tablename__ = 'question_author'

    id = sa.Column(sa.Integer, primary_key=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey(User.id), nullable=False)
    title = sa.Column(sa.String(50), nullable=False)
    desc = sa.Column(sa.Text, nullable=False)
    cost = sa.Column(sa.String(25), nullable=False)
    answer = sa.Column(sa.String(), nullable=False)
    status = sa.Column(sa.Enum(Status), default=Status.WAITING, nullable=False)

    def __repr__(self) -> str:
        return (
            f'QA(id: {self.id}, user_id: {self.user_id},'
            f' title: {self.title[:10]}, desc: {self.desc[:10]}, '
            f'answer: {self.answer}, status: {self.status})'
        )


class QuestionPlayer(Base):  # type: ignore
    __tablename__ = 'question_player'

    id = sa.Column(sa.Integer, primary_key=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey(User.id), nullable=False)
    question_id = sa.Column(
        sa.Integer, sa.ForeignKey(QuestionAuthor.id), nullable=False
    )
    status = sa.Column(sa.Enum(Status), nullable=False)

    def __repr__(self) -> str:
        return (
            f'QP(id: {self.id}, user_id: {self.user_id}, '
            f'question_id: {self.question_id}, status: {self.status})'
        )
