import httpx
from typing import Dict, Any, Optional
from src.config.settings import settings
from src.api.endpoints import DiskEndpoints


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

    def create_folder(self, folder_path: str) -> Dict[str, Any]:
        if not folder_path.startswith('/'):
            folder_path = '/' + folder_path

        params = {"path": folder_path}
        response = self._client.put(
            DiskEndpoints.RESOURCES,
            headers=self.headers,
            params=params
        )

        return {
            "status_code": response.status_code,
            "json": response.json() if response.text else {}
        }

    def delete_folder(self, folder_path: str, permanently: bool = False) -> Dict[str, Any]:
        if not folder_path.startswith('/'):
            folder_path = '/' + folder_path

        params = {
            "path": folder_path,
            "permanently": str(permanently).lower()
        }

        response = self._client.delete(
            DiskEndpoints.RESOURCES,
            headers=self.headers,
            params=params
        )

        result = {
            "status_code": response.status_code,
            "json": response.json() if response.text else {}
        }

        if response.status_code == 202 and response.text:
            result["operation_href"] = response.json().get("href")

        return result

    def get_trash_contents(self, path: str = "/") -> Dict[str, Any]:
        params = {"path": path}
        response = self._client.get(
            DiskEndpoints.TRASH,
            headers=self.headers,
            params=params
        )
        return {
            "status_code": response.status_code,
            "json": response.json() if response.text else {}
        }

    def restore_from_trash(self, trash_path: str, new_name: Optional[str] = None,
                           overwrite: bool = False) -> Dict[str, Any]:
        params = {"path": trash_path, "overwrite": str(overwrite).lower()}
        if new_name:
            params["name"] = new_name

        response = self._client.put(
            DiskEndpoints.TRASH_RESTORE,
            headers=self.headers,
            params=params
        )

        result = {
            "status_code": response.status_code,
            "json": response.json() if response.text else {}
        }

        if response.status_code == 202 and response.text:
            result["operation_href"] = response.json().get("href")

        return result

    def check_resource_exists(self, path: str) -> bool:
        if not path.startswith('/'):
            path = '/' + path

        response = self._client.get(
            DiskEndpoints.RESOURCES,
            headers=self.headers,
            params={"path": path}
        )
        return response.status_code == 200

    def wait_for_operation(self, operation_href: str, timeout: int = 30, interval: int = 1) -> bool:
        import time
        start_time = time.time()
        while time.time() - start_time < timeout:
            response = self._client.get(operation_href)
            if response.status_code == 200:
                status = response.json().get("status")
                if status == "success":
                    return True
                elif status == "failure":
                    return False
            time.sleep(interval)
        return False

    def close(self):
        self._client.close()
