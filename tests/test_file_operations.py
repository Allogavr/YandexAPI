import pytest
from src.models.disk import LinkResponse, ResourceInfo, ApiError

class TestFileUploadCopy:
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, api_client):
        self.input_folder = "/input_data"
        self.output_folder = "/output_data"
        api_client.create_folder(self.input_folder)
        api_client.create_folder(self.output_folder)
        yield
        api_client.delete_folder(self.input_folder, permanently=True)
        api_client.delete_folder(self.output_folder, permanently=True)

    def test_upload_copy_scenario(self, api_client, test_text_file):
        remote_path = f"{self.input_folder}/data.txt"
        upload_link_resp = api_client.get_upload_link(remote_path, overwrite=True)
        assert upload_link_resp["status_code"] == 200
        LinkResponse.model_validate(upload_link_resp["json"])

        with open(test_text_file, 'rb') as f:
            file_content = f.read()
        upload_result = api_client.upload_file(upload_link_resp["json"]["href"], file_content)
        assert upload_result["status_code"] in (201, 202)

        meta = api_client.get_resource_meta(remote_path)
        assert meta["status_code"] == 200
        ResourceInfo.model_validate(meta["json"])

        copy_result = api_client.copy_resource(remote_path, f"{self.output_folder}/data.txt", overwrite=False)
        assert copy_result["status_code"] == 201

        if copy_result["status_code"] == 202:
            assert api_client.wait_for_operation(copy_result["operation_href"])

        meta_copy_resp = api_client.get_resource_meta(f"{self.output_folder}/data.txt")
        assert meta_copy_resp["status_code"] == 200
        meta_copy = meta_copy_resp["json"]

        assert meta_copy["name"] == "data.txt"
        assert "mime_type" in meta_copy
        assert "media_type" in meta_copy

        copy_again = api_client.copy_resource(remote_path, f"{self.output_folder}/data.txt", overwrite=False)
        assert copy_again["status_code"] == 409
        ApiError.model_validate(copy_again["json"])


class TestFileDownload:
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, api_client):
        self.folder = "/sdet_data"
        self.file_path = f"{self.folder}/data.txt"
        self.file_content = b"username=SDET\npassword=secret_key"
        api_client.create_folder(self.folder)
        upload_link = api_client.get_upload_link(self.file_path, overwrite=True)
        assert upload_link["status_code"] == 200
        api_client.upload_file(upload_link["json"]["href"], self.file_content)
        yield
        api_client.delete_folder(self.folder, permanently=True)

    def test_download_file(self, api_client):
        download_link_resp = api_client.get_download_link(self.file_path)
        assert download_link_resp["status_code"] == 200
        LinkResponse.model_validate(download_link_resp["json"])

        downloaded = api_client.download_file(download_link_resp["json"]["href"])
        assert downloaded == self.file_content
