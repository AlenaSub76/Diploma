"""проверка имени (Sky_Pro) и выход из аккаунта."""
from typing import Tuple
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from pages.base_page import BasePage
from utils.config import config


class SettingsPage(BasePage):
    """Страница настроек аккаунта —
    проверка имени пользователя и выход из аккаунта."""

    # Локаторы
    USER_NAME_LABEL: Tuple[str, str] = (
        By.CSS_SELECTOR, "input[placeholder^='Отображаемое имя']"
    )
    BTN_LOGOUT: Tuple[str, str] = (
        By.XPATH, "//div[text()='Выход из аккаунта']"
    )

    # ---------- навигация ----------
    def navigate(self, timeout: int = 15) -> "SettingsPage":
        """Открывает страницу настроек аккаунта и ждёт её загрузки."""
        self.navigate_to(config.settings_url)
        WebDriverWait(self.driver, timeout).until(
            lambda _: config.settings_url in self.driver.current_url
        )
        return self

    # ---------- проверки ----------
    def get_user_name(self) -> str:
        """
        Возвращает отображаемое имя пользователя из модуля 'Профиль'.
        Ожидается значение вида 'Sky_Pro' (см. постусловие ТК-100).
        """
        return self.find(self.USER_NAME_LABEL).get_attribute("value") or ""

    # ---------- действия ----------
    def logout(self) -> "SettingsPage":
        """
        Нажимает 'Выход из аккаунта'.
        Постусловие ТК-100: после этого должен
        произойти переход на страницу логина.
        """
        self.click(self.BTN_LOGOUT)
        return self
