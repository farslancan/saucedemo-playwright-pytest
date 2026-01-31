import pytest

from automation_framework.pages import ProductsKeywords
from automation_framework.pages import CartKeywords


@pytest.fixture
def card(logged_in_page):
    return CartKeywords(logged_in_page)


@pytest.mark.smoke
@pytest.mark.products
@pytest.mark.usefixtures("logged_in_page")
class TestCardPage:

    def test_navigate_card_verify_default(self, card):
        card.navigate_to_cart()