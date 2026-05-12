# 🎭 Playwright QA Automation Framework

> Production-ready E2E testing framework with Playwright, pytest, API/DB integration, and full CI/CD pipeline.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker & Docker Compose (for CI/CD)
- Node.js (optional, for frontend testing)

### Installation

```bash
# 1. Clone repository and navigate to it
git clone <repo-url> playwright-qa
cd playwright-qa

# 2. Install uv (if not already installed)
pip install uv

# 3. Create virtual environment
uv venv

# 4. Activate virtual environment
# For PowerShell:
.\.venv\Scripts\Activate.ps1
# For CMD:
# .venv\Scripts\activate.bat
# For Bash/Zsh:
# source .venv/bin/activate

# 5. Install dependencies (including dev dependencies)
uv pip install -e ".[dev]"

# 6. Install Playwright browsers
playwright install chromium

# 7. Copy environment configuration
cp .env.example .env
# Or in PowerShell, if cp doesn't work:
# Copy-Item .env.example .env
```

### Run Tests

```bash
# Run all tests
pytest

# Run smoke tests only
pytest -m smoke

# Run with UI (headed mode)
pytest --headless=false

# Run in parallel (local only)
pytest -n auto

# Generate Allure report
pytest --alluredir=allure-results
allure serve allure-results
```

---

## 🏗 Architecture

```
┌─────────────────┐     ┌──────────────┐     ┌─────────────┐
│   Test Files    │────▶│   Pytest     │────▶│  Playwright │
│   (e2e/, api/)  │     │  Fixtures    │     │   Browser   │
└─────────────────┘     └──────────────┘     └─────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
        ┌──────────┐   ┌──────────┐   ┌──────────┐
        │ API      │   │ Database │   │  Test    │
        │ Clients  │   │ Engine   │   │  Data    │
        └──────────┘   └──────────┘   └──────────┘
```

**Stack:**
- **Core:** Python 3.11+, pytest + pytest-playwright
- **Config:** pydantic-settings + .env (strict validation)
- **API Client:** httpx (async)
- **Database:** SQLAlchemy 2.x + asyncpg
- **Test Data:** factory_boy + faker
- **Logging:** structlog (JSON in CI)
- **Reporting:** Allure + Playwright Trace Viewer

---

## 📁 Project Structure

```
/workspace/                      # 🔝 ROOT PROJECT DIRECTORY
├── .ai/                         # 🧠 Cross-AI memory (all assistants read)
│   └── memory/
│       ├── README.md            # Memory usage guide
│       ├── business/            # Business decisions (niche, prices, economics)
│       │   └── .gitkeep
│       ├── tech/                # Technical decisions (stack, DB, API) + [MEMORY]
│       │   ├── .gitkeep
│       │   └── 2026-05-12_playwright-qa-framework-setup.md  # ⭐ MEMORY: Framework setup
│       ├── design/              # UI/UX decisions, design tokens
│       │   └── .gitkeep
│       └── iterations/          # Iteration log
│           └── .gitkeep
├── .cursor/                     # Cursor-specific settings
│   └── prompts/                 # AI prompt templates
│       ├── README.md
│       └── new-chat-template.md
├── .github/workflows/e2e.yml    # 🔄 CI: matrix sharding, cache, retry, allure, tms-sync
├── scripts/tms_reporter.py      # 📤 JUnit → TMS REST API sync
├── src/                         # 🔌 Core clients and configs
│   ├── api/clients.py           # HTTPX async API client
│   ├── db/engine.py             # SQLAlchemy async engine
│   └── config/settings.py       # Pydantic settings
├── tests/
│   ├── components/              # 🧩 Component-based POM
│   │   └── base_component.py    # Base component class
│   ├── e2e/                     # 🎬 Business scenario tests
│   ├── fixtures/                # 🔧 Test data factories
│   │   └── factories.py         # factory_boy factories
│   └── conftest.py              # 📦 Global fixtures, logging
├── artifacts/                   # Workspace (development artifacts)
│   ├── README.md
│   ├── decisions/               # ADR
│   ├── flows/                   # User flows
│   ├── mockups/                 # Wireframes
│   ├── pages/                   # HTML prototypes
│   └── thinking/                # Manifests, research
├── .cursorrules                 # 📏 AI generation rules
├── .cursorrules.txt             # (compatibility duplicate)
├── Dockerfile                   # 🐳 Playwright official image
├── pyproject.toml               # 📦 Dependencies + tool configs
├── AGENTS.md                    # 🤖 AI assistant rules
├── PROJECT_GUIDE.md             # 📘 Full project guide
└── .env.example                 # 🔑 Environment template
```

