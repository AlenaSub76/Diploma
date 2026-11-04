import allure
import pytest


@allure.feature("Projects API")
@allure.story("Удаление проекта")
@pytest.mark.api
class TestDeleteProject:
    """Тесты на удаление проекта."""

    @allure.title("Удаление проекта и проверка, что он недоступен")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_delete_project_positive(self, api_client):
        """
        Полный сценарий soft-delete:
        создать → посчитать до → удалить → проверить флаг deleted →
        проверить отсутствие в списке → посчитать после → сравнить.
        """
        with allure.step("Шаг 1. Создать новый проект"):
            response = api_client.create_project()
            assert response.status_code == 201

        with allure.step("Шаг 2. Извлечь ID"):
            project_id = response.json()["id"]

        with allure.step("Шаг 3. Посчитать проекты ДО удаления"):
            response = api_client.get_all_projects()
            assert response.status_code == 200, (
                f"Не удалось получить список проектов. "
                f"Статус: {response.status_code}. Текст: {response.text}"
            )
            count_before = response.json()["paging"]["count"]

        with allure.step("Шаг 4. Проверить доступность проекта до удаления"):
            response = api_client.get_project(project_id)
            assert response.status_code == 200, (
                f"Проект {project_id} недоступен до удаления. "
                f"Статус: {response.status_code}"
            )

        with allure.step("Шаг 5. Удалить проект (soft delete)"):
            response = api_client.delete_project(project_id)

        with allure.step("Шаг 6. Проверить ответ на удаление"):
            assert response.status_code == 200, (
                f"Не удалось удалить проект {project_id}. "
                f"Статус: {response.status_code}"
            )
            delete_body = response.json()
            assert "id" in delete_body, (
                "В ответе на удаление отсутствует поле 'id'"
            )
            assert delete_body["id"] == project_id, (
                f"ID не совпадает. Отправляли {project_id}, "
                f"получили {delete_body['id']}"
            )

        with allure.step("Шаг 7. Проверить флаг deleted"):
            response = api_client.get_project(project_id)
            assert response.status_code == 200, (
                f"Ожидался 200 (soft delete). Получен {response.status_code}."
            )
            assert response.json().get("deleted") is True, (
                f"Ожидалось 'deleted': True, "
                f"получено {response.json().get('deleted')}"
            )

        with allure.step("Шаг 8. Проверить отсутствие в списке"):
            response = api_client.get_all_projects()
            assert response.status_code == 200
            project_ids = [p["id"] for p in response.json()["content"]]
            assert project_id not in project_ids, (
                f"Удалённый проект {project_id} всё ещё в списке"
            )

        with allure.step("Шаг 9. Посчитать проекты ПОСЛЕ удаления"):
            count_after = response.json()["paging"]["count"]

        with allure.step("Шаг 10. Сравнить: стало ровно на 1 меньше"):
            assert count_before - count_after == 1, (
                f"Количество должно уменьшиться на 1. "
                f"Было: {count_before}, стало: {count_after}"
            )
