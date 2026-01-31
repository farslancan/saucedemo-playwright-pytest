from typing import Final

# Inventory page header
APP_LOGO: Final[str] = '//div[@class="app_logo"]'
PRODUCTS_TITLE: Final[str] = "//span[@class='title' and text()='Products']"

# Product cards
PRODUCT_CARD: Final[str] = "//div[@class='inventory_item']"
PRODUCT_NAME: Final[str] = "//div[@class='inventory_item_name ']"
INVENTORY_ITEM_NAME: Final[str] = PRODUCT_NAME
PRODUCT_DESC: Final[str] = "//div[@class='inventory_item_desc']"
PRODUCT_PRICE: Final[str] = "//div[@class='inventory_item_price']"
PRODUCT_IMG: Final[str] = "//img[@class='inventory_item_img']"
ADD_TO_CART_BTN: Final[str] = "//button[contains(@data-test,'add-to-cart')]"
REMOVE_BTN: Final[str] = "//button[contains(@data-test,'remove')]"

# Sorting
SORT_CONTAINER: Final[str] = "//span[@class='select_container']"
SORT_SELECT: Final[str] = "//select[contains(@class,'product_sort_container')]"
SORT_ACTIVE_OPTION: Final[str] = "//span[@data-test='active-option']"
SORT_OPTION_AZ: Final[str] = "//option[@value='az']"
SORT_OPTION_ZA: Final[str] = "//option[@value='za']"
SORT_OPTION_LOHI: Final[str] = "//option[@value='lohi']"
SORT_OPTION_HILO: Final[str] = "//option[@value='hilo']"

# Cart badge and link
CART_BADGE: Final[str] = "//span[@class='shopping_cart_badge']"
CART_LINK: Final[str] = "//a[@class='shopping_cart_link']"

# Cart page
CART_ITEM: Final[str] = "//div[contains(@class,'cart_item')]"
CART_ITEM_NAME: Final[str] = "//div[contains(@class,'cart_item')]//div[contains(@class,'inventory_item_name')]"
CART_ITEM_DESC: Final[str] = "//div[contains(@class,'cart_item')]//div[contains(@class,'inventory_item_desc')]"
CART_ITEM_PRICE: Final[str] = "//div[contains(@class,'cart_item')]//div[contains(@class,'inventory_item_price')]"
CART_REMOVE_BTN: Final[str] = "//div[contains(@class,'cart_item')]//button[contains(@data-test,'remove')]"
CART_CONTINUE_BTN: Final[str] = "//button[@data-test='continue-shopping']"

# Product detail page
PRODUCT_DETAIL_NAME: Final[str] = "//div[@data-test='inventory-item-name']"
PRODUCT_DETAIL_DESC: Final[str] = "//div[@data-test='inventory-item-desc']"
PRODUCT_DETAIL_PRICE: Final[str] = "//div[@data-test='inventory-item-price']"
PRODUCT_DETAIL_IMG: Final[str] = "//img[contains(@class,'inventory_details_img')]"
PRODUCT_DETAIL_BACK_BTN: Final[str] = "//button[@data-test='back-to-products']"

__all__ = [
    'APP_LOGO',
    'PRODUCTS_TITLE',
    'PRODUCT_CARD',
    'PRODUCT_NAME',
    'INVENTORY_ITEM_NAME',
    'PRODUCT_DESC',
    'PRODUCT_PRICE',
    'PRODUCT_IMG',
    'ADD_TO_CART_BTN',
    'REMOVE_BTN',
    'SORT_CONTAINER',
    'SORT_SELECT',
    'SORT_ACTIVE_OPTION',
    'SORT_OPTION_AZ',
    'SORT_OPTION_ZA',
    'SORT_OPTION_LOHI',
    'SORT_OPTION_HILO',
    'CART_BADGE',
    'CART_LINK',
    'CART_ITEM',
    'CART_ITEM_NAME',
    'CART_ITEM_DESC',
    'CART_ITEM_PRICE',
    'CART_REMOVE_BTN',
    'CART_CONTINUE_BTN',
    'PRODUCT_DETAIL_NAME',
    'PRODUCT_DETAIL_DESC',
    'PRODUCT_DETAIL_PRICE',
    'PRODUCT_DETAIL_IMG',
    'PRODUCT_DETAIL_BACK_BTN',
]
