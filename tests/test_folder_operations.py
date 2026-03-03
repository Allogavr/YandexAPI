import pytest
from src.models.disk import LinkResponse, TrashContents


class TestFolderOperations:

    @pytest.mark.folders
    def test_create_folder_success(self, api_client, unique_folder_name):
        """Тест 3: Успешное создание папки"""
        result = api_client.create_folder(unique_folder_name)

        assert result["status_code"] == 201, f"Expected 201, got {result['status_code']}"

        assert "href" in result["json"]
        assert "method" in result["json"]
        assert result["json"]["method"] == "GET"

        LinkResponse.model_validate(result["json"])

        assert api_client.check_resource_exists(f"/{unique_folder_name}") is True

    @pytest.mark.folders
    def test_delete_folder_to_trash(self, api_client, unique_folder_name):
        """Тест 4: Удаление папки в корзину"""
        api_client.create_folder(unique_folder_name)
        assert api_client.check_resource_exists(f"/{unique_folder_name}") is True

        result = api_client.delete_folder(unique_folder_name, permanently=False)

        assert result["status_code"] in (204, 202), f"Expected 204 or 202, got {result['status_code']}"

        if result["status_code"] == 202 and "operation_href" in result:
            assert api_client.wait_for_operation(result["operation_href"]), "Delete operation failed"

        assert api_client.check_resource_exists(f"/{unique_folder_name}") is False

    @pytest.mark.folders
    def test_restore_folder_from_trash(self, api_client, unique_folder_name):
        """Тест 5: Восстановление папки из корзины"""
        api_client.create_folder(unique_folder_name)
        assert api_client.check_resource_exists(f"/{unique_folder_name}") is True

        delete_result = api_client.delete_folder(unique_folder_name, permanently=False)
        if delete_result["status_code"] == 202 and "operation_href" in delete_result:
            assert api_client.wait_for_operation(delete_result["operation_href"]), "Delete operation failed"
        assert api_client.check_resource_exists(f"/{unique_folder_name}") is False

        trash_contents = api_client.get_trash_contents("/")
        assert trash_contents["status_code"] == 200

        embedded = trash_contents["json"].get("_embedded", {})
        items = embedded.get("items", [])
        folder_item = None
        for item in items:
            if item["name"] == unique_folder_name and item["type"] == "dir":
                folder_item = item
                break

        assert folder_item is not None, f"Папка {unique_folder_name} не найдена в корзине"

        trash_data = TrashContents.model_validate(embedded)
        assert len(trash_data.items) > 0

        trash_path = folder_item["path"]

        restore_result = api_client.restore_from_trash(trash_path)
        assert restore_result["status_code"] == 201, f"Expected 201, got {restore_result['status_code']}"

        LinkResponse.model_validate(restore_result["json"])

        assert api_client.check_resource_exists(f"/{unique_folder_name}") is True
