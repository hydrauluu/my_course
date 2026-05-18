from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@db:5432/python_course"
    DATABASE_URL_SYNC: str = "postgresql+psycopg2://postgres:postgres@db:5432/python_course"
    REDIS_URL: str = "redis://redis:6379/0"

    GITHUB_CLIENT_ID: str = ""
    GITHUB_CLIENT_SECRET: str = ""
    GITHUB_REDIRECT_URI: str = "http://localhost:8000/api/auth/github/callback"
    GITHUB_WEBHOOK_SECRET: str = ""
    GITHUB_BOT_TOKEN: str = ""

    CLAUDE_API_KEY: str = ""
    CLAUDE_MODEL: str = "claude-sonnet-4-20250514"

    JWT_SECRET: str = "super-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24

    FRONTEND_URL: str = "http://localhost:5173"

    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_DEFAULT: str = "60/minute"

    class Config:
        env_file = ".env"


settings = Settings()
