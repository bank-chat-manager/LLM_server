from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    OLLAMA_API_URL: str = "http://localhost:11434"

    class Config:
        env_file = ".env"

settings = Settings()
