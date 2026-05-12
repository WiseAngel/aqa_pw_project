import pytest
from playwright.sync_api import Page, BrowserContext
from src.config.settings import settings
from src.api.client import ApiClient
import allure
import logging
import structlog

structlog.configure(
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    processors=[structlog.processors.JSONRenderer()],
)
logger = structlog.get_logger()

@pytest.fixture(scope="session")
def api_client() -> ApiClient:
    return ApiClient(base_url=settings.base_url, token=settings.api_token)

@pytest.fixture
def authenticated_context(context: BrowserContext, api_client: ApiClient) -> BrowserContext:
    """Авторизация через API, инжект куки в контекст"""
    payload = {"username": "test_user", "password": "secure_password"}
    response = api_client.post("/auth/login", json=payload)
    response.raise_for_status()
    token = response.json()["token"]
    
    context.add_cookies([{
        "name": "session_token",
        "value": token,
        "domain": settings.base_url.split("://")[1],
        "path": "/",
    }])
    return context

@pytest.fixture
def page(authenticated_context: BrowserContext) -> Page:
    page = authenticated_context.new_page()
    yield page
    # Скриншот при падении (обрабатывается в hook)

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    if rep.when == "call" and rep.failed:
        page = item.funcargs.get("page")
        if page:
            allure.attach(
                page.screenshot(),
                name="failure_screenshot",
                attachment_type=allure.attachment_type.PNG,
            )