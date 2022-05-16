from __future__ import annotations

from enum import Enum
from typing import List, Optional

from fastapi import Form
from pydantic import BaseModel, Field


class Status(str, Enum):
    WAITING = 'waiting'
    PLAYING = 'playing'
    DEFEAT = 'defeat'
    WIN = 'win'


class UserCreate(BaseModel):
    name: str
    password: str

    @classmethod
    def from_form(
        cls,
        name: str = Form(...),
        password: str = Form(...),
    ) -> UserCreate:
        return cls(name=name, password=password)


class User(BaseModel):
    id: int
    name: str
    money: str

    class Config:
        orm_mode = True


class QuestionCreate(BaseModel):
    user_id: Optional[int]
    title: str
    desc: str
    cost: str
    answer: str

    @classmethod
    def from_form(
        cls,
        title: str = Form(...),
        desc: str = Form(...),
        cost: str = Form(...),
        answer: str = Form(...),
    ) -> QuestionCreate:
        return cls(title=title, desc=desc, cost=cost, answer=answer)


class Question(BaseModel):
    id: int
    user_id: int = Field(..., exclude=True)
    title: str
    desc: str
    cost: str
    answer: str
    status: Status

    class Config:
        orm_mode = True


class PageData(BaseModel):
    error: Optional[str]
    user: Optional[User]
    questions: Optional[List[Question]]

    class Config:
        orm_mode = True


class QuestionData(BaseModel):
    user: User
    question: Question
    msg: Optional[str]

    class Config:
        orm_mode = True


class Expire(BaseModel):
    player_id: int
    question_id: int
