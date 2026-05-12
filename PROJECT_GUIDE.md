# 📘 Руководство по Playwright QA Framework

> Этот документ описывает, как устроен фреймворк и как с ним работать — людям и AI-ассистентам.

---

## 🎯 Что это

Production-ready E2E фреймворк для автотестов на базе Playwright + pytest с:
- Component-based POM архитектурой
- API pre-conditions для тестовых данных
- DB transaction isolation с auto-rollback
- Полным CI/CD циклом на GitHub Actions
- Интеграцией с TMS через REST API

---

## 📁 Структура проекта

```
/workspace/                      # 🔝 КОРНЕВАЯ ДИРЕКТОРИЯ ПРОЕКТА
├── .ai/                         # 🧠 Кросс-AI память (читают все ассистенты)
│   └── memory/
│       ├── README.md            # Инструкция по работе с памятью
│       ├── business/            # Бизнес-решения (ниша, цены, экономика)
│       │   └── .gitkeep
│       ├── tech/                # Технические решения (стек, БД, API) + [Память]
│       │   ├── .gitkeep
│       │   └── 2026-05-12_playwright-qa-framework-setup.md  # ⭐ ПАМЯТЬ: Настройка фреймворка
│       ├── design/              # UI/UX-решения, дизайн-токены
│       │   └── .gitkeep
│       └── iterations/          # Лог итераций
│           └── .gitkeep
├── .cursor/                     # Cursor-специфичные настройки
│   └── prompts/                 # Шаблоны промптов для AI
│       ├── README.md
│       └── new-chat-template.md
├── .github/workflows/e2e.yml    # 🔄 CI pipeline
├── scripts/tms_reporter.py      # 📤 JUnit → TMS sync
├── src/                         # 🔌 Core clients
│   ├── api/clients.py           # HTTPX async client
│   ├── db/engine.py             # SQLAlchemy engine
│   └── config/settings.py       # Pydantic settings
├── tests/
│   ├── components/              # 🧩 UI components
│   │   └── base_component.py    # Base class
│   ├── e2e/                     # 🎬 E2E tests
│   ├── fixtures/                # 🔧 Factories
│   │   └── factories.py         # factory_boy
│   └── conftest.py              # 📦 Fixtures
├── artifacts/                   # Рабочая площадка (артефакты разработки)
│   ├── README.md
│   ├── decisions/               # ADR
│   ├── flows/                   # User flows
│   ├── mockups/                 # Wireframes
│   ├── pages/                   # HTML-прототипы
│   └── thinking/                # Размышления, манифесты
├── docs/                        # Концептуальная документация
│   ├── 01-concept.md
│   ├── 03-mvp-spec.md
│   └── 04-ui-modules.md
├── AGENTS.md                    # 🤖 AI rules
├── README.md                    # 📖 Quick start
├── PROJECT_GUIDE.md             # 📘 Полное руководство
├── Dockerfile                   # 🐳 Container
├── pyproject.toml               # 📦 Dependencies
├── .cursorrules                 # Правила для ИИ-генерации
├── .cursorrules.txt             # (дубль для совместимости)
└── .env.example                 # 🔑 Config template
```

---

## 🚀 Быстрый старт

### 1. Установка

```bash
git clone <repo-url> playwright-qa
cd playwright-qa

pip install uv
uv pip install -e ".[dev]"
playwright install chromium

cp .env.example .env
```

### 2. Запуск тестов

```bash
# Все тесты
pytest

# Только smoke
pytest -m smoke

# С отчётом Allure
pytest --alluredir=allure-results
allure serve allure-results
```

### 3. Настройка окружения

Отредактируй `.env`:
```
BASE_URL=https://app.example.com
API_TOKEN=your-token
DB_HOST=localhost
```

---

## 🎭 Режимы работы с AI

В начале запроса указывай режим (см. `AGENTS.md`):

```
[СТРАТЕГ]      — гипотезы, метрики
[АРХИТЕКТУРА]  — БД, API, диаграммы
[КОД]          — генерация, рефакторинг
[РЕВЬЮ]        — безопасность, оптимизация
[ДИЗАЙН]       — компоненты, паттерны
[ДОКУМЕНТ]     — README, инструкции
```

Пример:
```
[КОД] Создай компонент HeaderComponent с локаторами.
Стек: Playwright + Component-based POM.
Наследуй от BaseComponent.
```

