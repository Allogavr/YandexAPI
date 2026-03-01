import pytest
from httpx import Client
from src.api.client import YandexDiskClient


@pytest.fixture(scope="session")
def api_client() -> YandexDiskClient:
    client = YandexDiskClient()
    yield client
    client.close()


@pytest.fixture
def unauth_http_client() -> Client:
    client = Client()
    yield client
    client.close()