---

## 🧪 Testing Patterns

### Component-Based POM

```python
from tests.components.base_component import BaseComponent

class HeaderComponent(BaseComponent):
    def __init__(self, page):
        super().__init__(page, "header")
    
    @property
    def logo(self):
        return self._child(".logo")
    
    def click_logo(self):
        self.logo.click()

# Usage in test
def test_navigation(page):
    header = HeaderComponent(page)
    header.expect_visible()
    header.click_logo()
```

### API Pre-conditions

```python
from src.api.clients import APIClient
from tests.fixtures.factories import UserFactory

@pytest.mark.asyncio
async def test_user_flow(page):
    # Create user via API
    user_data = UserFactory.build()
    
    async with APIClient() as api:
        response = await api.post("/users", json=user_data)
        user_id = response.json()["id"]
    
    # Continue with UI test using created user
    page.goto(f"/users/{user_id}")
```

### DB Transaction Isolation

```python
async def test_with_db(db_session):
    async with db_session as session:
        # All changes auto-rollback after test
        result = await session.execute(query)
```

---

## 🔄 CI/CD Pipeline

### GitHub Actions Features
- **Matrix Sharding:** Split tests across 2 runners (free tier optimized)
- **Caching:** pip dependencies + Playwright browsers
- **Retry Logic:** `--reruns 2 --reruns-delay 3` for flaky tests
- **Artifacts:** Screenshots, traces, Allure results
- **TMS Sync:** Auto-push results to external TMS via REST API

### Workflow Jobs
1. **test:** Parallel shards with `fail-fast: false`
2. **report:** Generate Allure HTML report
3. **tms-sync:** Push results to TMS (TestRail/Qase/etc.)

---

## 📊 Reporting

### Allure Report
```bash
# Local
allure serve allure-results

# CI: Deployed to GitHub Pages
```

### Playwright Trace Viewer
```bash
# View traces from failed tests
playwright show-trace trace.zip
```

### TMS Integration
Mark tests with TMS IDs:
```python
@pytest.mark.tms_id("TC-123")
def test_login():
    ...
```

---

## ⚙️ Configuration

### Environment Variables (.env)

| Variable | Description | Default |
|----------|-------------|---------|
| `BASE_URL` | Application URL | `http://localhost:3000` |
| `API_BASE_URL` | API URL (optional) | Derived from BASE_URL |
| `BROWSER` | Browser type | `chromium` |
| `HEADLESS` | Headless mode | `true` |
| `TIMEOUT` | Default timeout (ms) | `30000` |
| `DB_HOST` | Database host | `localhost` |
| `DB_PORT` | Database port | `5432` |
| `DB_NAME` | Database name | `qa_test` |
| `DB_USER` | Database user | `qa` |
| `DB_PASSWORD` | Database password | `qa_pass` |
| `API_TOKEN` | API auth token | — |
| `TMS_API_URL` | TMS API URL | — |
| `TMS_TOKEN` | TMS auth token | — |

---

## 🎯 Key Principles

1. **No Global State:** All browser/context/browser managed via fixtures
2. **No time.sleep():** Use Playwright auto-waits and expect()
3. **Component-Based:** Reusable UI components, not page objects
4. **API First:** Test data via API, not UI
5. **Auto-Rollback:** DB transactions rollback after each test
6. **No Hardcoding:** All data parameterized or generated
7. **Strict Typing:** mypy --strict enforced
8. **CI Optimized:** Shard-based parallelism (no xdist in CI)

---

## 📈 Metrics

| Metric | Target |
|--------|--------|
| Test execution time | <10 min (full suite) |
| Flaky rate | <2% |
| Code coverage | >80% (business logic) |
| CI success rate | >95% |

---

## 🔗 Documentation

- [AGENTS.md](./AGENTS.md) — AI assistant rules
- [PROJECT_GUIDE.md](./PROJECT_GUIDE.md) — Project workflow guide
- [.cursorrules](./.cursorrules) — AI code generation constraints

---

## 📄 License

MIT License
