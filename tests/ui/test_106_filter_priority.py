import allure
import pytest
import uuid
from pages.board_page import BoardPage
from pages.projects_page import ProjectsPage


@allure.feature("UI: Фильтрация")
@allure.story("Фильтр задач по приоритету")
@pytest.mark.ui
class TestFilterPriority:
    """ТК-106. Фильтрация списка задач по приоритету"""
    @allure.title("ТК-106: Фильтрация списка задач по приоритету '{priority}'")
    @allure.severity(allure.severity_level.NORMAL)
    def test_filter_by_priority(self, authorized_driver, created_task):
        board = BoardPage(authorized_driver)
        projects = ProjectsPage(authorized_driver)
        with allure.step("Предусловие: развернуть страницу во все окно"):
            authorized_driver.maximize_window()

        with allure.step("Шаг 1. Создать три задачи на доске"):
            # Получаем имя первой задачи из фикстуры
            task1_name = created_task

            # Генерируем названия еще двух задач
            task2_name = f"auto-{uuid.uuid4().hex[:6]}"
            task3_name = f"auto-{uuid.uuid4().hex[:6]}"

            # Возвращаемся на доску,
            # так как фикстура created_task оставляет нас там
            projects.open()

            # Создаем вторую задачу
            projects.create_task(task2_name)
            assert projects.is_task_visible(task2_name), (
                f"Задача {task2_name} не создана")

            # Создаем третью задачу
            projects.create_task(task3_name)
            assert projects.is_task_visible(task3_name), (
                f"Задача {task3_name} не создана")

            # Проверяем, что все три задачи на месте
            assert board.is_task_visible(task1_name), (
                f"Задача {task1_name} не найдена")
            assert board.is_task_visible(task2_name), (
                f"Задача {task2_name} не найдена")
            assert board.is_task_visible(task3_name), (
                f"Задача {task3_name} не найдена")

        with allure.step("Шаг 2: Первой задаче установить приоритет 'Важно'"):
            # В коде board_page.py приоритет "major"
            # соответствует русскому "Важно"
            board.set_priority_to_task(task1_name, "Важно")

        with allure.step(
                "Шаг 3: Второй задаче установить приоритет 'Нормально'"):
            board.set_priority_to_task(task2_name, "Нормально")

        with allure.step(
                "Шаг 4: Третьей задаче установить приоритет 'Не важно'"):
            board.set_priority_to_task(task3_name, "Не важно")

        with allure.step(
                "Шаг 5: В панели 'Настройки доски' "
                "кликнуть по полю 'Приоритет'"):
            # Метод filter_by_priority сам открывает меню и кликает по опции
            pass

        with allure.step("Шаг 6: Выбрать приоритет 'Важно'"):
            board.filter_by_priority("Важно")
            # Проверяем, что осталась только задача с приоритетом "Важно"
            assert board.is_task_visible(task1_name), (
                "Задача 'Важно' должна быть видна")
            assert not board.is_task_visible(task2_name), (
                "Задача 'Нормально' не должна быть видна")
            assert not board.is_task_visible(task3_name), (
                "Задача 'Не важно' не должна быть видна")

        with allure.step("Шаг 7: Снять галочку с приоритета 'Важно'"):
            # Для снятия фильтра используем метод фильтрации
            # еще раз (он переключает чекбокс)
            board.reset_all_filters()
            # Проверяем, что все задачи снова видны
            assert board.is_task_visible(task1_name), (
                "Все задачи должны быть видны")
            assert board.is_task_visible(task2_name), (
                "Все задачи должны быть видны")
            assert board.is_task_visible(task3_name), (
                "Все задачи должны быть видны")

        with allure.step("Шаг 8 (повтор): Выбрать приоритет 'Не важно'"):
            board.filter_by_priority("Не важно")

            # Проверяем, что осталась только задача с приоритетом "Не важно"
            assert not board.is_task_visible(task1_name), (
                "Задача 'Важно' не должна быть видна")
            assert not board.is_task_visible(task2_name), (
                "Задача 'Нормально' не должна быть видна")
            assert board.is_task_visible(task3_name), (
                "Задача 'Не важно' должна быть видна")

        with allure.step("Шаг 9: Снять галочку с приоритета 'Не важно'"):
            board.reset_all_filters()
            # Проверяем, что все задачи снова видны
            assert board.is_task_visible(task1_name), (
                "Все задачи должны быть видны")
            assert board.is_task_visible(task2_name), (
                "Все задачи должны быть видны")
            assert board.is_task_visible(task3_name), (
                "Все задачи должны быть видны")

        with allure.step("Шаг 10: Выбрать приоритет 'Нормально'"):
            board.filter_by_priority("Нормально")
            # Проверяем, что осталась только задача с приоритетом "Нормально"
            assert not board.is_task_visible(task1_name), (
                "Задача 'Важно' не должна быть видна")
            assert board.is_task_visible(task2_name), (
                "Задача 'Нормально' должна быть видна")
            assert not board.is_task_visible(task3_name), (
                "Задача 'Не важно' не должна быть видна")

        with allure.step("Шаг 11: Снять галочку с приоритета 'Нормально'"):
            board.reset_all_filters()
            # Проверяем, что все задачи снова видны
            assert board.is_task_visible(task1_name), (
                "Все задачи должны быть видны")
            assert board.is_task_visible(task2_name), (
                "Все задачи должны быть видны")
            assert board.is_task_visible(task3_name), (
                "Все задачи должны быть видны")

        # --- Постусловие: удаление задач ---
        with allure.step("Постусловие: дождаться отображения "
                         "всех задач после сброса фильтров"):
            # Ждем, пока все три задачи вернутся на доску
            assert board.is_task_visible(task1_name), (
                f"Задача {task1_name} не вернулась на доску")
            assert board.is_task_visible(task2_name), (
                f"Задача {task2_name} не вернулась на доску")
            assert board.is_task_visible(task3_name), (
                f"Задача {task3_name} не вернулась на доску")
        with allure.step("Постусловие: удалить созданные задачи"):
            board.delete_task_if_exists(task1_name)
            board.delete_task_if_exists(task2_name)
            board.delete_task_if_exists(task3_name)
