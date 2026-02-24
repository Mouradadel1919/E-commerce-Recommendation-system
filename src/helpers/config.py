from pydantic_settings import BaseSettings

class Settings(BaseSettings):

    APP_NAME: str
    APP_VERSION: str

    MONGODB_URL: str
    MONGODB_DATABASE: str

    HF_TOKE: str

    VECTOR_DB_PORT: int

    SENTENCE_TRANSFORMER: str

    class Config:
        env_file= ".env"

def get_setting():
    return Settings()