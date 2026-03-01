import sys
import pytest
import httpx
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from src.config.settings import settings
from src.api.client import YandexDiskClient


@pytest.fixture(scope="session")
def api_client() -> YandexDiskClient:
    if not settings.yandex_disk_token:
        pytest.skip("YANDEX_DISK_TOKEN не установлен в .env")
    client = YandexDiskClient()
    yield client
    client.close()


@pytest.fixture(scope="function")
def unauth_http_client() -> httpx.Client:
    client = httpx.Client(base_url=settings.yandex_disk_base_url)
    yield client
    client.close()
