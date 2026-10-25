import uuid
import allure
import pytest


@allure.feature("Projects API")
@allure.story("Изменение проекта")
@pytest.mark.api
class TestChangeProject:
    """Тесты на изменение проекта."""

    @allure.title("Изменение названия проекта на валидное")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_change_project_positive(self, api_client, created_project):
        """
        Предусловие: проект создан фикстурой created_project.
        Меняем название на уникальное и проверяем, что GET возвращает новое."""

        with allure.step("Шаг 1. Извлечь ID из фикстуры"):
            project_id = created_project["id"]

        with allure.step("Шаг 2. Изменить название проекта"):
            new_title = uuid.uuid4().hex[:3]
            response = api_client.change_project(project_id, new_title)
            assert response.status_code == 200, (
                f"Не удалось обновить проект. Статус {response.status_code}.")

        with allure.step("Шаг 3. Получить обновлённый проект по id"):
            response = api_client.get_project(project_id)
            assert response.status_code == 200, (
                f"Не удалось получить проект с {project_id}. "
                f"Статус: {response.status_code}")

        with allure.step("Шаг 4. Проверить новое название"):
            update_body = response.json()
            assert update_body["title"] == new_title, (
                f"Название не обоновилось. Ожидалось: '{new_title}', "
                f"получно: '{update_body["title"]}']")

        # Постусловие: удаление — в фикстуре created_project

    @allure.title("Изменение проекта с числом вместо строки")
    @allure.severity(allure.severity_level.NORMAL)
    def test_change_project_invalid_title_type(
            self, api_client, created_project):
        """
        Предусловие: проект создан фикстурой created_project.
        Негативный сценарий: обновление существующего проекта,
        где название передается в числовом формате (int)"""

        with allure.step("Шаг 1. Извлечь ID из фикстуры"):
            project_id = created_project["id"]

        with allure.step(
                "Шаг 2. Получить проект и сохранить валидное название"):
            response = api_client.get_project(project_id)
            assert response.status_code == 200, (
                f"Не удалось получить проект "
                f"с {project_id}. Статус: {response.status_code}")
            valid_title = response.json()["title"]

        with allure.step(
                "Шаг 3. Изменить название проекта с числом вместо строки"
        ):
            response = api_client.change_project(project_id, 1)

        with allure.step("Шаг 4. Проверить статус и тело ответа"):
            assert response.status_code == 400, (
                f"Ожидался статус 400, получен {response.status_code}."
                f"Текст:{response.text}")
            error_body = response.json()
            assert "error" in error_body, "В ответе отсутствует поле 'error'"
            assert error_body["error"] == "Bad Request"
            assert error_body["message"][0] == "title must be a string", (
                f"Ожидалось сообщение 'title must be a string', "
                f"получено {error_body["message"][0]}")

        with allure.step("Шаг 5. Убедиться, что название не изменилось"):
            response = api_client.get_project(project_id)
            assert response.status_code == 200
            assert response.json()["title"] == valid_title, \
                "Название проекта изменилось, не смотрая на ошибку 400"

        # Постусловие: удаление — в фикстуре created_project
