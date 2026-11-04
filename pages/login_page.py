"""Покрывает ТК-100. login() вызывается из conftest.py."""

from typing import Tuple
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from pages.base_page import BasePage
from utils.config import config
from selenium.webdriver.support import expected_conditions as ec


class LoginPage(BasePage):
    """Страница логина YouGile."""

    # ========== ЛОКАТОРЫ ====================
    # Кнопка «Войти» на главной странице YouGile
    BTN_LOGIN: Tuple[str, str] = (By.CSS_SELECTOR, "a.sign-in-button")
    # Поле ввода E-mail в форме логина
    INPUT_EMAIL: Tuple[str, str] = (
        By.CSS_SELECTOR, "input[placeholder='example@mail.ru']")
    # Поле ввода Пароль
    INPUT_PASSWORD: Tuple[str, str] = (
        By.CSS_SELECTOR, "input[type='password']")
    # Кнопку «Войти» в самой форме логина
    BTN_SUBMIT: Tuple[str, str] = (
        By.XPATH, "//div[@role='button'][.//div[text()='Войти']]")

    def open_main(self) -> "LoginPage":
        """Открывает главную страницу YouGile."""
        self.navigate_to(config.base_url)
        return self

    def click_login_button(self) -> "LoginPage":
        """Нажимает кнопку 'Войти' на главной."""
        self.click(self.BTN_LOGIN)
        return self

    def fill_credentials(self, email: str, password: str) -> "LoginPage":
        """Заполняет поля E-mail и Пароль."""
        self.type(self.INPUT_EMAIL, email)
        self.type(self.INPUT_PASSWORD, password)
        return self

    def submit(self) -> "LoginPage":
        """Нажимает кнопку 'Войти' в форме."""
        self.click(self.BTN_SUBMIT)
        return self

    def login(self, email: str, password: str) -> "LoginPage":
        """Полный сценарий логина.
        Утилитарный метод для подготовки."""
        return (
            self.open_main()
            .click_login_button()
            .fill_credentials(email, password)
            .submit()
            )

    def wait_for_login(self, timeout: int = 15) -> "LoginPage":
        """Ждёт завершения логина: URL /team/ и форма логина исчезла."""
        WebDriverWait(self.driver, timeout).until(
            lambda _: "/team/" in self.driver.current_url
                      and not self.driver.find_elements(*self.INPUT_EMAIL)
        )
        return self

    def login_and_wait(self, email: str, password: str) -> "LoginPage":
        """Полный логин с ожиданием завершения."""
        # 1. Ждем, пока прогрузится поле E-mail
        self.wait.until(ec.visibility_of_element_located(self.INPUT_EMAIL))
        # 2. Заполняем данные
        self.fill_credentials(email, password)
        # 3. Отправляем форму
        self.submit()
        # 4. Ждем завершения
        self.wait_for_login()
        return self

    def wait_for_login_page_load(self, timeout: int = 15) -> "LoginPage":
        """Ждет, пока на странице появится кнопка 'Войти' или поле E-mail."""
        WebDriverWait(self.driver, timeout).until(
            ec.any_of(
                ec.visibility_of_element_located(self.BTN_LOGIN),
                ec.visibility_of_element_located(self.INPUT_EMAIL)))
        return self
