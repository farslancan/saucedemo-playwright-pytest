import pytest
import logging
from playwright.sync_api import expect
from automation_framework.pages.keywords.cart_and_checkout_keywords import CartKeywords
from automation_framework.pages.keywords.products_keywords import ProductsKeywords
from automation_framework.pages.keywords.burger_menu_keywords import BurgerMenuKeywords
from automation_framework.pages.locators import cart_and_checkout_locators as locators
from automation_framework.pages.locators import products_locators
from automation_framework.pages.locators import login_locators

logger = logging.getLogger(__name__)

# Constants for checkout
PAYMENT_INFO = "SauceCard #31337"
SHIPPING_INFO = "Free Pony Express Delivery!"
DEFAULT_FIRST_NAME = "John"
DEFAULT_LAST_NAME = "Doe"
DEFAULT_ZIP_CODE = "12345"
SPECIAL_FIRST_NAME = "Jöhn-Döe"
SPECIAL_LAST_NAME = "Smïth"
SPECIAL_ZIP_CODE = "12345-6789"
NUMBERS_FIRST_NAME = "John123"
NUMBERS_LAST_NAME = "Doe456"
NUMBERS_ZIP_CODE = "12345"


class TestCart:
    @pytest.fixture
    def cart(self, logged_in_page):
        return CartKeywords(logged_in_page)

    @pytest.fixture
    def products(self, logged_in_page):
        return ProductsKeywords(logged_in_page)

    def test_invalid_checkout_info_empty_fields(self, products, cart):
        """Critical: Invalid empty fields."""
        products.add_random_items(count=1)
        cart.navigate_to_cart()
        cart.click_checkout()
        cart.fill_checkout_info("", "a", "1")
        cart.page.locator(locators.CHECKOUT_CONTINUE_BUTTON).click()
        expect(cart.page.locator(locators.CHECKOUT_ERROR_MESSAGE)).to_be_visible()
        expect(cart.page.locator(locators.CHECKOUT_ERROR_MESSAGE)).to_have_text("Error: First Name is required")
        cart.fill_checkout_info("a", "", "1")
        cart.page.locator(locators.CHECKOUT_CONTINUE_BUTTON).click()
        expect(cart.page.locator(locators.CHECKOUT_ERROR_MESSAGE)).to_be_visible()
        expect(cart.page.locator(locators.CHECKOUT_ERROR_MESSAGE)).to_have_text("Error: Last Name is required")
        cart.fill_checkout_info("a", "a", "")
        cart.page.locator(locators.CHECKOUT_CONTINUE_BUTTON).click()
        expect(cart.page.locator(locators.CHECKOUT_ERROR_MESSAGE)).to_be_visible()
        expect(cart.page.locator(locators.CHECKOUT_ERROR_MESSAGE)).to_have_text("Error: Postal Code is required")

    def test_remove_item_before_checkout(self, products, cart):
        """Critical: Remove item before checkout."""
        products.add_random_items(count=1)
        cart.navigate_to_cart()
        cart.remove_item_from_cart(index=0)
        cart.validate_empty_cart()
        cart.click_checkout()

    def test_logout_during_checkout_flow(self, products, cart):
        """Critical: Logout during checkout flow."""
        products.add_random_items(count=1)
        cart.navigate_to_cart()
        cart.click_checkout()
        cart.fill_checkout_info(DEFAULT_FIRST_NAME, DEFAULT_LAST_NAME, DEFAULT_ZIP_CODE)
        burger = BurgerMenuKeywords(cart.page)
        burger.open_menu()
        burger.logout_and_verify()

    def test_access_checkout_directly_without_items(self, page, creds):
        """Critical: Access checkout page directly without items."""
        checkout_url = f"{creds['base_url']}checkout-step-one.html"
        page.goto(checkout_url, wait_until="networkidle")
        expect(page.locator(login_locators.USERNAME_INPUT)).to_be_visible()

    def test_add_single_product_and_complete_checkout(self, products, cart):
        """Major: Add single product and complete checkout."""
        # Ensure cart is empty before starting
        products.verify_badge_count(expected_count=0)
        products.add_random_items(count=1)
        products.verify_badge_count(expected_count=1)
        cart.navigate_to_cart()
        expected_items = cart.get_cart_items()
        cart.validate_cart_items(expected_items)
        cart.click_checkout()
        cart.fill_checkout_info(DEFAULT_FIRST_NAME, DEFAULT_LAST_NAME, DEFAULT_ZIP_CODE)
        cart.proceed_to_overview()
        cart.verify_overview(expected_items, PAYMENT_INFO, SHIPPING_INFO)
        cart.finish_checkout()

    @pytest.mark.parametrize("checkout_data", [
        {"first_name": "John", "last_name": "Doe", "zip_code": "12345"},
        {"first_name": "Jane", "last_name": "Smith", "zip_code": "67890"}
    ])
    def test_add_multiple_products_and_complete_checkout(self, products, cart, checkout_data):
        """Major: Add multiple products and complete checkout."""
        products.add_random_items(count=3)
        products.verify_badge_count(expected_count=3)
        cart.navigate_to_cart()
        expected_items = cart.get_cart_items()
        cart.validate_cart_items(expected_items)
        cart.click_checkout()
        cart.fill_checkout_info(**checkout_data)
        cart.proceed_to_overview()
        cart.verify_overview(expected_items, PAYMENT_INFO, SHIPPING_INFO)
        cart.finish_checkout()

    def test_continue_shopping_from_cart(self, products, cart):
        """Major: Continue shopping from cart."""
        products.add_random_items(count=1)
        cart.navigate_to_cart()
        cart.continue_shopping_from_cart()
        products.add_random_items(count=1, clear_cart=False)
        cart.navigate_to_cart()
        products.verify_badge_count(expected_count=2)
        cart.navigate_to_cart()
        expected_items = cart.get_cart_items()
        cart.validate_cart_items(expected_items)
        cart.click_checkout()
        cart.fill_checkout_info(DEFAULT_FIRST_NAME, DEFAULT_LAST_NAME, DEFAULT_ZIP_CODE)
        cart.proceed_to_overview()
        cart.verify_overview(expected_items, PAYMENT_INFO, SHIPPING_INFO)
        cart.finish_checkout()

    def test_add_product_from_detail_page(self, products, cart):
        """Major: Add product from detail page and complete checkout."""
        # Add product from detail page
        idx = products.select_random_product_card()
        products.add_to_cart_from_detail_by_index(idx)
        products.verify_badge_count(expected_count=1)
        cart.navigate_to_cart()
        expected_items = cart.get_cart_items()
        cart.validate_cart_items(expected_items)
        cart.click_checkout()
        cart.fill_checkout_info(DEFAULT_FIRST_NAME, DEFAULT_LAST_NAME, DEFAULT_ZIP_CODE)
        cart.proceed_to_overview()
        cart.verify_overview(expected_items, PAYMENT_INFO, SHIPPING_INFO)
        cart.finish_checkout()

    def test_add_multiple_products_from_detail_page(self, products, cart):
        """Major: Add multiple products from detail page and complete checkout."""
        products.add_random_items(count=2)
        products.verify_badge_count(expected_count=2)
        cart.navigate_to_cart()
        expected_items = cart.get_cart_items()
        cart.validate_cart_items(expected_items)
        cart.click_checkout()
        cart.fill_checkout_info(DEFAULT_FIRST_NAME, DEFAULT_LAST_NAME, DEFAULT_ZIP_CODE)
        cart.proceed_to_overview()
        cart.verify_overview(expected_items, PAYMENT_INFO, SHIPPING_INFO)
        cart.finish_checkout()

    def test_add_and_remove_product_from_detail_page(self, products, cart):
        """Major: Add and remove product from detail page."""
        idx = products.select_random_product_card()
        products.add_to_cart_from_detail_by_index(idx)
        products.verify_badge_count(expected_count=1)
        cart.navigate_to_cart()
        cart.remove_item_from_cart(index=0)
        cart.validate_empty_cart()

    def test_add_mixed_sources(self, products, cart):
        """Major: Add multiple products from mixed sources."""
        # Add from list: index 0
        products.add_item_to_cart_by_index(0)
        # Add from detail: index 1
        products.add_to_cart_from_detail_by_index(1, clear_cart=False)
        cart.navigate_to_cart()
        products.verify_badge_count(expected_count=2)
        expected_items = cart.get_cart_items()
        cart.validate_cart_items(expected_items)
        cart.click_checkout()
        cart.fill_checkout_info(DEFAULT_FIRST_NAME, DEFAULT_LAST_NAME, DEFAULT_ZIP_CODE)
        cart.proceed_to_overview()
        cart.verify_overview(expected_items, PAYMENT_INFO, SHIPPING_INFO)
        cart.finish_checkout()

    def test_remove_one_from_multiple(self, products, cart):
        """Major: Remove one item from multiple and verify cart updates."""
        products.add_random_items(count=3)
        products.verify_badge_count(expected_count=3)
        cart.navigate_to_cart()
        expected_items = cart.get_cart_items()
        cart.validate_cart_items(expected_items)
        # Remove the first item
        cart.remove_item_from_cart(index=0)
        products.verify_badge_count(expected_count=2)
        # Verify remaining items
        remaining_items = cart.get_cart_items()
        assert len(remaining_items) == 2
        for i, item in enumerate(remaining_items):
            assert item["name"] == expected_items[i+1]["name"]
            assert item["desc"] == expected_items[i+1]["desc"]
            assert item["price"] == expected_items[i+1]["price"]
        cart.click_checkout()
        cart.fill_checkout_info(DEFAULT_FIRST_NAME, DEFAULT_LAST_NAME, DEFAULT_ZIP_CODE)
        cart.proceed_to_overview()
        cart.verify_overview(remaining_items, PAYMENT_INFO, SHIPPING_INFO)
        cart.finish_checkout()

    def test_remove_all_items_from_cart(self, products, cart):
        """Major: Remove all items from cart and verify badge updates."""
        products.add_random_items(count=3)
        products.verify_badge_count(expected_count=3)
        cart.navigate_to_cart()
        cart.remove_all_items_from_cart()
        products.verify_badge_count(expected_count=0)
        cart.validate_empty_cart()

    def test_verify_cart_resets_after_checkout(self, products, cart):
        """Major: Verify cart resets after successful checkout."""
        products.add_random_items(count=1)
        products.verify_badge_count(expected_count=1)
        cart.navigate_to_cart()
        cart.click_checkout()
        cart.fill_checkout_info(DEFAULT_FIRST_NAME, DEFAULT_LAST_NAME, DEFAULT_ZIP_CODE)
        cart.proceed_to_overview()
        cart.finish_checkout()
        # After checkout, cart should be reset
        cart.navigate_to_cart()
        cart.validate_empty_cart()
        products.verify_badge_count(expected_count=0)

    def test_validate_cart_empty_state(self, products, cart):
        """Minor: Validate empty cart."""
        products.add_random_items(count=1)
        cart.navigate_to_cart()
        cart.remove_item_from_cart(index=0)
        cart.validate_empty_cart()

    def test_cancel_from_checkout_information(self, products, cart):
        """Minor: Cancel from checkout info."""
        products.add_random_items(count=1)
        cart.navigate_to_cart()
        cart.click_checkout()
        cart.cancel_checkout()

    def test_continue_shopping_from_overview_and_complete_checkout(self, products, cart):
        """Minor: Continue shopping from overview and complete checkout."""
        # Add specific product: index 0
        products.add_item_to_cart_by_index(0)
        cart.navigate_to_cart()
        cart.click_checkout()
        cart.fill_checkout_info(DEFAULT_FIRST_NAME, DEFAULT_LAST_NAME, DEFAULT_ZIP_CODE)
        cart.proceed_to_overview()
        cart.cancel_checkout()
        # Add another specific product: index 1
        products.add_item_to_cart_by_index(1, clear_cart=False)
        cart.navigate_to_cart()
        products.verify_badge_count(expected_count=2)
        cart.click_checkout()
        cart.fill_checkout_info(DEFAULT_FIRST_NAME, DEFAULT_LAST_NAME, DEFAULT_ZIP_CODE)
        cart.proceed_to_overview()
        cart.finish_checkout()

    def test_refresh_on_checkout_overview(self, products, cart):
        """Minor: Refresh page on Checkout Overview."""
        products.add_random_items(count=1)
        cart.navigate_to_cart()
        expected_items = cart.get_cart_items()
        cart.click_checkout()
        cart.fill_checkout_info(DEFAULT_FIRST_NAME, DEFAULT_LAST_NAME, DEFAULT_ZIP_CODE)
        cart.proceed_to_overview()
        cart.page.reload(wait_until="networkidle")
        expect(cart.page.locator(locators.CHECKOUT_OVERVIEW_TITLE)).to_be_visible()
        cart.verify_overview(expected_items, PAYMENT_INFO, SHIPPING_INFO)

    def test_refresh_on_checkout_complete(self, products, cart):
        """Minor: Refresh page on Checkout Complete."""
        products.add_random_items(count=1)
        cart.navigate_to_cart()
        cart.click_checkout()
        cart.fill_checkout_info(DEFAULT_FIRST_NAME, DEFAULT_LAST_NAME, DEFAULT_ZIP_CODE)
        cart.proceed_to_overview()
        cart.finish_checkout()
        cart.page.reload(wait_until="networkidle")
        expect(cart.page.locator(products_locators.PRODUCTS_TITLE)).to_be_visible()

    def test_navigate_back_after_checkout_completion(self, products, cart):
        """Minor: Navigate browser back after checkout completion."""
        products.add_random_items(count=1)
        cart.navigate_to_cart()
        cart.click_checkout()
        cart.fill_checkout_info(DEFAULT_FIRST_NAME, DEFAULT_LAST_NAME, DEFAULT_ZIP_CODE)
        cart.proceed_to_overview()
        cart.finish_checkout()
        cart.page.go_back()
        expect(cart.page.locator(locators.CHECKOUT_COMPLETE_TITLE)).to_be_visible()

    def test_add_maximum_products(self, products, cart):
        """Edge: Add maximum products."""
        total_products = products.get_product_count()
        products.add_random_items(count=total_products)
        products.verify_badge_count(expected_count=total_products)
        cart.navigate_to_cart()
        expected_items = cart.get_cart_items()
        cart.validate_cart_items(expected_items)
        cart.click_checkout()
        cart.fill_checkout_info(DEFAULT_FIRST_NAME, DEFAULT_LAST_NAME, DEFAULT_ZIP_CODE)
        cart.proceed_to_overview()
        cart.verify_overview(expected_items, PAYMENT_INFO, SHIPPING_INFO)
        cart.finish_checkout()

    def test_minimum_valid_zip(self, products, cart):
        """Edge: Minimum valid zip."""
        products.add_random_items(count=1)
        cart.navigate_to_cart()
        cart.click_checkout()
        cart.fill_checkout_info("A", "B", "1")
        cart.proceed_to_overview()


    def test_checkout_with_special_characters(self, products, cart):
        """Edge: Checkout with special characters in names."""
        products.add_item_to_cart_by_index(0)
        cart.navigate_to_cart()
        cart.click_checkout()
        cart.fill_checkout_info(SPECIAL_FIRST_NAME, SPECIAL_LAST_NAME, SPECIAL_ZIP_CODE)
        cart.proceed_to_overview()
        expected_items = cart.get_cart_items()
        cart.verify_overview(expected_items, PAYMENT_INFO, SHIPPING_INFO)
        cart.finish_checkout()

    def test_checkout_with_very_long_names(self, products, cart):
        """Edge: Checkout with very long names."""
        long_first = "A" * 100
        long_last = "B" * 100
        long_zip = "1" * 10
        products.add_random_items(count=1)
        cart.navigate_to_cart()
        cart.click_checkout()
        cart.fill_checkout_info(long_first, long_last, long_zip)
        cart.proceed_to_overview()
        expected_items = cart.get_cart_items()
        cart.verify_overview(expected_items, PAYMENT_INFO, SHIPPING_INFO)
        cart.finish_checkout()


    def test_checkout_with_numbers_in_names(self, products, cart):
        """Edge: Checkout with numbers in names."""
        products.add_item_to_cart_by_index(0)
        cart.navigate_to_cart()
        cart.click_checkout()
        cart.fill_checkout_info(NUMBERS_FIRST_NAME, NUMBERS_LAST_NAME, NUMBERS_ZIP_CODE)
        cart.proceed_to_overview()
        expected_items = cart.get_cart_items()
        cart.verify_overview(expected_items, PAYMENT_INFO, SHIPPING_INFO)
        cart.finish_checkout()
