
import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE = Path(__file__).resolve().parents[1] / '.env'
load_dotenv(ENV_FILE)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        extra='ignore'
    )

    database_url_ro: str

    llm_model: str = 'google_genai:gemini-3.5-flash'
    llm_rpm: float = 8
    max_rows: int = 1000

    # Configuración de rotación de API Keys
    active_google_key: int = 1
    google_api_key_1: str = ''
    google_api_key_2: str = ''

    # API Key de Groq
    groq_api_key: str = ''

    @property
    def google_api_key(self) -> str:
        return (
            self.google_api_key_1
            if self.active_google_key == 1
            else self.google_api_key_2
        )


settings = Settings()

# Exportar las claves para que cada proveedor de LangChain
# encuentre su propia variable de entorno
for name, value in {
    'GOOGLE_API_KEY': settings.google_api_key,
    'GROQ_API_KEY': settings.groq_api_key,
}.items():
    if value:
        os.environ.setdefault(name, value)
