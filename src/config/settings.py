from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Settings(BaseSettings):
    yandex_disk_token: str
    yandex_disk_base_url: str = "https://cloud-api.yandex.net"
    test_user_login: str
    test_user_display_name: str

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent.parent.parent / ".env",
        env_file_encoding="utf-8"
    )


settings = Settings()
