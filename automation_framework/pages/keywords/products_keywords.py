import logging
import random
import re
from typing import Iterable
from urllib.parse import urljoin

from playwright.sync_api import expect

from automation_framework.pages.keywords.base_keywords import BaseKeywords
from automation_framework.pages.locators import products_locators as locators

logger = logging.getLogger(__name__)


class ProductsKeywords(BaseKeywords):
    """Products/Inventory page interactions."""

    def __init__(self, page):
        super().__init__(page)
        logger.debug("ProductsKeywords initialized")

    def assert_inventory_loaded(self):
        logger.info("Verifying inventory page is loaded")
        expect(self.page).to_have_url(re.compile(r"inventory\.html/?"))
        expect(self.page.locator(locators.PRODUCTS_TITLE)).to_be_visible()
        cards = self.page.locator(locators.PRODUCT_CARD)
        expect(cards.first).to_be_visible()
        assert cards.count() >= 1, "Expected at least one product card on inventory page"
        logger.info("Inventory page loaded with at least one product")

    def verify_product_cards_have_core_fields(self):
        logger.info("Verifying product cards have name, description, price, and image")
        cards = self.page.locator(locators.PRODUCT_CARD)
        total = cards.count()
        assert total >= 1, "No product cards found on inventory page"
        for idx in range(total):
            card = cards.nth(idx)
            name = card.locator(locators.PRODUCT_NAME)
            desc = card.locator(locators.PRODUCT_DESC)
            price = card.locator(locators.PRODUCT_PRICE)
            img = card.locator(locators.PRODUCT_IMG)

            expect(name).to_be_visible()
            expect(desc).to_be_visible()
            expect(price).to_be_visible()
            expect(img).to_be_visible()

            name_text = name.inner_text().strip()
            desc_text = desc.inner_text().strip()
            price_text = price.inner_text().strip()

            assert name_text, f"Product name missing for card {idx+1}"
            assert desc_text, f"Product description missing for card {idx+1}"
            assert price_text.startswith("$"), f"Price format invalid for card {idx+1}: {price_text}"

            logger.info(
                "Product card %s | name=%s | price=%s | desc=%s",
                idx + 1,
                name_text,
                price_text,
                desc_text[:300].replace("\n", " "),
            )
        logger.info("All product cards contain required fields")

    def verify_price_format_for_all_products(self):
        logger.info("Validating product price format ($, decimal, two-digit precision)")
        cards = self.page.locator(locators.PRODUCT_CARD)
        expect(cards.first).to_be_visible()
        price_re = re.compile(r"^\$\d+\.\d{2}$")
        for idx in range(cards.count()):
            price_text = cards.nth(idx).locator(locators.PRODUCT_PRICE).inner_text().strip()
            logger.info("Price format check | index=%s | raw=%s", idx + 1, price_text)
            assert price_re.match(price_text), f"Invalid price format on card {idx+1}: {price_text}"
            logger.info("Price validated | index=%s | price=%s", idx + 1, price_text)
        logger.info("All product prices match expected currency format")

    def get_product_count(self) -> int:
        logger.info("Getting total product card count on inventory page")
        cards = self.page.locator(locators.PRODUCT_CARD)
        expect(cards.first).to_be_visible()
        total = cards.count()
        assert total > 0, "No product cards found on inventory page"
        logger.info("Total product cards found: %s", total)
        return total

    def _clear_cart_and_return(self):
        logger.info("Clearing cart before add-to-cart test")
        self.page.locator(locators.CART_LINK).click()
        remove_buttons = self.page.locator(locators.CART_REMOVE_BTN)
        for i in range(remove_buttons.count()):
            remove_buttons.nth(i).click()
        self.page.locator(locators.CART_CONTINUE_BTN).click()
        expect(self.page).to_have_url(re.compile(r"inventory\.html/?"))
        badge = self.page.locator(locators.CART_BADGE)
        if badge.count() > 0:
            expect(badge).not_to_be_visible()
        logger.info("Cart cleared and back on inventory page")

    def clear_cart(self):
        """Public wrapper to clear cart and stay on inventory page."""
        self._clear_cart_and_return()

    def add_random_items(self, count: int):
        assert count >= 1, "Count must be at least 1"
        logger.info("Adding %s random products to cart and verifying badge updates", count)

        # Ensure clean slate
        self._clear_cart_and_return()

        cards = self.page.locator(locators.PRODUCT_CARD)
        total = cards.count()
        assert total >= count, f"Need at least {count} products to validate multi-add"

        selected_indices = random.sample(range(total), count)
        for idx, sel in enumerate(selected_indices, start=1):
            card = cards.nth(sel)
            name_text = card.locator(locators.PRODUCT_NAME).inner_text().strip()
            desc_text = card.locator(locators.PRODUCT_DESC).inner_text().strip()
            price_text = card.locator(locators.PRODUCT_PRICE).inner_text().strip()

            logger.info(
                "Adding product to cart | selection=%s/%s | index=%s | name=%s | price=%s | desc=%s",
                idx,
                count,
                sel + 1,
                name_text,
                price_text,
                desc_text[:300].replace("\n", " "),
            )

            card.locator(locators.ADD_TO_CART_BTN).click()
            # Validate button toggled to Remove after add
            expect(card.locator(locators.REMOVE_BTN)).to_be_visible()
            logger.info("Button toggled to Remove after adding | index=%s", sel + 1)

            badge = self.page.locator(locators.CART_BADGE)
            expect(badge).to_be_visible()
            expect(badge).to_have_text(str(idx))

        logger.info("Badge updated correctly to %s after adding %s items", count, count)

    def verify_add_remove_toggle_on_card(self, idx: int):
        logger.info("Verifying Add→Remove→Add toggle for card index=%s", idx + 1)
        self._clear_cart_and_return()
        cards = self.page.locator(locators.PRODUCT_CARD)
        total = cards.count()
        assert 0 <= idx < total, f"Index {idx} out of range for {total} products"
        button = cards.nth(idx).locator(locators.ADD_TO_CART_BTN)
        expect(button).to_be_visible()
        expect(button).to_have_text(re.compile(r"add to cart", re.IGNORECASE))
        button.click()
        expect(button).to_have_text(re.compile(r"remove", re.IGNORECASE))
        logger.info("Button toggled to Remove after add | index=%s", idx + 1)
        button.click()
        expect(button).to_have_text(re.compile(r"add to cart", re.IGNORECASE))
        logger.info("Button toggled back to Add to cart after removal | index=%s", idx + 1)

    def verify_badge_count(self, expected_count: int):
        logger.info("Verifying cart badge equals %s", expected_count)
        badge = self.page.locator(locators.CART_BADGE)
        if expected_count <= 0:
            actual_visible = badge.count() > 0 and badge.first.is_visible()
            logger.info(
                "Badge visibility check for expected=%s | visible=%s",
                expected_count,
                actual_visible,
            )
            if badge.count() > 0:
                expect(badge).not_to_be_visible()
            logger.info("Badge hidden/absent as expected for count %s", expected_count)
            return

        expect(badge).to_be_visible()
        actual_text = badge.inner_text().strip()
        logger.info(
            "Badge text verification | expected=%s | actual=%s",
            expected_count,
            actual_text,
        )
        expect(badge).to_have_text(str(expected_count))
        logger.info("Badge text matches expected count %s", expected_count)

    def remove_one_item_and_verify_badge_cleared(self):
        logger.info("Removing one item and verifying badge is cleared")
        remove_buttons = self.page.locator(locators.REMOVE_BTN)
        assert remove_buttons.count() > 0, "No Remove buttons available to click"
        remove_buttons.first.click()
        # Validate button toggled back to Add to cart after removal
        expect(self.page.locator(locators.ADD_TO_CART_BTN).first).to_be_visible()

        badge = self.page.locator(locators.CART_BADGE)
        if badge.count() > 0:
            expect(badge).not_to_be_visible()
        logger.info("Badge cleared after removal")

    def _get_product_names(self):
        items = self.page.locator(locators.PRODUCT_NAME)
        expect(items.first).to_be_visible()
        names = [t.strip() for t in items.all_text_contents()]
        logger.info("Collected product names", extra={"count": len(names)})
        return names

    def _get_product_prices(self):
        prices = self.page.locator(locators.PRODUCT_PRICE)
        expect(prices.first).to_be_visible()
        values = []
        for text in prices.all_text_contents():
            cleaned = text.strip().replace("$", "")
            try:
                values.append(float(cleaned))
            except ValueError:
                raise AssertionError(f"Invalid price format: {text}")
        logger.info("Collected product prices", extra={"count": len(values)})
        return values

    def select_sort_by_name(self, order: str):
        order_normalized = order.lower()
        option_map = {
            "asc": ("az", "A to Z"),
            "desc": ("za", "Z to A"),
        }
        assert order_normalized in option_map, f"Unsupported sort order: {order}"

        option_value, label = option_map[order_normalized]
        logger.info("Selecting sort option: Name (%s)", label)
        selects = self.page.locator(locators.SORT_SELECT)
        assert selects.count() >= 1, "Sort select not found"
        sort_select = selects.first
        sort_select.scroll_into_view_if_needed()
        expect(sort_select).to_be_visible()
        sort_select.select_option(option_value)
        active = self.page.locator(locators.SORT_ACTIVE_OPTION)
        expect(active).to_be_visible()
        expect(active).to_contain_text(label)
        logger.info("Sort option Name (%s) selected", label)

    def verify_sorted_by_name(self, order: str):
        order_normalized = order.lower()
        assert order_normalized in {"asc", "desc"}, f"Unsupported sort order: {order}"
        logger.info("Verifying products are sorted by name (%s)", order_normalized)
        names = self._get_product_names()
        expected = sorted(names, key=str.lower, reverse=(order_normalized == "desc"))
        logger.info(
            "Name sort verification | order=%s | actual=%s | expected=%s",
            order_normalized,
            names,
            expected,
        )
        assert names == expected, f"Names not sorted {order_normalized}: {names}"
        logger.info("Products sorted correctly by name (%s)", order_normalized)

    def select_sort_by_price(self, order: str):
        order_normalized = order.lower()
        option_map = {
            "low_high": ("lohi", "low to high"),
            "high_low": ("hilo", "high to low"),
        }
        assert order_normalized in option_map, f"Unsupported price sort order: {order}"

        option_value, label = option_map[order_normalized]
        logger.info("Selecting sort option: Price (%s)", label)
        selects = self.page.locator(locators.SORT_SELECT)
        assert selects.count() >= 1, "Sort select not found"
        sort_select = selects.first
        sort_select.scroll_into_view_if_needed()
        expect(sort_select).to_be_visible()
        sort_select.select_option(option_value)
        active = self.page.locator(locators.SORT_ACTIVE_OPTION)
        expect(active).to_be_visible()
        expect(active).to_contain_text(label)
        logger.info("Sort option Price (%s) selected", label)

    def verify_sorted_by_price(self, order: str):
        order_normalized = order.lower()
        assert order_normalized in {"low_high", "high_low"}, f"Unsupported price sort order: {order}"
        logger.info("Verifying products are sorted by price (%s)", order_normalized)
        prices = self._get_product_prices()
        expected = sorted(prices, reverse=(order_normalized == "high_low"))
        logger.info(
            "Price sort verification | order=%s | actual=%s | expected=%s",
            order_normalized,
            prices,
            expected,
        )
        assert prices == expected, f"Prices not sorted {order_normalized}: {prices}"
        logger.info("Products sorted correctly by price (%s)", order_normalized)

    def verify_sort_option_label(self, expected_label: str):
        logger.info("Verifying sort dropdown displays: %s", expected_label)
        active = self.page.locator(locators.SORT_ACTIVE_OPTION)
        expect(active).to_be_visible()
        expect(active).to_contain_text(expected_label)
        logger.info("Sort dropdown label matches: %s", expected_label)

    def select_random_product_card(self):
        cards = self.page.locator(locators.PRODUCT_CARD)
        total = cards.count()
        assert total >= 1, "No product cards available to open"
        idx = random.randrange(total)
        logger.info("Randomly selected product card index=%s of %s", idx + 1, total)
        return idx

    def extract_card_info(self, idx: int):
        card = self.page.locator(locators.PRODUCT_CARD).nth(idx)
        name_el = card.locator(locators.PRODUCT_NAME)
        desc_el = card.locator(locators.PRODUCT_DESC)
        price_el = card.locator(locators.PRODUCT_PRICE)
        name_text = name_el.inner_text().strip()
        desc_text = desc_el.inner_text().strip()
        price_text = price_el.inner_text().strip()
        logger.info(
            "Card values | index=%s | name=%s | price=%s | desc=%s",
            idx + 1,
            name_text,
            price_text,
            desc_text[:300].replace("\n", " "),
        )
        return {
            "index": idx,
            "name": name_text,
            "desc": desc_text,
            "price": price_text,
        }

    def open_detail_from_card(self, idx: int):
        card = self.page.locator(locators.PRODUCT_CARD).nth(idx)
        card.locator(locators.PRODUCT_NAME).click()
        logger.info("Opened detail page from card index=%s", idx + 1)

    def get_detail_info(self):
        detail_name = self.page.locator(locators.PRODUCT_DETAIL_NAME).first
        detail_desc = self.page.locator(locators.PRODUCT_DETAIL_DESC).first
        detail_price = self.page.locator(locators.PRODUCT_DETAIL_PRICE).first
        expect(detail_name).to_be_visible()
        expect(detail_desc).to_be_visible()
        expect(detail_price).to_be_visible()
        name_text = detail_name.inner_text().strip()
        desc_text = detail_desc.inner_text().strip()
        price_text = detail_price.inner_text().strip()
        logger.info(
            "Detail values | name=%s | price=%s | desc=%s",
            name_text,
            price_text,
            desc_text[:300].replace("\n", " "),
        )
        return {
            "name": name_text,
            "desc": desc_text,
            "price": price_text,
        }

    def verify_detail_matches(self, expected: dict, actual: dict):
        logger.info(
            "Verifying detail matches card | expected=%s | actual=%s",
            expected,
            actual,
        )
        assert actual["name"] == expected["name"], "Detail name does not match list card"
        assert actual["desc"] == expected["desc"], "Detail description does not match list card"
        assert actual["price"] == expected["price"], "Detail price does not match list card"
        logger.info("Detail page matches list card values")

    def return_to_inventory_from_detail(self):
        back_btn = self.page.locator(locators.PRODUCT_DETAIL_BACK_BTN)
        expect(back_btn).to_be_visible()
        back_btn.click()
        expect(self.page.locator(locators.PRODUCTS_TITLE)).to_be_visible()
        logger.info("Returned to inventory page after detail verification")

    def add_item_to_cart_by_index(self, idx: int):
        logger.info("Adding product by index=%s after clearing cart", idx + 1)
        self._clear_cart_and_return()
        cards = self.page.locator(locators.PRODUCT_CARD)
        total = cards.count()
        assert 0 <= idx < total, f"Index {idx} out of range for {total} products"
        card_info = self.extract_card_info(idx)
        add_btn = cards.nth(idx).locator(locators.ADD_TO_CART_BTN)
        expect(add_btn).to_be_visible()
        add_btn.click()
        # Validate button toggled to Remove after add
        expect(cards.nth(idx).locator(locators.REMOVE_BTN)).to_be_visible()
        logger.info("Button toggled to Remove after adding | index=%s", idx + 1)
        logger.info(
            "Added product to cart | index=%s | name=%s | price=%s",
            idx + 1,
            card_info["name"],
            card_info["price"],
        )
        self.verify_badge_count(1)

    def add_to_cart_from_detail_by_index(self, idx: int):
        logger.info("Adding product to cart from detail page | index=%s", idx + 1)
        self._clear_cart_and_return()
        cards = self.page.locator(locators.PRODUCT_CARD)
        total = cards.count()
        assert 0 <= idx < total, f"Index {idx} out of range for {total} products"
        card_info = self.extract_card_info(idx)
        self.open_detail_from_card(idx)
        add_btn = self.page.locator(locators.ADD_TO_CART_BTN).first
        expect(add_btn).to_be_visible()
        add_btn.click()
        # Validate button toggled to Remove after add on detail page
        expect(self.page.locator(locators.REMOVE_BTN).first).to_be_visible()
        logger.info("Button toggled to Remove on detail after adding | index=%s", idx + 1)
        logger.info(
            "Added from detail | name=%s | price=%s | desc=%s",
            card_info["name"],
            card_info["price"],
            card_info["desc"][:300].replace("\n", " "),
        )
        self.verify_badge_count(1)

    def remove_item_from_detail_and_verify_badge_cleared(self):
        logger.info("Removing item from detail page and verifying badge cleared")
        remove_btn = self.page.locator(locators.REMOVE_BTN).first
        expect(remove_btn).to_be_visible()
        remove_btn.click()
        # Validate button toggled back to Add to cart after removal on detail page
        expect(self.page.locator(locators.ADD_TO_CART_BTN).first).to_be_visible()
        badge = self.page.locator(locators.CART_BADGE)
        if badge.count() > 0:
            expect(badge).not_to_be_visible()
        logger.info("Badge cleared after removal on detail page")

    def open_cart(self):
        logger.info("Opening cart from inventory")
        self.page.locator(locators.CART_LINK).click()
        expect(self.page).to_have_url(re.compile(r"cart\.html/?"))
        continue_btn = self.page.locator(locators.CART_CONTINUE_BTN)
        expect(continue_btn).to_be_visible()
        logger.info("Cart page opened; continue button visible")

    def return_to_inventory_from_cart(self):
        logger.info("Returning to inventory from cart")
        continue_btn = self.page.locator(locators.CART_CONTINUE_BTN)
        expect(continue_btn).to_be_visible()
        continue_btn.click()
        expect(self.page).to_have_url(re.compile(r"inventory\.html/?"))
        expect(self.page.locator(locators.PRODUCTS_TITLE)).to_be_visible()
        logger.info("Returned to inventory page from cart")


__all__ = ["ProductsKeywords"]
