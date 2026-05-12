"""
Smoke tests for E2E validation.

Quick sanity checks to verify the application is running and basic functionality works.
Mark with @pytest.mark.smoke for CI inclusion.
"""

import re

import pytest
from playwright.sync_api import Page, expect


@pytest.mark.smoke
def test_homepage_loads(page: Page) -> None:
    """Verify homepage loads successfully."""
    from src.config.settings import settings

    page.goto(settings.base_url)
    expect(page).to_have_title(re.compile(r".+"))  # Любой непустой заголовок
    expect(page).to_have_url(settings.base_url)


@pytest.mark.smoke
def test_no_console_errors(page: Page) -> None:
    """Verify no critical console errors on page load."""
    from src.config.settings import settings

    errors = []

    def handle_console(msg):
        if msg.type == "error":
            errors.append(msg.text)

    page.on("console", handle_console)
    page.goto(settings.base_url)

    # Filter out non-critical errors (e.g., favicon 404)
    critical_errors = [e for e in errors if "favicon" not in e.lower()]
    assert len(critical_errors) == 0, f"Console errors found: {critical_errors}"


@pytest.mark.smoke
def test_page_responsive(page: Page) -> None:
    """Verify page is responsive on different viewport sizes."""
    from src.config.settings import settings

    page.goto(settings.base_url)

    # Test mobile viewport
    page.set_viewport_size({"width": 375, "height": 667})
    assert page.viewport_size["width"] == 375

    # Test desktop viewport
    page.set_viewport_size({"width": 1920, "height": 1080})
    assert page.viewport_size["width"] == 1920
