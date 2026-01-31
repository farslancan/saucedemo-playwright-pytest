import logging
import re
import pytest
from playwright.sync_api import expect

from automation_framework.config import global_config as gc
from automation_framework.pages import LoginPage
from automation_framework.pages.keywords.burger_menu_keywords import BurgerMenuKeywords, ensure_logged_out
from automation_framework.pages.keywords.login_keywords import load_login_cases
from automation_framework.pages.locators import login_locators

logger = logging.getLogger(__name__)

DATA_FILE = gc.DATA_DIR / "login_test_data.csv"
_LOGIN_CASES = load_login_cases(DATA_FILE)


@pytest.mark.parametrize("username,password,validation", _LOGIN_CASES)
def test_authentication_login(page, creds, username, password, validation):
    is_valid = validation.get("isValid") if isinstance(validation, dict) else None
    if is_valid is False:
        resolved_username = username
        resolved_password = password
    else:
        resolved_username = username or creds["username"]
        resolved_password = password or creds["password"]

    logger.info(
        "Executing authentication test",
        extra={
            "case": resolved_username or "<empty>",
            "has_validation": bool(validation),
        },
    )
    LoginPage(page).login(
        creds["base_url"],
        resolved_username,
        resolved_password,
        validation,
    )


def test_direct_detail_redirects_when_unauthenticated(page, creds):
    # Ensure we start logged out to verify redirect behaviour
    ensure_logged_out(page)
    detail_url = f"{creds['base_url']}inventory-item.html?id=0"
    page.goto(detail_url, wait_until="networkidle")
    expect(page.locator(login_locators.USERNAME_INPUT).first).to_be_visible()
    expect(page.locator(login_locators.PASSWORD_INPUT).first).to_be_visible()
    error = page.locator(login_locators.ERROR_MESSAGE)
    expect(error).to_be_visible()
    expect(error).to_have_text(
        "Epic sadface: You can only access '/inventory-item.html' when you are logged in."
    )


def test_inventory_access_requires_auth(page, creds):
    # Ensure we start logged out to verify redirect behaviour
    ensure_logged_out(page)
    inventory_url = f"{creds['base_url']}inventory.html"
    page.goto(inventory_url, wait_until="networkidle")
    expect(page.locator(login_locators.USERNAME_INPUT).first).to_be_visible()
    expect(page.locator(login_locators.PASSWORD_INPUT).first).to_be_visible()
    error = page.locator(login_locators.ERROR_MESSAGE)
    expect(error).to_be_visible()
    expect(error).to_have_text("Epic sadface: You can only access '/inventory.html' when you are logged in.")
    assert "inventory.html" in inventory_url