---

## 🧪 Паттерны тестирования

### Component-Based POM

```python
from tests.components.base_component import BaseComponent

class LoginFormComponent(BaseComponent):
    def __init__(self, page):
        super().__init__(page, "#login-form")
    
    def fill_email(self, email: str):
        self._child("#email").fill(email)
    
    def submit(self):
        self._child("button[type='submit']").click()

# В тесте
def test_login(page):
    form = LoginFormComponent(page)
    form.fill_email("test@example.com")
    form.submit()
    form.expect_hidden()
```

### API Pre-conditions

```python
from src.api.clients import APIClient
from tests.fixtures.factories import UserFactory

async def test_with_api_data(page):
    user = UserFactory.build()
    
    async with APIClient() as api:
        resp = await api.post("/users", json=user)
        user_id = resp.json()["id"]
    
    page.goto(f"/users/{user_id}")
    # Continue UI test
```

### DB Isolation

```python
async def test_with_db(db_session):
    async with db_session as session:
        # Auto-rollback after test
        result = await session.execute(query)
```

---

## 🔄 CI/CD Pipeline

### GitHub Actions workflow

1. **test job** (matrix shard 1, 2)
   - Cache: pip + Playwright browsers
   - Run: `pytest --shard=X/Y`
   - Retry: `--reruns 2 --reruns-delay 3`
   - Upload: artifacts (screenshots, traces, allure)

2. **report job**
   - Download all shards artifacts
   - Generate Allure HTML report
   - Deploy to GitHub Pages

3. **tms-sync job**
   - Parse JUnit XML
   - Push results to TMS via REST API

### Secrets required

| Secret | Description |
|--------|-------------|
| `BASE_URL` | Application URL |
| `API_TOKEN` | API auth token |
| `DB_HOST` | Database host |
| `DB_USER` | Database user |
| `DB_PASS` | Database password |
| `TMS_API_URL` | TMS API endpoint |
| `TMS_TOKEN` | TMS auth token |

---

## 📊 Отчётность

### Allure Report

Локально:
```bash
allure serve allure-results
```

В CI: деплоится на GitHub Pages

### Playwright Trace Viewer

```bash
playwright show-trace trace.zip
```

Trace автоматически сохраняется при failure (`--tracing=retain-on-failure`)

### TMS Integration

Маркируй тесты TMS ID:
```python
@pytest.mark.tms_id("TC-123")
def test_login():
    ...
```

`tms_reporter.py` распарсит JUnit и отправит статусы в TMS.

---

## ⚙️ Конфигурация

### Environment variables (.env)

| Variable | Default | Description |
|----------|---------|-------------|
| `BASE_URL` | `http://localhost:3000` | App URL |
| `API_BASE_URL` | Derived | API URL |
| `BROWSER` | `chromium` | Browser type |
| `HEADLESS` | `true` | Headless mode |
| `TIMEOUT` | `30000` | Timeout ms |
| `DB_HOST` | `localhost` | DB host |
| `DB_PORT` | `5432` | DB port |
| `DB_NAME` | `qa_test` | DB name |
| `DB_USER` | `qa` | DB user |
| `DB_PASSWORD` | `qa_pass` | DB pass |
| `API_TOKEN` | — | API token |
| `TMS_API_URL` | — | TMS URL |
| `TMS_TOKEN` | — | TMS token |

---

## 🎯 Ключевые принципы

1. **No Global State** — browser/context/page только через фикстуры
2. **No time.sleep()** — Playwright auto-wait
3. **Component-Based** — переиспользуемые компоненты
4. **API First** — данные через API, не UI
5. **Auto-Rollback** — DB транзакции откатываются
6. **No Hardcoding** — factory_boy или параметризация
7. **Strict Typing** — mypy --strict
8. **CI Optimized** — shard-based parallelism

---

## 📈 Метрики

| Metric | Target |
|--------|--------|
| Execution time | <10 min |
| Flaky rate | <2% |
| Coverage | >80% |
| CI success | >95% |

---

## 🔗 Документы

- [README.md](./README.md) — быстрый старт
- [AGENTS.md](./AGENTS.md) — правила для AI
- [pyproject.toml](./pyproject.toml) — зависимости
- [.cursorrules](./.cursorrules) — AI code rules

---

> 💡 **Главный принцип**: Код должен запускаться без модификаций после `uv pip install .` && `pytest -x`.
