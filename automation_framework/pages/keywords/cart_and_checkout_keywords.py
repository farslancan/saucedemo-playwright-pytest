import logging
from playwright.sync_api import Page, expect
import re

from automation_framework.pages.keywords.base_keywords import BaseKeywords
from automation_framework.pages.locators import cart_and_checkout_locators as locators
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

    def validate_cart_items(self, expected_items: list[dict]) -> None:
        """Validate cart items match expected details."""
        logger.info("Validating cart items")
        cart_items = self.page.locator(locators.CART_ITEM)
        expect(cart_items.first).to_be_visible()
        count = cart_items.count()
        if count != len(expected_items):
            logger.error(f"Cart item count mismatch: expected {len(expected_items)}, found {count}")
        assert count == len(expected_items), f"Expected {len(expected_items)} items, found {count}"
        for i, item in enumerate(expected_items):
            item_locator = cart_items.nth(i)
            expect(item_locator.locator(locators.INVENTORY_ITEM_NAME)).to_have_text(item["name"])
            expect(item_locator.locator(locators.INVENTORY_ITEM_DESC)).to_have_text(item["desc"])
            expect(item_locator.locator(locators.INVENTORY_ITEM_PRICE)).to_have_text(item["price"])
            logger.info("Validated cart item %d: name='%s', desc='%s', price='%s'", i+1, item["name"], item["desc"][:100], item["price"])
        logger.info("All %d cart items validated successfully", len(expected_items))

    def click_checkout(self) -> None:
        logger.info("Clicking checkout button")
        self.page.locator(locators.CHECKOUT_BUTTON).click()
        expect(self.page.locator(locators.CHECKOUT_INFO_TITLE)).to_be_visible()
        logger.info("Navigated to checkout information page")

    def fill_checkout_info(self, first_name: str, last_name: str, zip_code: str) -> None:
        logger.info("Filling checkout information")
        self.page.locator(locators.CHECKOUT_FIRST_NAME_INPUT).fill(first_name)
        self.page.locator(locators.CHECKOUT_LAST_NAME_INPUT).fill(last_name)
        self.page.locator(locators.CHECKOUT_ZIP_INPUT).fill(zip_code)
        logger.info("Filled checkout info: first_name='%s', last_name='%s', zip_code='%s'", first_name, last_name, zip_code)
        logger.info("Checkout information filled")

    def proceed_to_overview(self) -> None:
        logger.info("Proceeding to checkout overview")
        self.page.locator(locators.CHECKOUT_CONTINUE_BUTTON).click()
        expect(self.page.locator(locators.CHECKOUT_OVERVIEW_TITLE)).to_be_visible()
        logger.info("Navigated to checkout overview")

    def verify_overview(self, expected_items: list[dict], payment: str, shipping: str) -> None:
        logger.info("Verifying checkout overview")
        # Verify items
        self.validate_cart_items(expected_items)
        # Verify payment
        expect(self.page.locator(locators.PAYMENT_INFO)).to_have_text(payment)
        logger.info("Verified payment information: '%s'", payment)
        # Verify shipping
        expect(self.page.locator(locators.SHIPPING_INFO)).to_have_text(shipping)
        logger.info("Verified shipping information: '%s'", shipping)
        # Calculate totals
        item_total = sum(float(item["price"].replace("$", "")) for item in expected_items)
        tax = round(item_total * 0.08, 2)  # Assuming 8% tax
        total = item_total + tax
        logger.info("Calculated totals: item_total=%.2f, tax=%.2f, total=%.2f", item_total, tax, total)
        # Verify totals
        expect(self.page.locator(locators.ITEM_TOTAL)).to_have_text(f"Item total: ${item_total:.2f}")
        expect(self.page.locator(locators.TAX_TOTAL)).to_have_text(f"Tax: ${tax:.2f}")
        expect(self.page.locator(locators.TOTAL_PRICE)).to_have_text(f"Total: ${total:.2f}")
        logger.info("All totals verified successfully")
        logger.info("Checkout overview verified")

    def finish_checkout(self) -> None:
        logger.info("Finishing checkout")
        self.page.locator(locators.FINISH_BUTTON).click()
        expect(self.page.locator(locators.CHECKOUT_COMPLETE_TITLE)).to_be_visible()
        expect(self.page.locator(locators.COMPLETE_TEXT)).to_have_text("Thank you for your order!")
        expect(self.page.locator(locators.BACK_HOME_BUTTON)).to_be_visible()
        logger.info("Checkout completed successfully")
        # Click Back Home and verify navigation to inventory
        self.page.locator(locators.BACK_HOME_BUTTON).click()
        expect(self.page.locator(products_locators.PRODUCTS_TITLE)).to_be_visible()
        expect(self.page).to_have_url(re.compile(r"inventory\.html"))
        logger.info("Navigated back to inventory from checkout complete")

    def cancel_checkout(self) -> None:
        logger.info("Canceling checkout")
        is_on_overview = self.page.locator(locators.CHECKOUT_OVERVIEW_TITLE).is_visible()
        self.page.locator(locators.CHECKOUT_CANCEL_BUTTON).click()
        if is_on_overview:
            expect(self.page.locator(products_locators.PRODUCTS_TITLE)).to_be_visible()
            logger.info("Returned to products page from overview")
        else:
            expect(self.page.locator(locators.CART_TITLE)).to_be_visible()
            logger.info("Returned to cart")

    def continue_shopping_from_cart(self) -> None:
        logger.info("Continuing shopping from cart")
        self.page.locator(locators.CONTINUE_SHOPPING_BUTTON).click()
        expect(self.page.locator(products_locators.PRODUCTS_TITLE)).to_be_visible()
        expect(self.page).to_have_url(re.compile(r"inventory\.html"))
        logger.info("Returned to products page")

    def get_cart_items(self) -> list[dict]:
        """Get list of items in cart."""
        logger.info("Getting cart items")
        items = []
        cart_items = self.page.locator(locators.CART_ITEM)
        count = cart_items.count()
        for i in range(count):
            item_locator = cart_items.nth(i)
            name = item_locator.locator(locators.INVENTORY_ITEM_NAME).inner_text().strip()
            desc = item_locator.locator(locators.INVENTORY_ITEM_DESC).inner_text().strip()
            price = item_locator.locator(locators.INVENTORY_ITEM_PRICE).inner_text().strip()
            items.append({"name": name, "desc": desc, "price": price})
            logger.info("Retrieved cart item %d: name='%s', desc='%s', price='%s'", i+1, name, desc[:100], price)
        logger.info("Retrieved %d cart items", len(items))
        return items

    def continue_shopping_from_overview(self) -> None:
        logger.info("Continuing shopping from overview")
        self.page.locator(locators.CONTINUE_SHOPPING_BUTTON).click()
        expect(self.page.locator(products_locators.PRODUCTS_TITLE)).to_be_visible()
        expect(self.page).to_have_url(re.compile(r"inventory\.html"))
        logger.info("Returned to products page from overview")

    def remove_item_from_cart(self, index: int = 0) -> None:
        """Remove an item from cart by index (default first)."""
        logger.info("Removing item from cart at index %s", index)
        cart_items = self.page.locator(locators.CART_ITEM)
        if cart_items.count() > index:
            remove_btn = cart_items.nth(index).locator("button[data-test*='remove']")
            expect(remove_btn).to_be_visible()
            remove_btn.click()
            logger.info("Item removed from cart")
        else:
            logger.warning("No item at index %s to remove", index)

    def remove_all_items_from_cart(self) -> None:
        """Remove all items from cart."""
        logger.info("Removing all items from cart")
        while True:
            cart_items = self.page.locator(locators.CART_ITEM)
            count = cart_items.count()
            if count == 0:
                break
            self.remove_item_from_cart(index=0)
        logger.info("All items removed from cart")

    def validate_empty_cart(self) -> None:
        """Validate that the cart is empty."""
        logger.info("Validating cart is empty")
        cart_items = self.page.locator(locators.CART_ITEM)
        count = cart_items.count()
        if count != 0:
            logger.error(f"Cart is not empty: found {count} items")
        expect(cart_items).to_have_count(0)
        logger.info("Cart is empty")
