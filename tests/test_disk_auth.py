from src.config.settings import settings
from src.models.disk import DiskResponse, ApiError


class TestDiskAuthorization:

    def test_valid_token_authorization(self, api_client):
        """Тест 1: Авторизация с валидным токеном"""
        result = api_client.get_disk_info()

        assert result["status_code"] == 200
        assert result["json"]["user"]["login"] == settings.test_user_login
        assert result["json"]["user"]["display_name"] == settings.test_user_display_name

        DiskResponse.model_validate(result["json"])

    def test_unauthorized_access(self, unauth_http_client, api_client):
        """Тест 2: Доступ без токена"""
        result = api_client.get_disk_info_unauth(unauth_http_client)

        assert result["status_code"] == 401
        assert "error" in result["json"]
        assert "description" in result["json"]
        assert "message" in result["json"]

        ApiError.model_validate(result["json"])
