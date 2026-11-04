import allure
import pytest

from pages.board_page import BoardPage
from pages.projects_page import ProjectsPage


@allure.feature("UI: Исполнители")
@allure.story("Добавление через стикер")
@pytest.mark.ui
class TestAssigneeSticker:
    """ТК-103. Добавление исполнителя в проект
    через стикер "Исполнитель" на карточке задачи"""

    @allure.title("ТК-103. Добавление исполнителя в проект "
                  "через стикер 'Исполнитель' на карточке задачи")
    @allure.severity(allure.severity_level.NORMAL)
    def test_assignee_via_sticker(
            self,
            authorized_driver,
            created_project,
            created_task: str,
            created_employee: str):
        """
        Задача создаётся фикстурой created_task.
        Сотрудник создаётся фикстурой created_employee.
        Наводим курсор → стикер 'Исполнитель' →
        добавляем сотрудника с ролью 'Сотрудник'.
        Проверяем, что сотрудник отобразился.
        """
        task_name = created_task
        assignee_name = created_employee  # email из фикстуры
        page = BoardPage(authorized_driver)
        role = "Сотрудник"

        # Переходим на доску НОВОГО проекта
        projects_page = ProjectsPage(authorized_driver)
        projects_page.open(url=created_project["url"])

        with allure.step(f"Шаг 1. Навести курсор на карточку '{task_name}'"):
            page.hover_task_card(task_name)

        with allure.step(
                "Шаг 1.1. Запомнить количество иконок в верхней панели (до)"):
            count_before = page.get_top_panel_users_count()

        with allure.step("Шаг 2. Кликнуть по иконке 'Исполнитель'"):
            page.click_sticker_button(task_name)
            page.select_sticker("Исполнитель")

        with allure.step("Шаг 3. Нажать '+Добавить сотрудников в проект'"):
            page.click_add_employee()

        with allure.step(
                f"Шаг 4. Поставить галочку у email '{assignee_name}'"):
            page.check_assignee(assignee_name)

        with allure.step(
                f"Шаг 5. Выбрать роль '{role}' в поле 'Роль в проекте'"):
            page.select_role(assignee_name, role)

        with allure.step("Шаг 6. Нажать 'Сохранить'"):
            page.click_save()
            # закрыть стикер
            page.click_empty_board_space()

        with allure.step(f"Шаг 7. Проверить, что сотрудник '{assignee_name}' "
                         f"есть в списке стикера, и его роль = '{role}'"):
            actual_role = page.get_assignee_role_from_sticker(
                task_name, assignee_name)

            assert actual_role is not None, (
                f"Сотрудник '{assignee_name}' "
                f"не найден в выпадающем списке стикера")
            assert actual_role == role, (
                f"Ожидалась роль '{role}', получено '{actual_role}'")

        with allure.step(
                "8. Проверить, что иконка сотрудника "
                "добавилась в верхнюю панель"):
            # Ждем, пока иконок станет на 1 больше (до 10 секунд)
            page.wait_avatars(count_before + 1)
            # После ожидания просто проверяем фактическое количество
            count_after = page.get_top_panel_users_count()
            assert count_after == count_before + 1, (
                f"Ожидалось {count_before + 1} иконок в верхней панели, "
                f"стало {count_after} (было {count_before})")
