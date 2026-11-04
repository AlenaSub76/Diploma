import uuid
import allure
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from api.YouGileAPI import YouGileAPI
from pages.board_page import BoardPage
from pages.login_page import LoginPage
from pages.projects_page import ProjectsPage
from pages.company_page import CompanyPage
from utils.config import config
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import TimeoutException


# =============== API ===================
@pytest.fixture(scope="function")
def api_client():
    """
    HTTP-клиент YouGile API.
    scope='function' — новый клиент на каждый тест (изоляция сессии).
    В teardown закрываем сессию.
    """
    client = YouGileAPI()
    yield client
    client.session.close()


@pytest.fixture(scope="function")
def created_project(api_client: YouGileAPI):
    """
    Создаёт проект через API и гарантированно удаляет его после теста.
    Возвращает project_id и url проекта.
    Зачем: не копипастить «создать → достать id → удалить» в каждом тесте.
    """
    response = api_client.create_project()
    assert response.status_code == 201, (
        f"Проект не создался: {response.status_code}. Текст: {response.text}"
    )
    project_id: str = response.json()["id"]
    # Формируем URL для UI-тестов
    project_url = f"{config.base_url}team/{project_id}"

    yield {"id": project_id, "url": project_url}  # <--- Возвращаем словарь

    response = api_client.delete_project(project_id)
    assert response.status_code == 200, (
        f"Не удалось удалить проект {project_id} в teardown. "
        f"Статус: {response.status_code}. Текст: {response.text}"
    )


# ================== UI =============================
def _build_driver() -> webdriver.Remote:
    """Создаёт драйвер согласно BROWSER и HEADLESS из .env."""
    if config.browser == "firefox":
        options = FirefoxOptions()
        if config.headless:
            options.add_argument("-headless")
        return webdriver.Firefox(options=options)

    options = ChromeOptions()
    if config.headless:
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    return webdriver.Chrome(options=options)


@pytest.fixture(scope="session")
def driver():
    """
    Одна сессия браузера на весь прогон UI-тестов.
    """
    drv = _build_driver()
    drv.implicitly_wait(0)
    yield drv
    drv.quit()


@pytest.fixture(scope="function")
def authorized_driver(driver):
    """
    Драйвер с авторизацией.
    """
    # 1. Переходим на главную
    driver.get(config.base_url)
    # 2. Удаляем все куки
    driver.delete_all_cookies()
    driver.execute_script("window.localStorage.clear();")
    driver.execute_script("window.sessionStorage.clear();")
    # 3. Переходим на страницу логина НАПРЯМУЮ
    driver.get(config.login_url)
    # 4. Логинимся
    LoginPage(driver).login_and_wait(config.user_email, config.user_password)

    yield driver
    # 5. Teardown: очищаем куки
    driver.delete_all_cookies()
    driver.execute_script("window.localStorage.clear();")
    driver.execute_script("window.sessionStorage.clear();")


@pytest.fixture(scope="function")
def created_task(authorized_driver, created_project):
    """
    Создаёт задачу на канбан-доске через UI и удаляет её после теста.
    """
    task_name = f"auto-{uuid.uuid4().hex[:6]}"

    with allure.step(f"Setup: создать задачу '{task_name}'"):
        # Открываем доску НОВОГО проекта
        projects = ProjectsPage(authorized_driver)
        projects.open(url=created_project["url"])

        projects.create_task(task_name)
        assert projects.is_task_visible(task_name), (
            f"Не удалось создать задачу '{task_name}' в setup"
        )

    yield task_name

    with allure.step(f"Teardown: удалить задачу '{task_name}'"):
        # Открываем доску именно того проекта, где создавали задачу
        ProjectsPage(authorized_driver).open(url=created_project["url"])

        # Используем мягкое удаление, которое не падает, если задачи уже нет
        board = BoardPage(authorized_driver)
        try:
            # Ждем видимости карточки
            board.wait.until(ec.visibility_of_element_located(
                (By.XPATH, f"//div[@data-testid='tw-task-container']"
                           f"[.//span[text()='{task_name}']]")
            ))
            # Удаляем
            board.delete_task(task_name)
        except TimeoutException:
            # Если задачи нет (тест упал и не создал её), просто пропускаем
            pass


@pytest.fixture(scope="function")
def created_employee(authorized_driver, created_project, created_task):
    """
    Создаёт нового сотрудника в компании через CompanyPage (UI).
    Возвращает email приглашённого.
    После приглашения возвращает браузер на доску проекта,
    чтобы тест мог работать с карточками задач.
    В teardown — удаляет задаачу и сотрудника.
    """
    invite_email = f"autotest-{uuid.uuid4().hex[:6]}@mail.ru"
    # ---------- SETUP: пригласить сотрудника ----------
    with allure.step(f"Setup: пригласить сотрудника {invite_email}"):
        company = CompanyPage(authorized_driver).open()
        company.scroll_to_employees()
        company.click_add_employee()
        company.fill_invite_form(invite_email)
        company.uncheck_all_projects()
        company.click_invite()
        assert company.is_success_toast_visible(), (
            f"Не появился тост 'успешно приглашен' для {invite_email}")
        assert company.is_employee_in_list(invite_email), (
            f"Сотрудник {invite_email} не появился в списке")

    # ---------- SETUP: вернуться на доску проекта ----------
    with allure.step("Setup: вернуться на доску проекта"):
        # Переходим на доску именно того проекта, где создана задача
        ProjectsPage(authorized_driver).open(url=created_project["url"])

    yield invite_email

    # ---------- TEARDOWN ----------
    # 1. переходим в "Мою компанию" для удаления сотрудника
    with allure.step("Teardown: открыть 'Сотрудники компании'"):
        company = CompanyPage(authorized_driver).open()
        company.scroll_to_employees()

    # 2. удалить сотрудника (три шага)
    with allure.step(f"Teardown: удалить сотрудника {invite_email}"):
        company.delete_employee(invite_email)

    # 3. вернуться в компанию
    with allure.step("Teardown: нажать 'Назад в Мою компанию'"):
        company.click_back_to_company()

    # 4. !!! ВОЗВРАЩАЕМСЯ НА ДОСКУ ПРОЕКТА !!!
    # Чтобы следующая фикстура created_task могла удалить задачу
    ProjectsPage(authorized_driver).open(url=created_project["url"])
