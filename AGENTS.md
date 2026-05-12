# AGENTS.md — Правила работы AI-ассистентов в Playwright QA Framework

> Этот файл — **единый контракт** для всех AI-инструментов: Cursor, Claude Code, OpenAI Codex, Aider, Continue, Qwen Code.
> Все они автоматически читают `AGENTS.md` при старте сессии.

---

## 🎯 Миссия проекта

Создать production-ready E2E фреймворк для автотестов на базе Playwright + pytest с:
- **Component-based POM** (не Page-based)
- **API pre-conditions** для тестовых данных
- **DB transaction isolation** с auto-rollback
- **Полным CI/CD циклом** на GitHub Actions
- **Интеграцией с TMS** через REST API

---

## 🛠 Технический стек

| Слой | Выбор |
|------|-------|
| Core | Python 3.11+ + pytest + pytest-playwright |
| Config | pydantic-settings + .env (строгая валидация) |
| API Client | httpx (async) |
| Database | SQLAlchemy 2.x + asyncpg |
| Test Data | factory_boy + faker |
| Logging | structlog (JSON в CI) |
| Linting | ruff + mypy --strict + pre-commit |
| Reporting | Allure + Playwright Trace Viewer |
| CI/CD | GitHub Actions (matrix sharding) |

---

## 📋 Правила генерации кода

### Обязательно

1. **Типизация**: Type hints для всех функций и методов
2. **Docstrings**: Google Style с Args, Returns, Raises
3. **expect() вместо assert**: Для UI проверок использовать только `expect()` из Playwright
4. **Без time.sleep()**: Использовать встроенные авто-ожидания Playwright
5. **Без os.getenv()**: Использовать `settings` из `src.config.settings`
6. **Без глобального состояния**: Browser/context/page управляются ТОЛЬКО через фикстуры
7. **Компонентный подход**: UI компоненты наследуются от `BaseComponent`
8. **API для данных**: Тестовые данные создаются через API, не через UI
9. **[ПАМЯТЬ] в .ai/memory/tech/**: Все технические решения сохраняются в формате `[ПАМЯТЬ]` (см. файл-шаблон)

### Запрещено

- ❌ `time.sleep()` — использовать Playwright auto-wait
- ❌ `driver.find_element` — это Selenium антипаттерн
- ❌ Глобальные переменные — только фикстуры
- ❌ Смешивать API/UI логику в компонентах
- ❌ Предлагать `xdist` для CI — только `--shard`
- ❌ Хардкод данных — параметризация или factory_boy
- ❌ Русские имена файлов/переменных в коде
- ❌ Игнорировать `.ai/memory/` — читать перед генерацией кода

### Формат ответа

1. **Вердикт / решение** (1 строкой)
2. **Детализация** (по пунктам)
3. **Код / схема** (в блоках с языком)
4. **Следующие шаги**
5. **Вопросы на уточнение** (если задача неоднозначна)

---

## 🎭 Режимы работы

В начале запроса указывай режим:

| Режим | Когда | Пример |
|-------|-------|--------|
| `[СТРАТЕГ]` | Гипотезы, метрики, выбор инструментов | «Проверь гипотезу: стоит ли добавить ReportPortal?» |
| `[АРХИТЕКТУРА]` | Схема БД, API, диаграммы | «Спроектируй фикстуру DB-транзакций с auto-rollback» |
| `[КОД]` | Генерация, рефакторинг, тесты | «Создай компонент HeaderComponent с локаторами» |
| `[РЕВЬЮ]` | Уязвимости, оптимизация, best practices | «Проверь conftest.py на утечки ресурсов» |
| `[ДИЗАЙН]` | Структура компонентов, паттерны | «Опиши иерархию компонентов для CRM» |
| `[ДОКУМЕНТ]` | README, docstrings, инструкции | «Напиши гайд по миграции с Selenium» |

---

## 📁 Структура проекта

```
playwright-qa/
├── .ai-context/                 # Память для ИИ
├── .github/workflows/e2e.yml    # CI pipeline
├── scripts/tms_reporter.py      # TMS sync script
├── src/
│   ├── api/clients.py           # API client
│   ├── db/engine.py             # DB engine
│   └── config/settings.py       # Settings
├── tests/
│   ├── components/              # UI components
│   ├── e2e/                     # E2E tests
│   ├── fixtures/                # Factories
│   └── conftest.py              # Fixtures
├── Dockerfile
├── pyproject.toml
└── .env.example
```

---

## 🧠 Работа с памятью

Контекст хранится в `/workspace/.ai-context/`:
- `01_system_prompt.md` — системный промпт
- `02_knowledge_pack.md` — базовые знания
- `03_session_starter.md` — старт сессии
- `04_memory_log.md` — лог изменений
- `05_quick_ref.md` — быстрый справочник

**Перед генерацией кода:**
1. Спроси контракт данных (какие данные нужны тесту)
2. Не меняй структуру директорий без подтверждения
3. Используй `expect()` вместо `assert`
4. Добавляй docstrings с Args, Returns, Raises

---

## ⚙️ CI/CD правила

### GitHub Actions

- **Matrix Sharding:** `--shard=${{ matrix.shard }}/${{ matrix.total }}`
- **Free Tier:** 2 vCPU / 7GB RAM — только 2 шарда
- **Fail-fast:** `false` для независимого выполнения
- **Retry:** `--reruns 2 --reruns-delay 3`
- **Кэширование:** pip, ms-playwright, allure-results

### Запрещено в CI

- ❌ `pytest-xdist` (-n auto) — вызывает OOM на free runners
- ❌ Параллелизм внутри одного шарда
- ❌ Хранение секретов в коде — только GitHub Secrets

---

## 🔑 Ключевые файлы

При начале сессии желательно прочитать:

- `AGENTS.md` — этот файл (правила)
- `.cursorrules` — жёсткие правила генерации
- `pyproject.toml` — зависимости и конфиги
- `tests/conftest.py` — фикстуры
- `.ai-context/` — контекст проекта

---

## ❌ Чего AI делать НЕ должен

- Создавать новые файлы, если можно отредактировать существующий
- Менять структуру директорий без подтверждения
- Игнорировать правила из этого файла «потому что так быстрее»
- Молча добавлять зависимости без обоснования
- Предлагать решения, нарушающие принципы фреймворка

---

## 💡 Пример хорошего запроса

```
[КОД] Создай компонент LoginFormComponent с методами:
- fill_email(email: str)
- fill_password(password: str)
- click_submit()
- expect_error_message(text: str)

Стек: Playwright + Component-based POM.
Наследуй от BaseComponent. Используй expect() для проверок.
```

---

> **Главный принцип**: Код должен запускаться без модификаций после `uv pip install .` && `pytest -x`.
