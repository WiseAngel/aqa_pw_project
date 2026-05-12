# [ПАМЯТЬ] Ревью инфраструктуры — Спринт 1 (10.05.2026)

## Контекст

Первичная валидация бэкенд-инфраструктуры перед стартом разработки Auth.
Цель: убедиться, что Docker Compose, Alembic, RLS и модели соответствуют плану спринта.

Проверяемые файлы: `src/backend/Dockerfile`, `src/backend/alembic/`, `src/backend/app/`, `docker-compose.yml`.

---

## Найденные проблемы и исправления

| # | Файл | Проблема | Статус |
|---|------|----------|--------|
| 1 | `Dockerfile` | `alembic/` и `alembic.ini` не копировались в образ | ✅ Исправлено |
| 2 | `alembic/env.py` | Синхронный `engine_from_config` — несовместим с `asyncpg` | ✅ Исправлено |
| 3 | `alembic.ini` | Хардкод `postgresql://postgres:postgres@localhost` | ✅ Исправлено |
| 4 | `docker-compose.yml` | Нет Nginx; порт 5432 открыт наружу; секреты вшиты в файл | ✅ Исправлено |
| 5 | `app/api/v1/deps.py` | `set_tenant_id()` нигде не вызывался — RLS не работал | ✅ Исправлено |
| 6 | `app/models/__init__.py` | `JSON` вместо `JSONB`; нет `updated_at`/`deleted_at` | ✅ Исправлено |

---

## Принятые архитектурные решения

1. **RLS через зависимость, не middleware** — `get_db_with_rls` в `deps.py` применяет `SET LOCAL app.tenant_id` на каждый запрос. Это даёт гибкость для Celery-задач без HTTP-контекста.

2. **Nginx** проксирует только `/api/`, `/health`, `/docs`, `/openapi.json`. Статика фронта — отдельным блоком позже.

3. **`alembic upgrade head` встроен в `command`** backend-сервиса в `docker-compose.yml` — миграции применяются автоматически при старте контейнера.

4. **JSONB везде** вместо JSON — поддержка индексации и GIN-запросов в PostgreSQL 15+.

5. **Секреты только через `.env`** — добавлен `.env.example`; `SECRET_KEY` не имеет дефолтного значения.

6. **Non-root user в Docker** (`appuser`, uid 1000) — требование безопасности для production.

---

## Структура после правок

```
src/backend/
├── Dockerfile              # + alembic/, non-root user, PYTHONUNBUFFERED
├── alembic.ini             # URL → placeholder, читается из settings
├── alembic/
│   ├── env.py              # async: create_async_engine + asyncio.run
│   └── versions/
│       └── 001_initial.py  # JSONB, updated_at, deleted_at, RLS-политики
└── app/
    ├── models/__init__.py  # JSONB, updated_at, deleted_at на всех моделях
    └── api/v1/deps.py      # get_db_with_rls — RLS активируется здесь

src/infrastructure/
└── nginx/nginx.conf        # новый файл

.env.example                # новый файл
docker-compose.yml          # Nginx, internal network, ${VAR} секреты
```

---

## Следующий шаг (Auth + JWT + RLS)

- Таблица `users` (`id`, `tenant_id`, `email`, `password_hash`, `role`, аудит-поля)
- `POST /api/v1/auth/login` — bcrypt + `access_token` (15 мин) + `refresh_token` (30 дней)
- `POST /api/v1/auth/refresh` — ротация refresh токена
- `GET /api/v1/auth/me` — текущий пользователь
- Роли: `owner` / `admin` / `master` — проверка через `Depends`
- Миграция `2026_05_10_add_users.py`
