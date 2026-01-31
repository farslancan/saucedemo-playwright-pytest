import logging
import re
from typing import Optional

from playwright.sync_api import expect, Page

from automation_framework.pages.keywords.base_keywords import BaseKeywords
from automation_framework.pages.locators import products_locators as locators

logger = logging.getLogger(__name__)


def _first_existing(page: Page, selectors):
    for selector in selectors:
        locator = page.locator(selector)
        try:
            if locator.count() > 0:
                return locator.first
        except Exception:
            continue
    return None


def _is_logged_in(page: Page) -> bool:
    try:
        page.wait_for_load_state("networkidle", timeout=3000)
    except Exception:
        pass

    # Consider user logged in if already on inventory page or inventory elements visible
    url = page.url or ""
    if re.search(r"/inventory\.html/?$", url):
        return True
    try:
        if page.locator(locators.APP_LOGO).first.is_visible():
            return True
    except Exception:
        pass
    return False


def perform_login(
    page: Page,
    base_url: str,
    username: str,
    password: str,
    validation: Optional[dict] = None,
):
    logger.info(f"Navigating to login page: {base_url}")
    page.goto(base_url, wait_until="domcontentloaded")
    logger.info(f"Arrived at URL: {page.url}")
    page.wait_for_load_state("networkidle")

    logger.info("Waiting for login form")
    expect(page.locator(locators.USERNAME_INPUT).first).to_be_visible(timeout=15000)
    expect(page.locator(locators.PASSWORD_INPUT).first).to_be_visible(timeout=15000)

    user_candidates = [locators.USERNAME_INPUT]
    pass_candidates = [locators.PASSWORD_INPUT]
    submit_candidates = [locators.LOGIN_BUTTON]

    user_input = _first_existing(page, user_candidates) or page.get_by_role("textbox").first
    password_input = _first_existing(page, pass_candidates)
    submit_btn = _first_existing(page, submit_candidates)

    assert user_input is not None, "Could not find username/email input on the page."
    assert password_input is not None, "Could not find password input on the page."
    assert submit_btn is not None, "Could not find submit button on the page."

    user_preview = username or "(empty)"
    pass_preview = "***" if password else "(empty)"
    logger.info(f"Filling username: {user_preview}")
    user_input.fill(username or "")
    logger.info(f"Filling password: {pass_preview}")
    password_input.fill(password or "")
    logger.info("Clicking submit")
    submit_btn.click()

    logger.info("Waiting for post-login state")
    page.wait_for_load_state("networkidle", timeout=15000)
    logger.info(f"Current URL after submit: {page.url}")

    if validation is None:
        return _is_logged_in(page)

    is_valid = validation.get("isValid") if isinstance(validation, dict) else None
    if is_valid is True:
        logger.info("Asserting successful login state")
        expect(page).to_have_url(re.compile(r"https://www\.saucedemo\.com/inventory\.html/?"), timeout=15000)
        expect(page.locator(locators.APP_LOGO)).to_be_visible(timeout=10000)
        expect(page.locator(locators.PRODUCTS_TITLE)).to_be_visible(timeout=10000)
        items = page.locator(locators.INVENTORY_ITEM_NAME)
        expect(items.first).to_be_visible(timeout=10000)
        assert items.count() >= 1, "Expected at least one inventory item to be listed."
        if not _is_logged_in(page):
            page.screenshot(path="login_failure.png", full_page=True)
        assert _is_logged_in(
            page
        ), f"Login might have failed. Current URL: {page.url}. Screenshot saved to login_failure.png"
        return True

    if is_valid is False:
        validation_message = ""
        if isinstance(validation, dict):
            validation_message = validation.get("validationMessage", "") or ""
        assert validation_message, "validationMessage is required when isValid is False."
        logger.info(f"Asserting expected error message: {validation_message}")
        error_locator = page.locator(locators.ERROR_MESSAGE)
        expect(error_locator).to_be_visible(timeout=10000)
        expect(error_locator).to_contain_text(validation_message, timeout=10000)
        return False

    return _is_logged_in(page)


class LoginPage(BaseKeywords):
    """
    Page Object wrapper around the perform_login helper.
    """

    def __init__(self, page: Page):
        super().__init__(page)

    def login(
        self,
        base_url: str,
        username: str,
        password: str,
        validation: Optional[dict] = None,
    ):
        logger.info(
            "Performing login",
            extra={
                "base_url": base_url,
                "username": username,
                "has_validation": bool(validation),
            },
        )
        return perform_login(self.page, base_url, username, password, validation)


__all__ = ["LoginPage", "perform_login"]
