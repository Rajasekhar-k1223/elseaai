import os
from pydantic_settings import BaseSettings

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class Settings(BaseSettings):
    PROJECT_NAME: str = "ElseaAI Platform"
    MYSQL_URL: str = os.environ.get("MYSQL_URL", "mysql+aiomysql://elsea:elseapassword@localhost:3306/elsea_db")
    MONGO_URL: str = os.environ.get("MONGO_URL", "mongodb://elsea:elseapassword@localhost:27017/elsea_db?authSource=admin")
    QDRANT_URL: str = os.environ.get("QDRANT_URL", "http://localhost:6333")
    REDIS_URL: str = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    OLLAMA_URL: str = os.environ.get("OLLAMA_URL", "http://localhost:11434")
    GROQ_API_KEY: str = os.environ.get("GROQ_API_KEY", "")
    JWT_SECRET: str = os.environ.get("JWT_SECRET", "supersecretjwtkey_change_in_production")
    JWT_ALGORITHM: str = os.environ.get("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
    BACKEND_CORS_ORIGINS: str = os.environ.get("BACKEND_CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
    SQLALCHEMY_ECHO: bool = os.environ.get("SQLALCHEMY_ECHO", "false").lower() in ("1", "true", "yes")
    ORIGINAL_DOCUMENTS_DIR: str = os.environ.get("ORIGINAL_DOCUMENTS_DIR", os.path.join(BASE_DIR, "storage", "originals"))
    FINE_TUNE_OUTPUT_DIR: str = os.environ.get("FINE_TUNE_OUTPUT_DIR", os.path.join(BASE_DIR, "storage", "fine_tune"))

    class Config:
        env_file = ".env"

settings = Settings()
