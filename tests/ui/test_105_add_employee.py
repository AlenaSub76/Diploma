import allure
import pytest

from pages.company_page import CompanyPage
from utils.config import config


@allure.feature("UI: Сотрудники компании")
@allure.story("Добавление сотрудника")
@pytest.mark.ui
class TestAddEmployee:
    """ТК-105. Добавление сотрудника в компанию
    через раздел 'Сотрудники компании'."""

    @allure.title("ТК-105. Добавление сотрудника в компанию")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_add_employee(self, authorized_driver):
        """
        Открываем страницу проектов → скроллим до 'Сотрудники компании' →
        'Добавить сотрудника' → вводим e-mail → снимаем галочки у проектов →
        'Пригласить сотрудников' → проверяем тост и появление в списке.
        Постусловие — удалить сотрудника.
        """
        page = CompanyPage(authorized_driver).open()

        with allure.step("1. Прокрутить страницу до 'Сотрудники компании'"):
            page.scroll_to_employees()

        with allure.step("2. Нажать 'Добавить сотрудника'"):
            page.click_add_employee()

        with allure.step(f"3. Ввести e-mail: {config.invite_email}"):
            page.fill_invite_form(config.invite_email)

        with allure.step("4. Снять галочки у проектов (если есть)"):
            page.uncheck_all_projects()
            assert page.are_all_projects_unchecked(), (
                "Остались отмеченные проекты — ожидалось, "
                "что ни один не выбран")

        with allure.step("5. Нажать 'Пригласить сотрудников'"):
            page.click_invite()

        with allure.step("Проверка: тост об успехе и сотрудник в списке"):
            assert page.is_success_toast_visible(), (
                "Не появился тост 'Пользователь успешно приглашен'"
            )
            assert page.is_employee_in_list(config.invite_email), (
                f"Сотрудник {config.invite_email} не появился в разделе "
                f"'Сотрудники компании'")

        with allure.step("Постусловие: удалить сотрудника"):
            page.delete_employee(config.invite_email)
