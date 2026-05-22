import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "ElseaAI Platform"
    MYSQL_URL: str = os.environ.get("MYSQL_URL", "mysql+aiomysql://elsea:elseapassword@localhost:3306/elsea_db")
    MONGO_URL: str = os.environ.get("MONGO_URL", "mongodb://elsea:elseapassword@localhost:27017/elsea_db?authSource=admin")
    QDRANT_URL: str = os.environ.get("QDRANT_URL", "http://localhost:6333")
    REDIS_URL: str = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    OLLAMA_URL: str = os.environ.get("OLLAMA_URL", "http://localhost:11434")
    
    class Config:
        env_file = ".env"

settings = Settings()
