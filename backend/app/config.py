from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./feedback.db"
    JWT_SECRET: str = "dev-secret-change-me"
    JWT_ALG: str = "HS256"
    ACCESS_TOKEN_EXPIRES_MIN: int = 60 * 24  # 24h
    CORS_ORIGINS: str = "*"

settings = Settings()
