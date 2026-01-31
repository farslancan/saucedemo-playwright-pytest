import csv
import logging
import re
from pathlib import Path
from typing import Optional

import pytest
from _pytest.mark.structures import ParameterSet
from playwright.sync_api import expect, Page

from automation_framework.pages.keywords.base_keywords import BaseKeywords
from automation_framework.pages.locators import login_locators, products_locators

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
        if page.locator(products_locators.APP_LOGO).first.is_visible():
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
    expect(page.locator(login_locators.USERNAME_INPUT).first).to_be_visible(timeout=15000)
    expect(page.locator(login_locators.PASSWORD_INPUT).first).to_be_visible(timeout=15000)

    user_candidates = [login_locators.USERNAME_INPUT]
    pass_candidates = [login_locators.PASSWORD_INPUT]
    submit_candidates = [login_locators.LOGIN_BUTTON]

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
        expect(page.locator(products_locators.APP_LOGO)).to_be_visible(timeout=10000)
        expect(page.locator(products_locators.PRODUCTS_TITLE)).to_be_visible(timeout=10000)
        items = page.locator(products_locators.INVENTORY_ITEM_NAME)
        expect(items.first).to_be_visible(timeout=10000)
        assert items.count() >= 1, "Expected at least one inventory item to be listed."
        if not _is_logged_in(page):
            logger.error("Login failed: not on inventory page or elements not visible")
            page.screenshot(path="login_failure.png", full_page=True)
        assert _is_logged_in(page), "Login failed"
        return True

    if is_valid is False:
        validation_message = ""
        if isinstance(validation, dict):
            validation_message = validation.get("validationMessage", "") or ""
        assert validation_message, "validationMessage is required when isValid is False."
        logger.info(f"Asserting expected error message: {validation_message}")
        error_locator = page.locator(login_locators.ERROR_MESSAGE)
        expect(error_locator).to_be_visible(timeout=10000)
        expect(error_locator).to_contain_text(validation_message, timeout=10000)
        return False

    return _is_logged_in(page)


def load_login_cases(data_file: Path) -> list[ParameterSet]:
    if not data_file.exists():
        raise FileNotFoundError(f"Login data file not found: {data_file}")

    def _parse_is_valid(raw_value: str, row_num: int) -> Optional[bool]:
        value = raw_value.strip().lower()
        if value in {"", "none"}:
            return None
        if value in {"true", "1", "yes"}:
            return True
        if value in {"false", "0", "no"}:
            return False
        raise ValueError(
            f"Row {row_num}: isValid must be true/false/blank, got '{raw_value}'."
        )

    cases: list[ParameterSet] = []
    with data_file.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader, start=2):
            username = (row.get("username") or "").strip()
            password = row.get("password") or ""
            is_valid = _parse_is_valid(row.get("isValid", ""), idx)
            validation_message = (row.get("validationMessage") or "").strip()
            severity = (row.get("severity") or "minor").strip().lower()

            validation = None
            if is_valid is not None:
                validation = {"isValid": is_valid}
                if validation_message:
                    validation["validationMessage"] = validation_message
            if is_valid is False and not validation_message:
                raise ValueError(
                    f"Row {idx}: validationMessage is required when isValid is false."
                )

            label = row.get("id") or f"row{idx-1}"
            marker = getattr(pytest.mark, severity, None)
            marks = [marker] if marker else []
            cases.append(
                pytest.param(
                    username,
                    password,
                    validation,
                    id=label,
                    marks=marks,
                )
            )
    return cases


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


__all__ = ["LoginPage", "perform_login", "load_login_cases"]
