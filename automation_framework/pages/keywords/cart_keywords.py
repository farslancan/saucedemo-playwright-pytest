import logging
import re
from playwright.sync_api import Page, expect

from automation_framework.config import global_config as gc
from automation_framework.pages.keywords.base_keywords import BaseKeywords
from automation_framework.pages.locators import cart_locators as locators
from automation_framework.pages.locators import products_locators

logger = logging.getLogger(__name__)



class CartKeywords(BaseKeywords):
    def __init__(self, page: Page):
        super().__init__(page)

    def navigate_to_cart(self) -> None:
        logger.info("Opening cart")
        self.page.locator(products_locators.CART_LINK).click()
        expect(self.page.locator(locators.CART_TITLE)).to_be_visible()
        expect(self.page.locator(locators.CART_QTY_LABEL)).to_be_visible()
        expect(self.page.locator(locators.CART_DESC_LABEL)).to_be_visible()
        expect(self.page.locator(locators.CONTINUE_SHOPPING_BUTTON)).to_be_visible()
        expect(self.page.locator(locators.CHECKOUT_BUTTON)).to_be_visible()
        logger.info("Cart opened and default locators visible")