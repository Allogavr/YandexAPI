import time
import pytest
from jsonschema import validate, ValidationError

FILES_LIST_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["items", "limit", "offset"],
    "properties": {
        "items": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["name", "path", "type"],
                "properties": {
                    "name": {"type": "string"},
                    "path": {"type": "string"},
                    "type": {"type": "string", "enum": ["file", "dir"]},
                    "mime_type": {"type": ["string", "null"]},
                    "media_type": {"type": ["string", "null"]},
                    "size": {"type": ["integer", "null"]},
                    "created": {"type": ["string", "null"]},
                    "modified": {"type": ["string", "null"]},
                    "md5": {"type": ["string", "null"]},
                    "sha256": {"type": ["string", "null"]}
                }
            }
        },
        "limit": {"type": "integer"},
        "offset": {"type": "integer"}
    }
}


class TestFileList:

    @pytest.fixture(autouse=True)
    def setup(self, api_client):
        """Создаём тестовый файл и убеждаемся, что он появился"""
        self.test_folder = "/list_test"
        self.test_file = f"{self.test_folder}/test.txt"

        api_client.create_folder(self.test_folder)

        upload_link = api_client.get_upload_link(self.test_file, overwrite=True)
        assert upload_link["status_code"] == 200, "Не удалось получить ссылку для загрузки"

        upload_result = api_client.upload_file(upload_link["json"]["href"], b"test content")
        assert upload_result["status_code"] in (201, 202), f"Ошибка загрузки: {upload_result['status_code']}"

        file_ready = False
        for _ in range(5):
            if api_client.check_resource_exists(self.test_file):
                file_ready = True
                break
            time.sleep(1)
        assert file_ready, f"Файл {self.test_file} не появился после загрузки"

        yield

        api_client.delete_folder(self.test_folder, permanently=True)

    def test_get_files_list_structure(self, api_client):
        """Тест получения списка файлов с проверкой структуры ответа"""
        assert api_client.check_resource_exists(self.test_file), \
            f"Файл {self.test_file} не найден на диске перед тестом"

        result = api_client.get_files_list(limit=1000)
        assert result["status_code"] == 200, f"Expected 200, got {result['status_code']}"

        try:
            validate(instance=result["json"], schema=FILES_LIST_SCHEMA)
        except ValidationError as e:
            pytest.fail(f"Ответ не соответствует JSON Schema: {e}")

        assert result["json"]["limit"] == 1000
        assert result["json"]["offset"] == 0

        expected_path = f"disk:{self.test_file}"
        items = result["json"]["items"]
        found = any(item["name"] == "test.txt" and item["path"] == expected_path for item in items)
        assert found, f"Файл {expected_path} не найден в списке файлов (даже с limit=1000)"
