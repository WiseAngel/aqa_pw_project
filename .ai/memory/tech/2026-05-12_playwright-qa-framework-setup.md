# [ПАМЯТЬ] Playwright QA Framework — Технический контекст

**Дата создания**: 2026-05-12  
**Категория**: tech  
**Статус**: Активно  

---

## 🎯 Назначение проекта

Production-ready E2E фреймворк для автотестов на базе **Playwright + pytest** с:
- **Component-based POM** архитектурой (не Page-based)
- **API pre-conditions** для тестовых данных
- **DB transaction isolation** с auto-rollback
- **Полным CI/CD циклом** на GitHub Actions (matrix sharding)
- **Интеграцией с TMS** через REST API

---

## 🛠 Технический стек

| Слой | Технология | Обоснование |
|------|------------|-------------|
| **Core** | Python 3.11+ + pytest + pytest-playwright | Стандарт де-факто для Python E2E |
| **Config** | pydantic-settings + .env | Строгая валидация при импорте, защита от ошибок конфигурации |
| **API Client** | httpx (async) | Async/await, типизация, лучше requests для async-кода |
| **Database** | SQLAlchemy 2.x + asyncpg | Async поддержка, type hints, миграции через Alembic |
| **Test Data** | factory_boy + faker | Генерация данных, параметризация, нет хардкоду |
| **Logging** | structlog (JSON в CI) | Структурированное логирование, парсинг в ELK/Grafana |
| **Linting** | ruff + mypy --strict + pre-commit | Быстрый линтер, строгая типизация |
| **Reporting** | Allure + Playwright Trace Viewer | Детальные отчёты, трассировка失败 тестов |
| **CI/CD** | GitHub Actions (matrix sharding) | Free tier 2000 мин/мес, шардирование вместо xdist |

---

## 📁 Архитектура проекта

```
playwright-qa/
├── .ai/                         # 🧠 Кросс-AI память (читают все ассистенты)
│   └── memory/
│       ├── business/            # Бизнес-решения (ниша, цены, экономика)
│       ├── tech/                # Технические решения (стек, БД, API) ← ЭТОТ ФАЙЛ
│       ├── design/              # UI/UX-решения, дизайн-токены
│       └── iterations/          # Лог итераций
├── .github/workflows/e2e.yml    # 🔄 CI: matrix sharding, cache, retry, allure, tms-sync
├── scripts/tms_reporter.py      # 📤 Парсер JUnit → REST TMS
├── src/                         # 🔌 Клиенты API/DB, конфиги
│   ├── api/clients.py           # HTTPX async API client
│   ├── db/engine.py             # SQLAlchemy async engine с auto-rollback
│   └── config/settings.py       # Pydantic settings (валидация при импорте)
├── tests/
│   ├── components/              # 🧩 Component-based POM
│   │   └── base_component.py    # Base class с expect()-обёртками
│   ├── e2e/                     # 🎬 Бизнес-сценарии
│   ├── fixtures/                # 🔧 Генераторы данных
│   │   └── factories.py         # factory_boy factories
│   └── conftest.py              # 📦 Auth, скриншоты, structlog, context isolation
├── AGENTS.md                    # 🤖 Правила для AI-ассистентов
├── README.md                    # 📖 Быстрый старт
├── PROJECT_GUIDE.md             # 📘 Полное руководство
├── .cursorrules                 # 📏 Жёсткие правила генерации для Cursor
├── Dockerfile                   # 🐳 non-root, playwright/python official
├── pyproject.toml               # 📦 deps, pytest/ruff/mypy конфиги
└── .env.example                 # 🔑 Шаблон секретов
```

---

## 🔑 Ключевые архитектурные решения

### 1. Component-based POM (не Page-based)

**Проблема**: Page Object Model создаёт громоздкие классы на 500+ строк, трудно поддерживать.

**Решение**: Компоненты = UI-виджеты с локаторами + `expect()`-обёртки.

