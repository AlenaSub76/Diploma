"""Все страницы наследуются от BasePage и получают единый набор действий."""

from typing import Tuple
# remote нужен только для аннотации
from selenium.webdriver.remote.webdriver import WebDriver
# нужен только для аннотации возвращаемого типа метода find() в BasePage.
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import TimeoutException


class BasePage:
    """Базовый класс всех Page Object'ов: явные ожидания и JS-хелперы."""

    DEFAULT_TIMEOUT: int = 15  # секунд — единый таймаут для всех ожиданий

    def __init__(self, driver: WebDriver) -> None:
        self.driver = driver
        self.wait = WebDriverWait(driver, self.DEFAULT_TIMEOUT)

    # ---------- низкоуровневые функции ----------

    def find(self, locator: Tuple[str, str]) -> WebElement:
        """Ждёт появления элемента в DOM и возвращает его."""
        return self.wait.until(ec.presence_of_element_located(locator))

    def click(self, locator: Tuple[str, str]) -> None:
        """Ждёт кликабельности элемента и кликает."""
        element = self.wait.until(ec.element_to_be_clickable(locator))
        element.click()

    def type(self, locator: Tuple[str, str], text: str) -> None:
        """Ждёт видимости, очищает поле и печатает текст."""
        element = self.wait.until(ec.visibility_of_element_located(locator))
        element.clear()
        element.send_keys(text)

    def is_visible(self,
                   locator: Tuple[str, str],
                   timeout: int | None = None) -> bool:
        """True, если элемент появился за timeout секунд."""
        try:
            WebDriverWait(self.driver, timeout or self.DEFAULT_TIMEOUT).until(
                ec.visibility_of_element_located(locator))
            return True
        except TimeoutException:
            return False

    def get_text(self, locator: Tuple[str, str]) -> str:
        """Возвращает текст элемента."""
        return self.find(locator).text

    # ---------- JavaScript-скролл----------

    def scroll_to(self, locator: Tuple[str, str]) -> None:
        """Прокручивает страницу так, чтобы элемент оказался по центру."""
        element = self.find(locator)
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", element
        )

    def js_click(self, element: WebElement) -> None:
        self.driver.execute_script("arguments[0].click();", element)

    # ---------- URL ----------
    def navigate_to(self, url: str) -> "BasePage":
        """Переходит по URL и возвращает self для
        последовательной цепочки методов."""
        self.driver.get(url)
        return self

    def current_url(self) -> str:
        """Текущий URL браузера."""
        return self.driver.current_url
