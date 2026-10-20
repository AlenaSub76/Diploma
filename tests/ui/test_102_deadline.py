import allure
import pytest

from pages.board_page import BoardPage


@allure.feature("UI: Стикеры")
@allure.story("Дедлайн")
@pytest.mark.ui
class TestDeadline:
    """ТК-102. Установка срока выполнения (дедлайна) для задачи."""

    @allure.title("ТК-102. Установка срока выполнения (дедлайна) для задачи")
    @allure.severity(allure.severity_level.NORMAL)
    def test_set_deadline(self, authorized_driver, created_task: str):
        """
        Задача создаётся фикстурой created_task
        (setup + teardown автоматически).
        Устанавливаем дедлайн 31.10.2026 17:00
        через стикер и проверяем отображение.
        """
        task_name = created_task
        page = BoardPage(authorized_driver)

        with allure.step(f"1. Навести курсор на карточку '{task_name}'"):
            page.hover_task_card(task_name)

        with allure.step("2. Нажать '+Стикер'"):
            page.click_sticker_button(task_name)

        with allure.step("3. Выбрать 'Дедлайн'"):
            page.select_sticker("Дедлайн")

        with allure.step("4-6. Установить дату 31.10.2026 и время 17:00"):
            page.set_deadline("31.10.2026", "17:00")

        with allure.step("7. Проверить отображение дедлайна на карточке"):
            assert page.is_deadline_visible(task_name), (
                f"Дедлайн не отображается на карточке '{task_name}'")
