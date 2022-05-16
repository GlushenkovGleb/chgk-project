import uvicorn

from .database import init_db

if __name__ == '__main__':
    init_db()
    uvicorn.run(
        'app.app:app',
    )
