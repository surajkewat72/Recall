from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Application settings using Pydantic."""
    
    # API Settings
    PROJECT_NAME: str = "RAG Google Drive API"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False
    
    # Security
    SECRET_KEY: str = "development_secret_key"
    
    # External APIs
    OPENAI_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None
    
    # GDrive Settings
    GDRIVE_CREDENTIALS_FILE: str = "credentials.json"
    GDRIVE_TOKEN_FILE: str = "token.json"
    
    # Vector Database
    VECTOR_STORE_URL: Optional[str] = None
    VECTOR_STORE_API_KEY: Optional[str] = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=True)

# Create a global settings object
settings = Settings()
