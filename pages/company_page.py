"""Обслуживает ТК-105 — от скролла до проверки тоста и
удаления сотрудника в постусловии."""

from typing import Tuple
from selenium.webdriver.common.by import By
from pages.base_page import BasePage
from utils.config import config
import allure


class CompanyPage(BasePage):
    """Раздел 'Сотрудники компании' — ТК-105."""

    # =============== ЛОКАТОРЫ ==================
    # ---------- навигация по странице ----------
    SECTION_EMPLOYEES: Tuple[str, str] = (
        By.XPATH, "//div[text()='Сотрудники компании']"
    )
    # ---------- форма приглашения ----------
    BTN_ADD_EMPLOYEE: Tuple[str, str] = (
        By.XPATH, "//span[text()='Добавить сотрудника']"
    )
    INPUT_EMAIL: Tuple[str, str] = (
        By.CSS_SELECTOR,
        "textarea[placeholder^='Введите адреса электронной почты']")
    BTN_INVITE: Tuple[str, str] = (
        By.CSS_SELECTOR,
        "div[data-testid='company-invite-popup-submit-button']")
    TOAST_SUCCESS: Tuple[str, str] = (
        By.XPATH, "//span[contains(text(), 'успешно приглаш')]"
    )

    # ---------- чекбоксы проектов в модалке приглашения ----------
    PROJECT_CHECKBOXES: Tuple[str, str] = (
        By.CSS_SELECTOR,
        "div[data-testid^='invite-project-'][data-testid$='-checkbox']")

    # ---------- строка сотрудника в списке ----------
    # для проверки видимости email в списке
    EMPLOYEE_NAME: Tuple[str, str] = (By.XPATH, "//span[@title='{email}']")
    # для кликов (раскрывает карточку сотрудника)
    EMPLOYEE_ROW: Tuple[str, str] = (
        By.XPATH,
        "//div[contains(@class, 'group')][.//span[@title='{email}']]")

    # ---------- удаление сотрудника (постусловие ТК-105) ----------
    BTN_REMOVE_EMPLOYEE: Tuple[str, str] = (
        By.CSS_SELECTOR, "div.prj-invite__card-remove-btn"
    )
    BTN_CONFIRM_REMOVE: Tuple[str, str] = (
        By.XPATH, "//div[@role='button'][.//div[text()='Удалить сотрудника']]"
    )
    BTN_BACK_TO_COMPANY: Tuple[str, str] = (
        By.XPATH,
        "//div[@role='button'][.//div[text()='Назад в Мою компанию']]"
    )

    def open(self) -> "CompanyPage":
        """Открывает страницу проектов, где внизу — 'Сотрудники компании'."""
        self.navigate_to(config.projects_url)
        return self

    def scroll_to_employees(self) -> "CompanyPage":
        """JS-скролл до секции 'Сотрудники компании' (шаг 1 ТК-105)."""
        self.scroll_to(self.SECTION_EMPLOYEES)
        return self

    def click_add_employee(self) -> "CompanyPage":
        """Нажимает 'Добавить сотрудника' (шаг 2 ТК-105)."""
        self.click(self.BTN_ADD_EMPLOYEE)
        return self

    def fill_invite_form(self, email: str) -> "CompanyPage":
        """Вводит e-mail приглашаемого (шаг 3 ТК-105)."""
        self.type(self.INPUT_EMAIL, email)
        return self

    def uncheck_all_projects(self) -> "CompanyPage":
        """
        Снимает галочки у всех проектов в модалке приглашения.
        По умолчанию в UI YouGile отмечен последний проект.
        """
        checkboxes = self.driver.find_elements(*self.PROJECT_CHECKBOXES)
        for cb in checkboxes:
            if self._is_checkbox_checked(cb):
                cb.click()
        return self

    def are_all_projects_unchecked(self) -> bool:
        """True, если ни один проект не отмечен (шаг 4 ТК-105)."""
        checkboxes = self.driver.find_elements(*self.PROJECT_CHECKBOXES)
        return not any(self._is_checkbox_checked(cb) for cb in checkboxes)

    def _is_checkbox_checked(self, checkbox) -> bool:
        """
        Проверяет, отмечен ли кастомный чекбокс.
        Признак: внутри квадратика есть <svg> — галочка.
        """
        return bool(checkbox.find_elements(By.TAG_NAME, "svg"))

    def click_invite(self) -> "CompanyPage":
        """Нажимает 'Пригласить сотрудников' (шаг 5 ТК-105)."""
        self.click(self.BTN_INVITE)
        return self

    def is_success_toast_visible(self) -> bool:
        """Проверка зелёного тоста 'Пользователь успешно приглашен'."""
        return self.is_visible(self.TOAST_SUCCESS)

    def is_employee_in_list(self, email: str) -> bool:
        """Проверяет, что приглашённый появился в разделе
        'Сотрудники компании'."""
        locator = (
            self.EMPLOYEE_ROW[0], self.EMPLOYEE_ROW[1].format(email=email))
        return self.is_visible(locator)

    def delete_employee(self, email: str) -> None:
        """
        Постусловие ТК-105: удалить сотрудника из компании.
        Три шага:
        1. Кликнуть по строке — раскрыть карточку сотрудника.
        2. Нажать 'Удалить сотрудника из компании'.
        3. Подтвердить — нажать 'Удалить сотрудника'.
        """
        with allure.step(f"Постусловие: удалить сотрудника {email}"):
            self._click_employee_row(email)
            self._click_remove_button()
            self._click_confirm_remove()

    def _click_employee_row(self, email: str) -> "CompanyPage":
        """Кликает по строке сотрудника, чтобы раскрыть карточку."""
        locator = (
            self.EMPLOYEE_ROW[0],
            self.EMPLOYEE_ROW[1].format(email=email),
        )
        self.click(locator)
        return self

    def _click_remove_button(self) -> "CompanyPage":
        """Нажимает 'Удалить сотрудника из компании' в раскрытой карточке."""
        self.click(self.BTN_REMOVE_EMPLOYEE)
        return self

    def _click_confirm_remove(self) -> "CompanyPage":
        """Подтверждает удаление — кнопка 'Удалить сотрудника' в диалоге."""
        self.click(self.BTN_CONFIRM_REMOVE)
        return self

    def click_back_to_company(self) -> "CompanyPage":
        """Нажимает 'Назад в Мою компанию' после удаления сотрудника."""
        self.click(self.BTN_BACK_TO_COMPANY)
        return self
