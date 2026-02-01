import logging
import re
from playwright.sync_api import Page, expect

from automation_framework.config import global_config as gc
from automation_framework.pages.keywords.base_keywords import BaseKeywords
from automation_framework.pages.locators import burger_menu_locators as burger_locators
from automation_framework.pages.locators import login_locators
from automation_framework.pages.locators import products_locators as locators

logger = logging.getLogger(__name__)


def ensure_logged_out(page: Page):
    """Guarantee the session is logged out; navigate to inventory then logout if needed."""
    try:
        if page.locator(login_locators.USERNAME_INPUT).first.is_visible(timeout=2000):
            return
    except Exception:
        pass

    target = f"{gc.SAUCE_DEMO_URL}inventory.html"
    page.goto(target, wait_until="domcontentloaded")
    page.wait_for_load_state("networkidle")

    # If login form is shown after navigation, we are already logged out.
    if page.locator(login_locators.USERNAME_INPUT).first.count() > 0:
        try:
            expect(page.locator(login_locators.USERNAME_INPUT).first).to_be_visible(timeout=2000)
            return
        except Exception:
            pass

    # Otherwise assume logged in and logout via burger menu.
    menu = BurgerMenuKeywords(page)
    menu.open_menu()
    menu.logout_and_verify()


class BurgerMenuKeywords(BaseKeywords):
    def __init__(self, page: Page):
        super().__init__(page)

    def open_menu(self):
        logger.info("Opening burger menu")
        try:
            expect(self.page.locator(burger_locators.BURGER_MENU).first).to_be_visible()
        except Exception as e:
            logger.error(f"Burger menu button not visible: {e}")
            raise
        self.page.locator(burger_locators.BURGER_MENU).first.click()
        expect(self.page.locator(burger_locators.BURGER_MENU_OVERLAY)).to_be_visible()
        logger.info("Burger menu opened and overlay visible")

    def assert_menu_items(self):
        logger.info("Asserting burger menu items are visible")
        expect(self.page.locator(burger_locators.BURGER_MENU_ALL_ITEMS)).to_be_visible()
        expect(self.page.locator(burger_locators.BURGER_MENU_ABOUT)).to_be_visible()
        expect(self.page.locator(burger_locators.BURGER_MENU_LOGOUT)).to_be_visible()
        expect(self.page.locator(burger_locators.BURGER_MENU_RESET)).to_be_visible()
        logger.info("Burger menu items verified")

    def select_all_items_and_verify(self):
        logger.info("Clicking 'All Items'")
        self.page.locator(burger_locators.BURGER_MENU_ALL_ITEMS).click()
        expect(self.page).to_have_url(re.compile(r"inventory\.html/?"))
        logger.info("Navigated to inventory via All Items")

    def open_about_in_new_tab_and_verify(self):
        href = self.page.locator(burger_locators.BURGER_MENU_ABOUT).get_attribute("href")
        assert href, "About link href is missing"
        logger.info("Opening About link in new tab", extra={"href": href})
        about_page = self.page.context.new_page()
        about_page.goto(href, wait_until="domcontentloaded")
        expect(about_page).to_have_url(re.compile(r"saucelabs\.com"))
        logger.info("About page opened", extra={"url": about_page.url})
        about_page.close()

    def logout_and_verify(self):
        logger.info("Clicking Logout")
        self.page.locator(burger_locators.BURGER_MENU_LOGOUT).click()
        expect(self.page.locator(login_locators.USERNAME_INPUT)).to_be_visible()
        expect(self.page.locator(login_locators.PASSWORD_INPUT)).to_be_visible()
        logger.info("Logout successful; login form visible")

    def reset_app_state_and_verify(self):
        logger.info("Clicking Reset App State")
        self.page.locator(burger_locators.BURGER_MENU_RESET).click()
        badge = self.page.locator(locators.CART_BADGE)
        if badge.count() > 0:
            expect(badge).not_to_be_visible()
        logger.info("Reset App State completed and cart badge cleared/hidden")

    def close_menu_and_verify_hidden(self):
        logger.info("Closing burger menu")
        expect(self.page.locator(burger_locators.BURGER_MENU_CLOSE)).to_be_visible()
        self.page.locator(burger_locators.BURGER_MENU_CLOSE).click()
        expect(self.page.locator(burger_locators.BURGER_MENU_ALL_ITEMS)).not_to_be_visible()
        expect(self.page.locator(burger_locators.BURGER_MENU_ABOUT)).not_to_be_visible()
        expect(self.page.locator(burger_locators.BURGER_MENU_LOGOUT)).not_to_be_visible()
        expect(self.page.locator(burger_locators.BURGER_MENU_RESET)).not_to_be_visible()
        logger.info("Burger menu closed and items hidden")


__all__ = ["BurgerMenuKeywords", "ensure_logged_out"]
