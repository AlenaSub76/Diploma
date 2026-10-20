"""обслуживает ТК-102 - 106 и постусловия удаления."""

from typing import List, Tuple
import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from pages.base_page import BasePage
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as ec


class BoardPage(BasePage):
    """Канбан-доска:
    стикеры, дедлайн, приоритет, исполнитель, удаление задачи."""

    # ========== ЛОКАТОРЫ ======================
    TASK_CARD: Tuple[str, str] = (
        By.CSS_SELECTOR, "div[data-testid='tw-task-container']")
    TASK_CARDS_ALL: Tuple[str, str] = (
        By.CSS_SELECTOR, "div[data-testid='tw-task-container']")
    TASK_CARD_BY_NAME: Tuple[str, str] = (
        By.XPATH,
        "//div[@data-testid='tw-task-container'][.//span[text()='{name}']]"
    )

    # контекстное меню карточки
    TASK_CONTEXT_MENU: Tuple[str, str] = (
        By.XPATH,
        "//div[@data-testid='tw-task-container'][.//span[text()='{name}']]"
        "//div[@data-testid='board-task-menu']")
    MENU_ITEM_DELETE: Tuple[str, str] = (
        By.CSS_SELECTOR, "div[data-testid='menu-item-delete']")
    BTN_CONFIRM_DELETE: Tuple[str, str] = (
        By.XPATH, "//div[@role='button'][.//div[text()='Удалить']]")

    # стикеры
    BTN_STICKER: Tuple[str, str] = (
        By.CSS_SELECTOR, "div[data-testid='task-add-sticker-button']")
    MENU_ITEM_DEADLINE: Tuple[str, str] = (
        By.XPATH, "//div[@data-testid='list-of-task-stickers-item']"
                  "[.//span[text()='Дедлайн']]")
    MENU_ITEM_PRIORITY: Tuple[str, str] = (
        By.XPATH, "//div[@data-testid='list-of-task-stickers-item']"
        "[.//span[text()='Приоритет']]")

    MENU_ITEM_ASSIGNEE: Tuple[str, str] = (
        By.XPATH, "//div[@data-testid='list-of-task-stickers-item']"
        "[.//span[text()='Исполнитель']]")

    # дедлайн
    DEADLINE_SLIDER: Tuple[str, str] = (
        By.CSS_SELECTOR, "div[data-testid^='deadline-with-time-']")
    DEADLINE_DATE: Tuple[str, str] = (
        By.CSS_SELECTOR, "input[data-testid='date-picker-date-input']")
    DEADLINE_TIME: Tuple[str, str] = (
        By.CSS_SELECTOR, "input[data-testid='date-picker-time-input']")
    DEADLINE_BADGE: Tuple[str, str] = (
        By.CSS_SELECTOR, "div[data-testid='dad-sticker']:has("
        "svg[data-icon='IconCustomCalendar'])")

    # фильтр приоритета
    PRIORITY_LABELS: dict[str, str] = {
        "low": "Не важно",
        "normal": "Нормально",
        "major": "Важно",
    }

    # выбор приоритета в выпадающем меню карточки задачи
    FILTER_OPTION: Tuple[str, str] = (
        By.XPATH,
        "//*[normalize-space(text())='{value}']")

    # локатор для кнопки "Приоритет" в ВЕРХНЕЙ ПАНЕЛИ фильтров
    FILTER_PRIORITY_FIELD: Tuple[str, str] = (
        By.XPATH, "//div[normalize-space(text())='Приоритет' "
        "and not(ancestor::div[@data-testid='tw-task-container'])]")

    # Локатор для выбора значения приоритета в меню верхней панели
    FILTER_PRIORITY_OPTION: Tuple[str, str] = (
         By.XPATH, "//div[contains(@class, 'sticker-group')]"
         "[.//div[contains(text(), '{value}')]]")

    # стикер приоритета на карточке — ожидаем атрибут data-priority
    PRIORITY_STICKER_ANY: Tuple[str, str] = (
        By.XPATH, "//div[@data-testid='dad-sticker']"
        "[.//svg[@data-icon='prio']]")

    # кнопка сброса активных фильтров
    BTN_RESET_FILTER: Tuple[str, str] = (
        By.XPATH, "//div[@role='button']"
        "[.//div[contains(text(), 'Сбросить')]]")

    # исполнитель
    BTN_ADD_EMPLOYEE: Tuple[str, str] = (
        By.CSS_SELECTOR, "div[data-testid='add-users-button']")
    ASSIGNEE_CHECKBOX: Tuple[str, str] = (
        By.XPATH, "//span[@title='{name}']/ancestor::div[contains("
        "@class, 'project-participants__item')]"
        "//div[contains(@class, 'item-tick')]")
    ROLE_SELECT_BY_NAME: Tuple[str, str] = (
        By.XPATH, "(//span[@title='{name}']"
                  "/ancestor::div[contains("
                  "@class, 'project-participants__item')]"
                  "//div[contains(@class, 'role__title')])[1]")
    ROLE_OPTION = (By.XPATH, "//div[contains(@class, 'project-role__option')]"
                             "[contains(., '{role}')]")
    BTN_SAVE: Tuple[str, str] = (
        By.XPATH, "//div[@role='button'][.//div[text()='Сохранить']]")
    ASSIGNEE_ITEM: Tuple[str, str] = (
        By.CSS_SELECTOR, "div.user-avatar.sticker-item-icon")
    ASSIGNEE_LIST_ITEM: Tuple[str, str] = (
        By.XPATH, "//div[contains(@class, 'cursor-move')]"
        "[.//span[text()='{name}']]")
    ASSIGNEE_AVATAR_IN_ITEM: Tuple[str, str] = (
        By.CSS_SELECTOR, "div.user-avatar")
    TOP_PANEL_USERS: Tuple[str, str] = (
        By.CSS_SELECTOR, "div[class*='ring-panel-outline-badge']")

    # ============== СТИКЕРЫ =================
    def hover_task_card(self, task_name: str | None = None) -> "BoardPage":
        """
        Наводит курсор на карточку. Если task_name задан — на конкретную,
        иначе на первую на доске.
        """
        if task_name:
            locator = (
                self.TASK_CARD_BY_NAME[0],
                self.TASK_CARD_BY_NAME[1].format(name=task_name),
            )
        else:
            locator = self.TASK_CARD
        ActionChains(self.driver).move_to_element(self.find(locator)).perform()
        return self

    def click_sticker_button(
            self, task_name: str | None = None) -> "BoardPage":
        """Наводит на карточку и нажимает '+Стикер'."""
        self.hover_task_card(task_name)
        if task_name:
            card = self.find((
                self.TASK_CARD_BY_NAME[0],
                self.TASK_CARD_BY_NAME[1].format(name=task_name),
            ))
            card.find_element(
                By.CSS_SELECTOR, "div[data-testid='task-add-sticker-button']"
            ).click()
        else:
            self.click(self.BTN_STICKER)
        return self

    def select_sticker(self, sticker: str) -> "BoardPage":
        """Выбирает тип стикера из выпадающего меню."""
        mapping = {
            "Дедлайн": self.MENU_ITEM_DEADLINE,
            "Приоритет": self.MENU_ITEM_PRIORITY,
            "Исполнитель": self.MENU_ITEM_ASSIGNEE,
        }
        self.click(mapping[sticker])
        return self

    # ============= ДЕДЛАЙН (ТК-102) ============
    def set_deadline(self, date: str, time_value: str) -> "BoardPage":
        """Устанавливает дату и время дедлайна."""
        self.click(self.DEADLINE_SLIDER)
        self.type(self.DEADLINE_DATE, date)

        time_input = self.find(self.DEADLINE_TIME)
        time_input.click()
        time_input.send_keys(Keys.CONTROL, "a")
        time_input.send_keys(Keys.DELETE)

        # вводим цифры по одной
        for digit in time_value.replace(":", ""):
            time_input.send_keys(digit)

        self.click_empty_board_space()  # ← одна строка вместо JS
        return self

    def is_deadline_visible(self, task_name: str) -> bool:
        """Проверяет, что дедлайн отображается на карточке."""
        card = self.find((
            self.TASK_CARD_BY_NAME[0],
            self.TASK_CARD_BY_NAME[1].format(name=task_name),
        ))
        return bool(card.find_elements(*self.DEADLINE_BADGE))

    # ================= ПРИОРИТЕТ (ТК-106) =============
    def set_priority_to_task(self,
                             task_name: str,
                             priority: str) -> "BoardPage":
        """Устанавливает приоритет конкретной задаче через стикер."""
        # 1. Находим карточку и нажимаем +Стикер именно в ней
        self.click_sticker_button(task_name)

        # 2. Выбираем "Приоритет"
        self.select_sticker("Приоритет")

        # 3. Ждем, пока появится выпадающее меню со значениями.
        # Используем локатор, который ищет текст строго внутри
        # выпадающего списка.
        priority_locator = (
            By.XPATH, f"//div[contains(@class, 'sticker-group')]"
                      f"//div[normalize-space(text())='{priority}']")

        # Ждем, пока элемент станет кликабельным
        # (это значит, что меню открылось и прогрузилось)
        element = self.wait.until(ec.element_to_be_clickable(priority_locator))

        # Кликаем через JS
        self.js_click(element)

        self.click_empty_board_space()
        return self

    def filter_by_priority(self, priority: str) -> "BoardPage":
        """Применяет фильтр 'Приоритет' в панели 'Настройки доски'."""
        # 1. Проверяем, открыто ли уже меню фильтра.
        menu_is_open = bool(self.driver.find_elements(
            By.XPATH, "//div[contains(@class, 'sticker-group')]"))

        # 2. Если меню закрыто — открываем его кликом по кнопке фильтра
        if not menu_is_open:
            element = self.find(self.FILTER_PRIORITY_FIELD)
            self.js_click(element)

        # 3. Ждем появления элемента с нужным текстом
        self.wait.until(ec.presence_of_element_located(
            (By.XPATH, f"//*[normalize-space(text())='{priority}']")))

        # 4. Находим ВСЕ элементы с таким текстом (на доске могут быть стикеры)
        elements = self.driver.find_elements(By.XPATH, (
            f"//*[normalize-space(text())='{priority}']"))

        # 5. Кликаем по пункту в открытом меню фильтра
        for el in reversed(elements):
            if el.is_displayed():
                self.js_click(el)
                break
        else:
            raise TimeoutException(
                f"Не найдено видимое значение приоритета '{priority}' "
                f"в фильтре")

        self.click_empty_board_space()
        return self

    def reset_all_filters(self) -> "BoardPage":
        """
        Сбрасывает все активные фильтры на доске.
        Сначала закрывает выпадающее меню (Escape),
        затем кликает 'Сбросить фильтр'.
        """
        # 1. Закрываем открытое меню фильтра (если оно открыто),
        # чтобы оно не перекрывало кнопку сброса
        self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)

        # 2. Ждем появления кнопки сброса и кликаем по ней
        try:
            element = self.wait.until(
                ec.element_to_be_clickable(self.BTN_RESET_FILTER))
            self.js_click(element)
        except TimeoutException:
            # Если фильтров нет (кнопка не появилась), значит сбрасывать нечего
            pass

        return self

    def get_priorities_on_board(self) -> List[str]:
        """
        Возвращает список приоритетов всех видимых карточек.
        Читает русский текст бейджа, преобразует в код: 'Важно' → 'major'.
        """
        cards = self.driver.find_elements(*self.TASK_CARDS_ALL)
        priorities: List[str] = []
        for card in cards:
            stickers = card.find_elements(
                By.CSS_SELECTOR, ".priority-sticker[data-priority]")
            if stickers:
                priorities.append(stickers[0].get_attribute(
                    "data-priority") or "")
        return priorities

    def assert_only_priority_tasks(self, expected_priority: str) -> None:
        """Проверяет, что все видимые задачи имеют заданный приоритет."""
        actual = self.get_priorities_on_board()
        with allure.step(
            f"Проверка: на доске только задачи с "
            f"приоритетом '{expected_priority}'. "
            f"Найдено: {actual}"
        ):
            assert actual, "На доске нет карточек с приоритетом"
            assert all(p == expected_priority for p in actual), (
                f"Ожидались только '{expected_priority}', получено: {actual}"
            )

    # =============== ИСПОЛНИТЕЛЬ (ТК-103, ТК-104) ================
    def click_add_employee(self) -> "BoardPage":
        """Нажимает '+Добавить сотрудников в проект' — открывает форму
        'Участники проекта' (шаг 3 ТК-103)."""
        self.click(self.BTN_ADD_EMPLOYEE)
        return self

    def check_assignee(self, assignee_name: str) -> "BoardPage":
        """Ставит галочку у email сотрудника в форме 'Участники проекта'
        (шаг 4 ТК-103)."""
        self.click((
            self.ASSIGNEE_CHECKBOX[0],
            self.ASSIGNEE_CHECKBOX[1].format(name=assignee_name),
        ))
        return self

    def select_role(self, assignee_name: str, role: str) -> "BoardPage":
        """
        Выбирает роль для указанного сотрудника.
        Открывает выпадающий список роли и кликает по нужной опции.
        """
        # 1. открыть выпадающий список роли для конкретного сотрудника
        self.click((self.ROLE_SELECT_BY_NAME[0],
                    self.ROLE_SELECT_BY_NAME[1].format(name=assignee_name),))
        # 2. кликнуть по нужной роли в открывшемся списке
        self.click((self.ROLE_OPTION[0],
                    self.ROLE_OPTION[1].format(role=role),))
        return self

    def click_save(self) -> "BoardPage":
        """Нажимает 'Сохранить' в форме 'Участники проекта' (шаг 6 ТК-103)."""
        self.click(self.BTN_SAVE)
        return self

    def get_assignee_role_from_sticker(
            self, task_name: str, assignee_name: str) -> str | None:
        """
        Открывает стикер 'Исполнитель', проверяет наличие сотрудника
        в выпадающем списке и возвращает его роль.
        Если сотрудника нет — возвращает None.
        """
        # Открываем стикер 'Исполнитель'
        self.click_sticker_button(task_name)
        self.select_sticker("Исполнитель")

        locator = (
            self.ASSIGNEE_LIST_ITEM[0],
            self.ASSIGNEE_LIST_ITEM[1].format(name=assignee_name))

        # Ждем появления строки сотрудника (с явным ожиданием)
        try:
            item = self.wait.until(ec.presence_of_element_located(locator))
        except TimeoutException:
            self.click_empty_board_space()  # закрываем панель перед выходом
            return None

        # Читаем роль из атрибута аватарки
        avatar = item.find_element(*self.ASSIGNEE_AVATAR_IN_ITEM)
        role = avatar.get_attribute("role") or ""

        self.click_empty_board_space()  # закрываем панель
        return role

    def get_top_panel_users_count(self) -> int:
        """Возвращает количество аватарок в верхней панели."""
        return len(self.driver.find_elements(*self.TOP_PANEL_USERS))

    # ============== УДАЛЕНИЕ ЗАДАЧИ ==================
    def delete_task(self, task_name: str) -> "BoardPage":
        """
        Удаляет задачу через контекстное меню карточки:
        hover → открыть меню → 'Удалить' → подтвердить (если есть).
        """
        with allure.step(f"Постусловие: удалить задачу '{task_name}'"):
            # Принудительно убираем все оверлеи, чтобы они не перекрывали меню
            self.driver.execute_script("""
                           document.querySelectorAll(
                           '.z-2000.fixed').forEach(el => el.remove());
                       """)
            self.hover_task_card(task_name)
            menu_locator = (
                self.TASK_CONTEXT_MENU[0],
                self.TASK_CONTEXT_MENU[1].format(name=task_name))
            self.click(menu_locator)
            # Ждем появления кнопки "Удалить" в DOM
            delete_btn = self.find(self.MENU_ITEM_DELETE)
            # Кликаем через JS, чтобы обойти перекрытия
            self.js_click(delete_btn)

            if self.is_visible(self.BTN_CONFIRM_DELETE):
                self.click(self.BTN_CONFIRM_DELETE)
                # Ждем, пока карточка физически исчезнет из DOM
                task_locator = (
                    self.TASK_CARD_BY_NAME[0],
                    self.TASK_CARD_BY_NAME[1].format(name=task_name)
                )
                try:
                    self.wait.until(
                        ec.invisibility_of_element_located(task_locator))
                except TimeoutException:
                    # Если карточка не исчезла, возможно,
                    # удаление не сработало, но мы не падаем
                    pass
        return self

    def delete_task_if_exists(self, task_name: str) -> "BoardPage":
        """
        Мягкое удаление: проверяет наличие карточки и удаляет, если она есть.
        Используется в teardown, где задача могла быть удалена ранее.
        """
        locator = (
            self.TASK_CARD_BY_NAME[0],
            self.TASK_CARD_BY_NAME[1].format(name=task_name),
        )
        # Мгновенная проверка без ожиданий
        if self.driver.find_elements(*locator):
            self.delete_task(task_name)
        return self

    def is_task_visible(self, task_name: str) -> bool:
        """Проверяет наличие карточки с заданным названием."""
        locator = (
            self.TASK_CARD_BY_NAME[0],
            self.TASK_CARD_BY_NAME[1].format(name=task_name),
        )
        return self.is_visible(locator)

    # =================== ПРОЧЕЕ =======================
    def click_empty_board_space(self) -> "BoardPage":
        """Закрывает открытые панели (overlay) JS-кликом."""
        self.driver.execute_script("""
            document.querySelectorAll(
            'div.z-2000.fixed').forEach(ov => ov.click());
        """)
        return self
