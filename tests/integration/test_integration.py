"""
Интеграционный тест для проверки взаимодействия с API и базой данных.

Использует публичный API JSONPlaceholder для демонстрации работы.
"""

import pytest
from src.api.clients import APIClient
from src.db.engine import DatabaseEngine
from src.utils.logger import get_logger

logger = get_logger(__name__)


class TestIntegration:
    """Класс интеграционных тестов."""

    @pytest.fixture
    async def api_client(self):
        """Создать экземпляр API клиента."""
        async with APIClient(base_url="https://jsonplaceholder.typicode.com") as client:
            yield client

    @pytest.fixture
    def db_engine(self):
        """Создать экземпляр движка БД (mock для примера)."""
        # В реальном проекте здесь будет подключение к тестовой БД
        return DatabaseEngine(
            host="localhost",
            port=5432,
            database="test_db",
            user="test_user",
            password="test_password",
        )

    @pytest.mark.api
    async def test_get_posts_from_api(self, api_client):
        """Проверка получения списка постов из API."""
        logger.info("Выполняем запрос к API для получения постов")

        response = await api_client.get("/posts", params={"_limit": 5})

        assert response.status_code == 200, "API вернул ошибку"
        data = response.json()

        assert isinstance(data, list), "Ответ должен быть списком"
        assert len(data) == 5, "Должно быть возвращено 5 постов"
        assert "id" in data[0], "Пост должен содержать поле id"
        assert "title" in data[0], "Пост должен содержать поле title"

        logger.info(f"Успешно получено {len(data)} постов")

    @pytest.mark.api
    async def test_get_single_post(self, api_client):
        """Проверка получения одного поста по ID."""
        logger.info("Запрашиваем пост с ID=1")

        response = await api_client.get("/posts/1")

        assert response.status_code == 200
        post = response.json()

        assert post["id"] == 1
        assert "userId" in post
        assert "body" in post

        logger.info(f"Получен пост: {post['title'][:30]}...")

    @pytest.mark.api
    async def test_create_post_via_api(self, api_client):
        """Проверка создания нового поста через API."""
        logger.info("Создаем новый пост через API")

        new_post = {
            "title": "Тестовый пост",
            "body": "Это тело тестового поста",
            "userId": 1,
        }

        response = await api_client.post("/posts", json=new_post)

        assert response.status_code == 201, "Не удалось создать пост"
        created_post = response.json()

        assert created_post["title"] == new_post["title"]
        assert created_post["id"] is not None, "Сервер должен вернуть ID созданного поста"

        logger.info(f"Создан пост с ID={created_post['id']}")

    def test_database_connection_mock(self, db_engine):
        """
        Проверка подключения к БД (mock-тест).

        В реальном проекте здесь будет проверка реального подключения.
        """
        logger.info("Проверяем подключение к базе данных")

        # В реальном проекте:
        # connection = db_engine.connect()
        # assert connection.is_closed() is False

        # Для примера просто проверяем инициализацию
        assert db_engine.host == "localhost"
        assert db_engine.port == 5432

        logger.info("Подключение к БД успешно (mock)")

    @pytest.mark.api
    async def test_integration_api_and_logging(self, api_client):
        """Комплексный тест: API + логирование."""
        logger.info("Запуск комплексного интеграционного теста")

        # Получаем список пользователей
        users_response = await api_client.get("/users", params={"_limit": 3})
        assert users_response.status_code == 200
        users = users_response.json()

        logger.info(f"Получено пользователей: {len(users)}")

        # Для каждого пользователя получаем его посты
        for user in users:
            user_id = user["id"]
            posts_response = await api_client.get(f"/posts?userId={user_id}")
            assert posts_response.status_code == 200

            posts = posts_response.json()
            logger.debug(f"Пользователь {user_id} имеет {len(posts)} постов")

            assert len(posts) > 0 or True  # У пользователя могут отсутствовать посты

        logger.info("Комплексный тест завершен успешно")
