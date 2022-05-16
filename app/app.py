from fastapi import FastAPI

from .routers import auth, game, question

app = FastAPI()
app.include_router(auth.router)
app.include_router(question.router)
app.include_router(game.router)
