import logging
import pytest

from automation_framework.pages import BurgerMenuKeywords
from automation_framework.pages import ProductsKeywords

logger = logging.getLogger(__name__)


@pytest.fixture
def products(logged_in_page):
    return ProductsKeywords(logged_in_page)


def test_burger_menu_items_and_actions(logged_in_page, creds):
    burger = BurgerMenuKeywords(logged_in_page)
    burger.open_menu()
    burger.close_menu_and_verify_hidden()
    burger.open_menu()
    burger.assert_menu_items()
    burger.select_all_items_and_verify()
    burger.reset_app_state_and_verify()
    burger.open_about_in_new_tab_and_verify()
    burger.logout_and_verify()


def test_burger_menu_from_cart_checkout(products):
    products.add_random_items(count=1)
    products.verify_badge_count(expected_count=1)
    products.open_cart()
    menu = BurgerMenuKeywords(products.page)
    menu.open_menu()
    menu.assert_menu_items()
    menu.close_menu_and_verify_hidden()
    products.return_to_inventory_from_cart()
    products.assert_inventory_loaded()


def test_reset_app_state_clears_cart(products, logged_in_page):
    products.add_random_items(count=2)
    products.verify_badge_count(expected_count=2)
    menu = BurgerMenuKeywords(logged_in_page)
    menu.open_menu()
    menu.reset_app_state_and_verify()
    products.verify_badge_count(expected_count=0)
