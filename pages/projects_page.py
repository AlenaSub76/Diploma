"""покрывает ТК-101 (создание задачи) и обслуживает фикстуру created_task."""

from typing import Tuple
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from pages.base_page import BasePage
from utils.config import config


class ProjectsPage(BasePage):
    """Страница 'Моя компания / Проекты' — здесь создаём задачи."""

    # Локаторы
    BTN_ADD_TASK: Tuple[str, str] = (
        By.XPATH,
        "//div[@data-testid='link-button-new']"
        "[.//span[text()='Добавить задачу']]")
    INPUT_NEW_TASK: Tuple[str, str] = (
        By.CSS_SELECTOR, "textarea[data-testid='board-task-input-name']"
    )
    COLUMN_TITLE: Tuple[str, str] = (
        By.XPATH, "//span[text()='Новая колонка']")

    TASK_CARD_BY_NAME: Tuple[str, str] = (
        By.XPATH,
        "//div[@data-testid='tw-task-container']"
        "[.//*[@data-testid='board-task-title'][.//span[text()='{name}']]]"
    )

    def open(self) -> "ProjectsPage":
        """Открывает страницу проектов (канбан-доску)."""
        self.navigate_to(config.project_url)
        return self

    def click_add_task(self) -> "ProjectsPage":
        """Нажимает 'Добавить задачу' (шаг 1 ТК-101)."""
        self.click(self.BTN_ADD_TASK)
        return self

    def type_task_name(self, name: str) -> "ProjectsPage":
        """Вводит название в поле новой задачи (шаг 2 ТК-101)."""
        self.type(self.INPUT_NEW_TASK, name)
        return self

    def press_enter_on_task(self) -> "ProjectsPage":
        """Нажимает Enter в поле — создаёт карточку задачи."""
        self.find(self.INPUT_NEW_TASK).send_keys(Keys.ENTER)
        return self

    def press_escape_on_task(self) -> "ProjectsPage":
        """Нажимает Escape — закрывает поле ввода после создания задачи."""
        self.find(self.INPUT_NEW_TASK).send_keys(Keys.ESCAPE)
        return self

    def create_task(self, name: str) -> "ProjectsPage":
        """Полный сценарий создания задачи —
        используется в фикстуре created_task."""
        return (
            self.click_add_task()
            .type_task_name(name)
            .press_enter_on_task()  # ← Enter создаёт задачу
            .press_escape_on_task()  # ← Escape закрывает поле
        )

    def is_task_visible(self, name: str) -> bool:
        """Проверяет, что карточка с заданным названием видна на доске."""
        locator = (
            self.TASK_CARD_BY_NAME[0],
            self.TASK_CARD_BY_NAME[1].format(name=name),
        )
        return self.is_visible(locator)
