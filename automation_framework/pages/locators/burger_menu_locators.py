from typing import Final

BURGER_MENU_BUTTON: Final[str] = "//button[text()='Open Menu']"
BURGER_MENU_ALL_ITEMS: Final[str] = "//a[text()='All Items']"
BURGER_MENU_ABOUT: Final[str] = "//a[text()='About']"
BURGER_MENU_LOGOUT: Final[str] = "//a[text()='Logout']"
BURGER_MENU_RESET: Final[str] = "//a[text()='Reset App State']"
BURGER_MENU_CLOSE: Final[str] = "//button[text()='Close Menu']"

__all__ = [
    "BURGER_MENU_BUTTON",
    "BURGER_MENU_ALL_ITEMS",
    "BURGER_MENU_ABOUT",
    "BURGER_MENU_LOGOUT",
    "BURGER_MENU_RESET",
    "BURGER_MENU_CLOSE",
]
