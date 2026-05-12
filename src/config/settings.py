from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    base_url: str = "http://localhost:3000"
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "qa_test"
    db_user: str = "qa"
    db_password: str = "qa_pass"
    api_token: str = ""
    headless: bool = True

    @field_validator("base_url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        if not v.startswith(("http://", "https://")):
            raise ValueError("base_url must start with http:// or https://")
        return v.rstrip("/")

settings = Settings()