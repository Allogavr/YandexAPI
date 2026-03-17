import time
import pytest
from src.models.disk import LinkResponse, ApiError, TrashContents


class TestFolderOperations:

    @pytest.mark.folders
    def test_create_folder_success(self, api_client, unique_folder_name):
        result = api_client.create_folder(unique_folder_name)
        assert result["status_code"] == 201
        LinkResponse.model_validate(result["json"])
        assert api_client.check_resource_exists(f"/{unique_folder_name}") is True

    @pytest.mark.folders
    def test_delete_folder_to_trash(self, api_client, unique_folder_name):
        api_client.create_folder(unique_folder_name)
        assert api_client.check_resource_exists(f"/{unique_folder_name}") is True
        time.sleep(1)
        max_retries = 3
        for attempt in range(max_retries):
            result = api_client.delete_folder(unique_folder_name, permanently=False)
            if result["status_code"] in (204, 202):
                break
            elif result["status_code"] == 423 and attempt < max_retries - 1:
                time.sleep(2)
                continue
            else:
                pytest.fail(f"Expected 204 or 202, got {result['status_code']}")
        if result["status_code"] in (204, 202):
            if result["status_code"] == 202 and "operation_href" in result:
                assert api_client.wait_for_operation(result["operation_href"]), "Delete operation failed"
            assert api_client.check_resource_exists(f"/{unique_folder_name}") is False
        else:
            pytest.fail(f"Unexpected status code: {result['status_code']}")

    @pytest.mark.folders
    def test_restore_folder_from_trash(self, api_client, unique_folder_name):
        api_client.create_folder(unique_folder_name)
        assert api_client.check_resource_exists(f"/{unique_folder_name}") is True
        delete_result = api_client.delete_folder(unique_folder_name, permanently=False)
        if delete_result["status_code"] == 202 and "operation_href" in delete_result:
            assert api_client.wait_for_operation(delete_result["operation_href"]), "Delete operation failed"
        # Wait for disappearance
        for _ in range(5):
            if not api_client.check_resource_exists(f"/{unique_folder_name}"):
                break
            time.sleep(1)
        # Get trash contents and find folder
        trash_path = None
        for _ in range(5):
            trash_contents = api_client.get_trash_contents("/")
            assert trash_contents["status_code"] == 200
            items = trash_contents["json"].get("_embedded", {}).get("items", [])
            for item in items:
                if item["name"] == unique_folder_name and item["type"] == "dir":
                    trash_path = item["path"]
                    break
            if trash_path:
                break
            time.sleep(1)
        assert trash_path, f"Folder {unique_folder_name} not found in trash"
        # Restore
        restore_result = api_client.restore_from_trash(trash_path)
        assert restore_result["status_code"] == 201
        LinkResponse.model_validate(restore_result["json"])
        assert api_client.check_resource_exists(f"/{unique_folder_name}") is True

    @pytest.mark.folders
    def test_create_existing_folder(self, api_client, unique_folder_name):
        api_client.create_folder(unique_folder_name)
        result = api_client.create_folder(unique_folder_name)
        assert result["status_code"] == 409
        ApiError.model_validate(result["json"])

    @pytest.mark.folders
    def test_delete_nonexistent_folder(self, api_client):
        result = api_client.delete_folder("/folder_that_does_not_exist_123456")
        assert result["status_code"] == 404
        ApiError.model_validate(result["json"])