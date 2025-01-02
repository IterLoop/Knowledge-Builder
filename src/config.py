from pydantic import BaseSettings

class Settings(BaseSettings):
    MONGODB_URL: str
    OPENAI_API_KEY: str
    GOOGLE_API_KEY: str
    YOUTUBE_API_KEY: str
    
    class Config:
        env_file = "secrets/.env"

settings = Settings()
