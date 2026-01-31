from typing import Final

# Navigation / layout shared across portal sections
LEFT_NAV_MENU_HEADER: Final[str] = "//header[contains(@class,'SidebarHeader')]"
LOGIN_CARD_LOCATOR: Final[str] = ".card-pf"
SIDEBAR_MENU_LOCATOR: Final[str] = "//span[contains(@class,'SidebarMenuItemTitle')]"
SNA_CARD_LOCATOR: Final[str] = "//h2[normalize-space()='NForce Silent Authentication']"

# Saucedemo login page
USERNAME_INPUT: Final[str] = 'input[placeholder*="Username"]'
PASSWORD_INPUT: Final[str] = 'input[placeholder*="Password"]'
LOGIN_BUTTON: Final[str] = 'input[type="submit"]'
ERROR_MESSAGE: Final[str] = "//h3[@data-test='error']"

# Saucedemo inventory page
APP_LOGO: Final[str] = '//div[@class="app_logo"]'
PRODUCTS_TITLE: Final[str] = "//span[@class='title' and text()='Products']"
INVENTORY_ITEM_NAME: Final[str] = "//div[@class='inventory_item_name ']"
