from pydantic import BaseSettings


class Settings(BaseSettings):
    server_host: str = '127.0.0.1'
    server_port: int = 8000
    redis_host: str = 'localhost'
    redis_port: int = 6379
    database_url: str = 'sqlite:///./isinstance/database.sqlite3'

    class Config:
        _env_file = ('.env',)
        _env_file_encoding = ('utf-8',)


settings = Settings()
