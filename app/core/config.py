from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    DATABASE_URL: str
    SECRET_KEY: str

    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]
    PROJECT_NAME: str = "Product Catalog API"
    API_PREFIX: str = "/api"

    MEDIA_DIR: str = "media"
    MEDIA_URL: str = "/media"
    BASE_URL: str = "http://localhost:8000"
    ALLOWED_IMAGE_TYPES: list[str] = ["image/jpeg", "image/png", "image/webp"]
    MAX_IMAGE_SIZE_MB: int = 5


settings = Settings()
