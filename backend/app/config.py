from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE = Path(__file__).resolve().parents[1] / '.env'
load_dotenv(ENV_FILE)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_FILE, extra='ignore')

    database_url_ro: str
    llm_model: str = 'google_genai:gemini-3.5-flash'
    llm_rpm: float = 8
    max_rows: int = 1000


settings = Settings()