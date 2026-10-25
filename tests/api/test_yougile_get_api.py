import allure
import pytest


@allure.feature("Projects API")
@allure.story("Получение проекта")
@pytest.mark.api
class TestGetProject:
    """Тесты на получение проекта."""

    @allure.title("Получение проекта по валидному ID")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_project_id_positive(self, api_client, created_project):
        """
        Предусловие: проект создан фикстурой created_project.
        Проверяем, что GET возвращает 200 и совпадающий id.
        """
        with allure.step("Шаг 1. Извлечь ID из фикстуры"):
            project_id = created_project["id"]

        with allure.step("Шаг 2. Получить проект по ID"):
            response = api_client.get_project(project_id)
            assert response.status_code == 200, (
                f"Не удалось получить проект с {project_id}. "
                f"Статус: {response.status_code}")

        with allure.step("Шаг 3. Проверить соответствие ID"):
            assert response.json()["id"] == project_id

        # Постусловие: удаление — в фикстуре created_project

    @allure.title("Получение проекта по несуществующему ID (Null UUID)")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_project_negative(self, api_client):
        """
        Null UUID → 404 Not Found с сообщением 'Проект не найден'.
        """
        invalid_project_id = "00000000-0000-0000-0000-000000000000"

        with allure.step(f"Шаг 1. GET проекта по ID {invalid_project_id}"):
            response = api_client.get_project(invalid_project_id)

        with allure.step("Шаг 2. Проверить статус и тело сообщения об ошибке"):
            assert response.status_code == 404, (
                f"Ожидался статус 404, получен {response.status_code}."
                f"Текст:{response.text}")
            error_body = response.json()
            assert "error" in error_body, "В ответе отсутствует поле 'error'"
            assert error_body["error"] == "Not Found"
            assert error_body.get("message") == "Проект не найден", (
                f"Ожидалось сообщение 'Проект не найден',"
                f"получено {error_body.get('message')}")

        # Постусловие: удаление — в фикстуре created_project
