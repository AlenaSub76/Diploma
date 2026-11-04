import allure
import pytest


@allure.feature("Projects API")
@allure.story("Создание проекта")
@pytest.mark.api
class TestCreateProject:
    """Тесты на создание проекта."""

    @allure.title("Создание проекта с валидным названием")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_create_project_positive(self, api_client):
        """Тест проверяет полный цикл жизни проекта:
        создание->чтение->проверка данных->удаление"""

        with allure.step(
                "Шаг 1. Создать проект (название сгенерируется автоматически)"
        ):
            response = api_client.create_project()
            # Проверить успешное создание проекта
            assert response.status_code == 201, (
                f"Проект не создался, получен {response.status_code}. "
                f"Текст:{response.text}")

        with allure.step(
                "Шаг 2. Извлечь ID и запомнить отправленное название"):
            project_id = response.json()["id"]
            expected_title = api_client.last_created_title

        with allure.step("Шаг 3. Получить проект по ID"):
            response = api_client.get_project(project_id)
            assert response.status_code == 200, (
                f"Не удалось получить проект с {project_id}. "
                f"Статус: {response.status_code}")

        with allure.step("Шаг 4. Сравнить название из GET с отправленным"):
            response_body = response.json()
            assert "title" in response_body, (
                "В ответе отсутствует поле 'title'")
            assert response_body["title"] == expected_title, (
                f"Название не совпадает. Отправляли '{expected_title}', "
                f"получили '{response_body['title']}'"
            )

        with allure.step("Шаг 5. Удалить созданный проект"):
            response = api_client.delete_project(project_id)
            assert response.status_code == 200, (
                f"Не удалось удалить проект {project_id}. "
                f"Статус: {response.status_code}")

    @allure.title("Создание проекта с пустым названием")
    @allure.severity(allure.severity_level.NORMAL)
    def test_create_project_negative(self, api_client):
        """Тест проверяет, что API возвращает ошибку 400
        и соответствие тела ответа документации"""
        with allure.step("Шаг 1. Создать проект с пустым названием"):
            project_title = ""
            response = api_client.create_project(project_title)
        with allure.step("Шаг 2. Проверить HTTP-статус"):
            assert response.status_code == 400, (
                f"Ожидался HTTP-статус 400 для пустого title, "
                f"получен {response.status_code}."
                f"Текст:{response.text}")

        with allure.step("Шаг 3. Проверить тело ответа"):
            error_body = response.json()
            assert "error" in error_body, "В ответе отсутствует поле 'error'"
            assert error_body["error"] == "Bad Request", (
                f"Ожидалось 'Bad Request' в поле 'error',"
                f"получено {error_body['error']}")
            assert error_body["message"][0] == "title should not be empty", (
                f"Ожидалось сообщение 'title should not be empty', "
                f"получено {error_body["message"][0]}")
