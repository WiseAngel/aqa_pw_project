"""
Компонентные тесты для UI элементов.

Проверяют изолированные компоненты интерфейса: кнопки, формы, навигацию.
"""

from playwright.sync_api import Page, expect


class TestButtonComponent:
    """Тесты для компонента кнопки."""

    def test_button_exists(self, page: Page):
        """Проверка существования кнопки на странице."""
        page.goto("https://demo.playwright.dev/todomvc")

        # Ищем кнопку добавления задачи
        button = page.locator('button[aria-label="Add"]')
        expect(button).to_be_visible()

    def test_button_clickable(self, page: Page):
        """Проверка кликабельности кнопки."""
        page.goto("https://demo.playwright.dev/todomvc")

        button = page.locator('button[aria-label="Add"]')
        button.click()

        # После клика фокус должен остаться на поле ввода
        input_field = page.locator(".new-todo")
        expect(input_field).to_be_focused()


class TestFormComponent:
    """Тесты для компонента формы ввода."""

    def test_input_field_exists(self, page: Page):
        """Проверка существования поля ввода."""
        page.goto("https://demo.playwright.dev/todomvc")

        input_field = page.locator(".new-todo")
        expect(input_field).to_be_visible()

    def test_input_typing(self, page: Page):
        """Проверка ввода текста в поле."""
        page.goto("https://demo.playwright.dev/todomvc")

        input_field = page.locator(".new-todo")
        test_text = "Тестовая задача"

        input_field.fill(test_text)
        expect(input_field).to_have_value(test_text)

    def test_form_submission(self, page: Page):
        """Проверка отправки формы."""
        page.goto("https://demo.playwright.dev/todomvc")

        input_field = page.locator(".new-todo")
        test_text = "Задача для проверки отправки"

        input_field.fill(test_text)
        input_field.press("Enter")

        # Проверяем, что задача появилась в списке
        todo_item = page.locator(".todo-list li").filter(has_text=test_text)
        expect(todo_item).to_be_visible()


class TestNavigationComponent:
    """Тесты для компонента навигации."""

    def test_navigation_links_exist(self, page: Page):
        """Проверка существования ссылок навигации."""
        page.goto("https://demo.playwright.dev/todomvc")

        # Создадим задачу, чтобы появились фильтры
        input_field = page.locator(".new-todo")
        input_field.fill("Тестовая задача")
        input_field.press("Enter")

        # Проверяем наличие фильтров
        all_filter = page.locator('a[href="#/"]').filter(has_text="All")
        active_filter = page.locator('a[href="#/active"]').filter(has_text="Active")
        completed_filter = page.locator('a[href="#/completed"]').filter(has_text="Completed")

        expect(all_filter).to_be_visible()
        expect(active_filter).to_be_visible()
        expect(completed_filter).to_be_visible()

    def test_navigation_filtering(self, page: Page):
        """Проверка фильтрации через навигацию."""
        page.goto("https://demo.playwright.dev/todomvc")

        # Создаем две задачи
        input_field = page.locator(".new-todo")
        input_field.fill("Активная задача")
        input_field.press("Enter")

        input_field.fill("Еще одна задача")
        input_field.press("Enter")

        # Отмечаем одну как выполненную
        page.locator(".todo-list li").nth(0).locator(".toggle").click()

        # Переходим к активным
        page.locator('a[href="#/active"]').click()

        # Должна остаться только одна активная задача
        active_items = page.locator(".todo-list li.visible")
        expect(active_items).to_have_count(1)


class TestCheckboxComponent:
    """Тесты для компонента чекбокса."""

    def test_checkbox_toggle(self, page: Page):
        """Проверка переключения чекбокса."""
        page.goto("https://demo.playwright.dev/todomvc")

        # Создаем задачу
        input_field = page.locator(".new-todo")
        input_field.fill("Задача для чекбокса")
        input_field.press("Enter")

        checkbox = page.locator(".todo-list li .toggle")

        # Проверяем начальное состояние
        expect(checkbox).not_to_be_checked()

        # Кликаем и проверяем изменение состояния
        checkbox.click()
        expect(checkbox).to_be_checked()
