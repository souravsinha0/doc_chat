import os
from pydantic_settings import BaseSettings, SettingsConfigDict

# This finds the absolute path of the folder containing THIS file (config.py)
current_dir = os.path.dirname(os.path.abspath(__file__))
env_file_path = os.path.join(current_dir, ".env")

class Settings(BaseSettings):
    DATABASE_URL: str
    LLM_PROVIDER: str = "OLLAMA"
    LLM_MODEL: str = "llama3"
    
    # API Keys
    OPENAI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    
    # Ollama
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    
    # Updated to use the absolute path
    model_config = SettingsConfigDict(
        env_file=env_file_path,
        env_file_encoding='utf-8',
        extra='ignore'  # This prevents errors if you have extra vars like EMBEDDING_DIM
    )

settings = Settings()