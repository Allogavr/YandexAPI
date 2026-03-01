import httpx
from typing import Dict, Any
from src.config.settings import settings


class YandexDiskClient:
    def __init__(self):
        self.base_url = settings.yandex_disk_base_url
        self.headers = {
            "Authorization": f"OAuth {settings.yandex_disk_token}",
            "Content-Type": "application/json"
        }
        self._client = httpx.Client(base_url=self.base_url)

    def get_disk_info(self) -> Dict[str, Any]:
        response = self._client.get("/v1/disk/", headers=self.headers)
        return {
            "status_code": response.status_code,
            "json": response.json()
        }

    def get_disk_info_unauth(self, http_client: httpx.Client) -> Dict[str, Any]:
        response = http_client.get("/v1/disk/")
        return {
            "status_code": response.status_code,
            "json": response.json()
        }

    def close(self):
        self._client.close()
