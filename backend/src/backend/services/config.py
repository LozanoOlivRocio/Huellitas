from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE = Path(__file__).resolve().parents[3] / '.env'


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding='utf-8',
        extra='ignore',
    )
    sqlserver_connection_string: str
    allowed_origins: list[str] = ["http://localhost:4200", "http://127.0.0.1:4200"]
    cookie_secure: bool = False
    session_days: int = 7


def get_settings() -> Settings:
    return Settings()
