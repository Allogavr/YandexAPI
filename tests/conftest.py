import sys
import pytest
import httpx
import tempfile
import os
import time
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


@pytest.fixture(scope="function")
def test_text_file():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write("Это тестовый файл для Яндекс.Диск API")
        temp_path = f.name

    yield temp_path

    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture(scope="function")
def unique_folder_name():
    return f"test_folder_{int(time.time())}"
