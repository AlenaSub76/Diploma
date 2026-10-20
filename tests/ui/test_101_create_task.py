import uuid
import allure
import pytest

from pages.board_page import BoardPage
from pages.projects_page import ProjectsPage


@allure.feature("UI: Задачи")
@allure.story("Создание задачи")
@pytest.mark.ui
class TestCreateTask:
    """ТК-101. Успешное создание задачи на канбан-доске."""

    @allure.title("ТК-101. Успешное создание задачи на канбан-доске")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_create_task_positive(self, authorized_driver):
        """
        Создаём задачу через UI:
        «Добавить задачу» → ввести имя → клик по пустому месту.
        Проверяем появление карточки. Постусловие — удалить задачу.
        """
        task_name = f"task-{uuid.uuid4().hex[:6]}"
        page = ProjectsPage(authorized_driver).open()

        with allure.step("1. Нажать 'Добавить задачу'"):
            page.click_add_task()

        with allure.step(f"2. Ввести название: {task_name}"):
            page.type_task_name(task_name)

        with allure.step("3. Нажать Enter — создать задачу"):
            page.press_enter_on_task()

        with allure.step("4. Нажать Escape — закрыть поле ввода"):
            page.press_escape_on_task()

        with allure.step("Проверка: карточка появилась"):
            assert page.is_task_visible(task_name), (
                f"Задача '{task_name}' не появилась на доске")

        with allure.step("Постусловие: удалить задачу"):
            BoardPage(authorized_driver).delete_task(task_name)
