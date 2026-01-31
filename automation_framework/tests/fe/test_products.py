import pytest

from automation_framework.pages import ProductsKeywords
from automation_framework.pages import BurgerMenuKeywords


@pytest.fixture
def products(logged_in_page):
    return ProductsKeywords(logged_in_page)


@pytest.mark.smoke
@pytest.mark.products
@pytest.mark.usefixtures("logged_in_page")
class TestProductsPage:

    def test_load_inventory_page(self, products):
        """Major: Load inventory page."""
        products.assert_inventory_loaded()

    def test_product_card_fields(self, products):
        """Major: Product card fields."""
        products.verify_product_cards_have_core_fields()

    def test_add_to_cart_updates_badge(self, products):
        """Major: Add to cart updates badge."""
        products.add_random_items(count=2)
        products.verify_badge_count(expected_count=2)

    def test_remove_from_cart_updates_badge(self, products):
        """Major: Remove from cart updates badge."""
        products.add_random_items(count=1)
        products.verify_badge_count(expected_count=1)
        products.remove_one_item_and_verify_badge_cleared()

    def test_sort_name_asc(self, products):
        """Major: Sort name ascending."""
        products.select_sort_by_name("asc")
        products.verify_sorted_by_name("asc")

    def test_sort_name_desc(self, products):
        """Major: Sort name descending."""
        products.select_sort_by_name("desc")
        products.verify_sorted_by_name("desc")

    def test_sort_price_low_high(self, products):
        """Major: Sort price low to high."""
        products.select_sort_by_price("low_high")
        products.verify_sorted_by_price("low_high")

    def test_sort_price_high_low(self, products):
        """Major: Sort price high to low."""
        products.select_sort_by_price("high_low")
        products.verify_sorted_by_price("high_low")

    def test_product_detail_navigation(self, products):
        """Major: Product detail navigation."""
        idx = products.select_random_product_card()
        card_info = products.extract_card_info(idx)
        products.open_detail_from_card(idx)
        detail_info = products.get_detail_info()
        products.verify_detail_matches(card_info, detail_info)
        products.return_to_inventory_from_detail()

    def test_add_to_cart_from_product_detail(self, products):
        """Major: Add to cart from product detail."""
        idx = products.select_random_product_card()
        products.add_to_cart_from_detail_by_index(idx)
        products.return_to_inventory_from_detail()

    def test_back_to_products_navigation(self, products):
        """Major: Back to products navigation."""
        idx = products.select_random_product_card()
        products.open_detail_from_card(idx)
        products.return_to_inventory_from_detail()
        products.assert_inventory_loaded()

    def test_add_remove_from_detail_page(self, products):
        """Major: Add remove from detail page."""
        idx = products.select_random_product_card()
        products.add_item_to_cart_by_index(idx)
        products.open_detail_from_card(idx)
        products.remove_item_from_detail_and_verify_badge_cleared()
        products.return_to_inventory_from_detail()

    def test_cart_link_navigation(self, products):
        """Major: Cart link navigation."""
        products.add_random_items(count=1)
        products.verify_badge_count(expected_count=1)
        products.open_cart()
        products.return_to_inventory_from_cart()
        products.assert_inventory_loaded()

    def test_price_format_validation(self, products):
        """Major: Price format validation."""
        products.verify_price_format_for_all_products()

    def test_cart_badge_persists_after_refresh(self, products):
        """Minor: Cart badge persists after refresh."""
        products.add_random_items(count=2)
        products.verify_badge_count(expected_count=2)
        products.page.reload(wait_until="networkidle")
        products.verify_badge_count(expected_count=2)

    def test_sort_persists_after_cart_actions(self, products):
        """Minor: Sort persists after cart actions."""
        products.select_sort_by_name("asc")
        products.verify_sorted_by_name("asc")
        products.add_random_items(count=1)
        products.verify_badge_count(expected_count=1)
        products.remove_one_item_and_verify_badge_cleared()
        products.verify_sorted_by_name("asc")

    def test_burger_menu_from_cart_checkout(self, products):
        """Minor: Burger menu from cart checkout."""
        products.add_random_items(count=1)
        products.verify_badge_count(expected_count=1)
        products.open_cart()
        menu = BurgerMenuKeywords(products.page)
        menu.open_menu()
        menu.assert_menu_items()
        menu.close_menu_and_verify_hidden()
        products.return_to_inventory_from_cart()
        products.assert_inventory_loaded()

    def test_sort_persists_after_reset_app_state(self, products):
        """Minor: Sort persists after reset app state."""
        products.select_sort_by_name("desc")
        products.verify_sorted_by_name("desc")
        menu = BurgerMenuKeywords(products.page)
        menu.open_menu()
        menu.reset_app_state_and_verify()
        products.verify_sort_option_label("Name (Z to A)")
        products.verify_sorted_by_name("desc")

    def test_sort_reset_after_reload(self, products):
        """Minor: Sort reset after reload."""
        products.select_sort_by_price("low_high")
        products.verify_sorted_by_price("low_high")
        products.page.reload(wait_until="networkidle")
        products.verify_sort_option_label("Name (A to Z)")
        products.verify_sorted_by_name("asc")

    def test_cart_badge_overflow(self, products):
        """Edge: Cart badge overflow."""
        total_products = products.get_product_count()
        overflow_count = min(total_products, 6)
        products.add_random_items(count=overflow_count)
        products.verify_badge_count(expected_count=overflow_count)
