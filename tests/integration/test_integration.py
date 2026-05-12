"""
Интеграционный тест для проверки взаимодействия с API и базой данных.

Использует публичный API JSONPlaceholder для демонстрации работы.
Все тесты синхронные — используется httpx.Client напрямую.
"""

import httpx
import pytest
from src.utils.logger import get_logger

logger = get_logger(__name__)

API_BASE_URL = "https://jsonplaceholder.typicode.com"


class TestIntegration:
    """Класс интеграционных тестов."""

    @pytest.fixture
    def api_client(self):
        """Создать синхронный HTTP клиент."""
        with httpx.Client(base_url=API_BASE_URL, timeout=10) as client:
            yield client

    @pytest.mark.api
    def test_get_posts_from_api(self, api_client: httpx.Client) -> None:
        """Проверка получения списка постов из API."""
        logger.info("Выполняем запрос к API для получения постов")

        response = api_client.get("/posts", params={"_limit": 5})

        assert response.status_code == 200, "API вернул ошибку"
        data = response.json()

        assert isinstance(data, list), "Ответ должен быть списком"
        assert len(data) == 5, "Должно быть возвращено 5 постов"
        assert "id" in data[0], "Пост должен содержать поле id"
        assert "title" in data[0], "Пост должен содержать поле title"

        logger.info(f"Успешно получено {len(data)} постов")

    @pytest.mark.api
    def test_get_single_post(self, api_client: httpx.Client) -> None:
        """Проверка получения одного поста по ID."""
        logger.info("Запрашиваем пост с ID=1")

        response = api_client.get("/posts/1")

        assert response.status_code == 200
        post = response.json()

        assert post["id"] == 1
        assert "userId" in post
        assert "body" in post

        logger.info(f"Получен пост: {post['title'][:30]}...")

    @pytest.mark.api
    def test_create_post_via_api(self, api_client: httpx.Client) -> None:
        """Проверка создания нового поста через API."""
        logger.info("Создаем новый пост через API")

        new_post = {
            "title": "Тестовый пост",
            "body": "Это тело тестового поста",
            "userId": 1,
        }

        response = api_client.post("/posts", json=new_post)

        assert response.status_code == 201, "Не удалось создать пост"
        created_post = response.json()

        assert created_post["title"] == new_post["title"]
        assert created_post["id"] is not None, "Сервер должен вернуть ID созданного поста"

        logger.info(f"Создан пост с ID={created_post['id']}")

    @pytest.mark.api
    def test_integration_api_and_logging(self, api_client: httpx.Client) -> None:
        """Комплексный тест: API + логирование."""
        logger.info("Запуск комплексного интеграционного теста")

        users_response = api_client.get("/users", params={"_limit": 3})
        assert users_response.status_code == 200
        users = users_response.json()

        logger.info(f"Получено пользователей: {len(users)}")

        for user in users:
            user_id = user["id"]
            posts_response = api_client.get("/posts", params={"userId": user_id})
            assert posts_response.status_code == 200

            posts = posts_response.json()
            logger.debug(f"Пользователь {user_id} имеет {len(posts)} постов")

        logger.info("Комплексный тест завершен успешно")
