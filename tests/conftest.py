"""
Pytest configuration and fixtures for Playwright E2E tests.

Provides:
- Browser context isolation per test
- Automatic authentication via API
- Structlog logging setup
- Screenshot/trace on failure
- DB transaction rollback for test isolation
"""

import asyncio
import logging
from collections.abc import AsyncGenerator, Generator
from typing import Any

import pytest
import structlog
from playwright.sync_api import BrowserContext, Page, expect
from src.config.settings import settings
from src.db.engine import DatabaseEngine


def pytest_addoption(parser: pytest.Parser) -> None:
    """Add custom command-line options."""
    parser.addoption(
        "--headless",
        action="store_true",
        default=None,
        help="Run browsers in headless mode",
    )


@pytest.fixture(scope="session")
def browser_type_launch_args(request: pytest.FixtureRequest) -> dict:
    """Override browser launch args to support --headless flag."""
    headless = request.config.getoption("--headless")
    # Use CLI arg if provided, otherwise fall back to settings
    if headless is not None:
        return {"headless": headless}
    return {"headless": settings.headless}

# Configure structlog for JSON logging in CI
structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create session-scoped event loop for async fixtures."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def db_engine() -> AsyncGenerator[DatabaseEngine, None]:
    """
    Session-scoped database engine fixture.

    Provides connected DB engine for all tests in session.
    Automatically disconnects after session ends.
    """
    db = DatabaseEngine()
    await db.connect()
    yield db
    await db.disconnect()


@pytest.fixture
async def db_session(db_engine: DatabaseEngine) -> AsyncGenerator:
    """
    Function-scoped DB session with auto-rollback.

    Each test gets a fresh transaction that is rolled back after test.
    Ensures complete test isolation without manual cleanup.

    Usage:
        async def test_something(db_session):
            async with db_session as session:
                # DB operations here
    """
    async with db_engine.session() as session:
        try:
            yield session
            await session.rollback()  # Auto-rollback after test
        except Exception:
            await session.rollback()
            raise


@pytest.fixture
def context(context: BrowserContext) -> BrowserContext:
    """
    Override default browser context with custom settings.

    Adds:
    - Base URL from settings
    - Timeout from settings
    - Extra HTTP headers (auth token)
    """
    context.set_default_timeout(settings.timeout)

    if settings.api_token:
        context.set_extra_http_headers({"Authorization": f"Bearer {settings.api_token}"})

    return context


@pytest.fixture
def page(page: Page, request: pytest.FixtureRequest) -> Page:
    """
    Override default page with enhanced failure handling.

    Captures:
    - Screenshot on failure
    - Console logs on failure

    Note: Tests must explicitly navigate to pages with page.goto(url)
    """
    yield page

    # If test failed, capture diagnostic info
    if hasattr(request.node, "rep_call") and request.node.rep_call.failed:
        screenshot_name = f"screenshots/{request.node.name}.png"
        page.screenshot(path=screenshot_name)
        logger.error("Test failed", screenshot=screenshot_name)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo) -> Any:
    """Capture test outcome for use in fixtures."""
    outcome = yield
    report = outcome.get_result()

    if report.when == "call":
        item.rep_call = report
    elif report.when == "setup":
        item.rep_setup = report
    elif report.when == "teardown":
        item.rep_teardown = report


# Helper matchers for common UI patterns
class ComponentExpectations:
    """Reusable expect() wrappers for UI components."""

    @staticmethod
    def element_visible(page: Page, selector: str, timeout: float | None = None) -> None:
        """Assert element is visible."""
        expect(page.locator(selector)).to_be_visible(timeout=timeout)

    @staticmethod
    def element_hidden(page: Page, selector: str, timeout: float | None = None) -> None:
        """Assert element is hidden."""
        expect(page.locator(selector)).to_be_hidden(timeout=timeout)

    @staticmethod
    def has_text(page: Page, selector: str, text: str, timeout: float | None = None) -> None:
        """Assert element has expected text."""
        expect(page.locator(selector)).to_have_text(text, timeout=timeout)

    @staticmethod
    def contains_text(page: Page, selector: str, text: str, timeout: float | None = None) -> None:
        """Assert element contains expected text."""
        expect(page.locator(selector)).to_contain_text(text, timeout=timeout)

    @staticmethod
    def enabled(page: Page, selector: str, timeout: float | None = None) -> None:
        """Assert element is enabled."""
        expect(page.locator(selector)).to_be_enabled(timeout=timeout)

    @staticmethod
    def disabled(page: Page, selector: str, timeout: float | None = None) -> None:
        """Assert element is disabled."""
        expect(page.locator(selector)).to_be_disabled(timeout=timeout)


@pytest.fixture
def ui() -> type[ComponentExpectations]:
    """Provide reusable UI expectation helpers."""
    return ComponentExpectations