```python
# tests/components/base_component.py
class BaseComponent:
    def __init__(self, page, locator):
        self.page = page
        self.locator = page.locator(locator)
    
    def expect_visible(self, timeout=5000):
        expect(self.locator).to_be_visible(timeout=timeout)
    
    def _child(self, selector):
        return self.locator.locator(selector)

# tests/components/login_form.py
class LoginFormComponent(BaseComponent):
    def __init__(self, page):
        super().__init__(page, "#login-form")
    
    def fill_email(self, email: str):
        self._child("#email").fill(email)
    
    def submit(self):
        self._child("button[type='submit']").click()
```

### 2. API Pre-conditions для данных

**Антипаттерн**: Создание данных через UI (медленно, нестабильно).

**Паттерн**: Данные создаются через API перед тестом, очищаются через teardown.

```python
# tests/e2e/test_user_flow.py
from src.api.clients import APIClient
from tests.fixtures.factories import UserFactory

async def test_user_dashboard(page):
    user = UserFactory.build()
    
    async with APIClient() as api:
        resp = await api.post("/users", json=user.dict())
        user_id = resp.json()["id"]
    
    page.goto(f"/dashboard/{user_id}")
    # Continue UI test...
```

### 3. DB Transaction Isolation с Auto-Rollback

**Проблема**: Очистка данных после теста через UI/API — медленно и ненадёжно.

**Решение**: Транзакция с auto-rollback в фикстуре.

```python
# tests/conftest.py
@pytest.fixture(scope="function")
async def db_session():
    async with engine.begin() as conn:
        transaction = await conn.begin()
        session = AsyncSession(bind=conn, expire_on_commit=False)
        yield session
        await transaction.rollback()  # Auto-cleanup
```

### 4. Matrix Sharding в CI (не xdist)

**Ограничение**: GitHub Actions free tier — 2 vCPU / 7GB RAM. `pytest-xdist` вызывает OOM.

**Решение**: Встроенный `--shard` в pytest.

```yaml
# .github/workflows/e2e.yml
strategy:
  matrix:
    shard: [1, 2, 3]
    total: [3]

steps:
  - name: Run tests
    run: pytest --shard=${{ matrix.shard }}/${{ matrix.total }}
```

### 5. TMS Sync через JUnit Parser

**Интеграция**: `scripts/tms_reporter.py` парсит `junit-xml` и пушит статусы в TMS.

**Маппинг**: Через `@pytest.mark.tms_id("ID")`.

```python
# tests/e2e/test_login.py
@pytest.mark.tms_id("TC-123")
def test_valid_login(page):
    ...
```

---

## ⚠️ Ключевые ограничения

| Ограничение | Митигация |
|-------------|-----------|
| GitHub Actions free tier: 2 vCPU/runner, 2000 мин/мес | В CI только `--shard` или `-n 2`, кэширование pip/ms-playwright/allure |
| Flaky тесты >2% | Фиксация на уровне архитектуры/локаторов, не увеличение retry |
| Секреты (`BASE_URL`, `API_TOKEN`, `TMS_*`) | ТОЛЬКО в GitHub Secrets, никогда в коде |
| Пре-коммит проверки | Строгий `pre-commit` блокирует мерж без `ruff`/`mypy --strict` |

---

## 🔄 Workflow разработки

1. **Задача в TMS** → создаётся маркер `@pytest.mark.tms_id("ID")`
2. **Разработка теста** → `[КОД]` режим в AI, генерация через Cursor
3. **Локальный запуск** → `pytest -m smoke && ruff check && mypy --strict`
4. **Коммит** → Conventional Commits (см. ниже)
5. **CI Pipeline** → matrix sharding, allure, tms-sync
6. **Отчёт в TMS** → `tms_reporter.py` пушит статусы

---

## 📝 Формат коммита (Conventional Commits)

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Типы коммитов

| Type | Когда использовать | Пример |
|------|-------------------|--------|
| `feat` | Новая функциональность | `feat(components): add LoginFormComponent` |
| `fix` | Исправление бага | `fix(ci): correct shard matrix in workflow` |
| `docs` | Документация | `docs(README): update quick start section` |
| `style` | Форматирование, semicolons, etc. | `style(tests): format imports with ruff` |
| `refactor` | Рефакторинг без изменений поведения | `refactor(api): extract retry logic to decorator` |
| `test` | Добавление/изменение тестов | `test(e2e): add smoke tests for auth flow` |
| `chore` | Инфраструктура, зависимости | `chore(deps): bump playwright to 1.40.0` |
| `ci` | Изменения в CI/CD | `ci(workflows): add tms-sync step` |
| `perf` | Улучшение производительности | `perf(db): add index on users.email` |
| `build` | Сборка, docker | `build(docker): switch to non-root user` |

