import allure
import pytest

from pages.login_page import LoginPage
from pages.settings_page import SettingsPage
from utils.config import config


@allure.feature("UI: Авторизация")
@allure.story("Авторизация пользователя")
@pytest.mark.ui
class TestLogin:
    """ТК-100. Авторизация пользователя в системе YouGile
    с валидными данными."""

    @allure.title("ТК-100. Авторизация с валидными учётными данными")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_login_valid_credentials(self, driver):
        """
        Полный сценарий логина:
        открыть главную страницу → нажать «Войти» → заполнить форму →
        отправить → проверить переход.
        В постусловии — проверить имя пользователя и выйти из аккаунта.
        """
        with allure.step("1. Открыть главную страницу YouGile"):
            page = LoginPage(driver).open_main()

        with allure.step("2. Нажать кнопку 'Войти'"):
            page.click_login_button()
            assert "/team/" in driver.current_url, (
                f"Не открылась страница логина: {driver.current_url}")

        with allure.step("3. Заполнить форму входа"):
            page.fill_credentials(config.user_email, config.user_password)

        with allure.step("4. Нажать кнопку 'Войти'"):
            page.submit()

        with allure.step("4.5. Дождаться авторизации"):
            page.wait_for_login()

        with allure.step("5. Переход на страницу настроек аккаунта"):
            settings = SettingsPage(driver)
            settings.navigate()

        with allure.step(
                f"6. Проверить имя пользователя = {config.user_name}"):
            assert settings.get_user_name() == config.user_name, (
                f"Ожидалось имя '{config.user_name}', "
                f"получено '{settings.get_user_name()}'")

        with allure.step("Постусловие: выход из аккаунта"):
            settings.logout()
            driver.delete_all_cookies()
