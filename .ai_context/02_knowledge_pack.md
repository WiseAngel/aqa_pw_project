📌 КОНТЕКСТ
- Python 3.11+, uv/pip, Docker на `playwright/python`.
- CI: GitHub Actions, matrix sharding, allure, tms_reporter.py.
- Фикстуры: session (auth/token), function (context/clean).
- Данные: factory_boy, pydantic models, API rollback.
- Интеграции: TMS через JUnit XML parser, Playwright Trace on fail.

🔒 ПРАВИЛА ВАЛИДАЦИИ
- Все env-переменные в `pydantic.BaseSettings`. Ошибка старта при отсутствии.
- Локаторы только `data-testid` или `role=`. CSS/XPath запрещены, кроме legacy.
- Ожидания: `expect().to_be_visible()`, `wait_for_load_state('networkidle')`.

📊 МЕТРИКИ КАЧЕСТВА
- Flaky < 2%, CI time < 15 мин, покрытие критических путей 100%.
- Zero manual cleanup, 100% typed, ruff/mypy pass 100%.