### Scope (область изменений)

- `components` — UI компоненты
- `e2e` — E2E тесты
- `fixtures` — Фикстуры и фабрики
- `api` — API клиенты
- `db` — База данных, миграции
- `config` — Конфигурация, settings
- `ci` — GitHub Actions, workflows
- `docs` — Документация
- `infra` — Docker, инфраструктура

### Subject (тема)

- Начинается с глагола в повелительном наклонении (add, fix, update, remove)
- Без точки в конце
- Максимум 50 символов

### Body (тело)

- Опционально
- Объясняет **почему**, а не **что** (что видно из diff)
- Wrap на 72 символах

### Footer (подвал)

- Опционально
- `BREAKING CHANGE:` — если есть breaking changes
- `Closes #123` — закрытие issues
- `Refs: TC-456` — ссылка на тест-кейс в TMS

### Примеры

```bash
# Новая фича
feat(components): add HeaderComponent with navigation locators

Implements header component for Component-based POM architecture.
Includes locators for logo, menu, user profile dropdown.

Closes #42
Refs: TC-101, TC-102

# Исправление бага
fix(ci): correct shard matrix calculation in e2e workflow

The previous formula caused duplicate test execution on shard 2.
Now uses GitHub Actions matrix strategy correctly.

Fixes #57

# Обновление документации
docs(README): add troubleshooting section for common errors

Adds solutions for:
- Playwright browser installation failures
- Missing environment variables
- Database connection timeouts

# Рефакторинг
refactor(api): extract retry logic to async decorator

Reduces code duplication across API client methods.
No behavioral changes.

# Зависимости
chore(deps): bump pytest-playwright from 0.4.3 to 0.5.0

Release notes: https://github.com/microsoft/playwright-pytest/releases/tag/v0.5.0
```

---

## 🤖 Использование с AI-ассистентами

### Режимы запроса (в начале сообщения)

| Режим | Когда | Пример |
|-------|-------|--------|
| `[СТРАТЕГ]` | Гипотезы, метрики, выбор инструментов | «Проверь гипотезу: стоит ли добавить ReportPortal?» |
| `[АРХИТЕКТУРА]` | Схема БД, API, диаграммы | «Спроектируй фикстуру DB-транзакций с auto-rollback» |
| `[КОД]` | Генерация, рефакторинг, тесты | «Создай компонент HeaderComponent с локаторами» |
| `[РЕВЬЮ]` | Уязвимости, оптимизация, best practices | «Проверь conftest.py на утечки ресурсов» |
| `[ДИЗАЙН]` | Структура компонентов, паттерны | «Опиши иерархию компонентов для CRM» |
| `[ДОКУМЕНТ]` | README, docstrings, инструкции | «Напиши гайд по миграции с Selenium» |

### Обязательные правила для AI

1. **Спрашивать контракт данных** перед генерацией кода
2. **Не менять структуру директорий** без подтверждения
3. **Использовать `expect()`** вместо `assert` для UI проверок
4. **Добавлять docstrings** с Args, Returns, Raises
5. **Код должен запускаться** без модификаций после `uv pip install .` && `pytest -x`

---

## 📚 Связанные файлы

- `.ai/memory/business/` — Бизнес-контекст (ниша, метрики)
- `.ai/memory/design/` — UI/UX паттерны компонентов
- `.ai/memory/iterations/` — Лог изменений архитектуры
- `AGENTS.md` — Правила для AI-ассистентов
- `.cursorrules` — Специфичные правила для Cursor IDE
- `PROJECT_GUIDE.md` — Полное руководство по проекту

---

## 📅 История изменений

- **2026-05-12**: Создан файл памяти для Playwright QA Framework
- **2026-05-12**: Утверждена Component-based POM архитектура
- **2026-05-12**: Выбран matrix sharding вместо xdist для CI
