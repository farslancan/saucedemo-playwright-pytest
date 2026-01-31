from typing import Final

LOGIN_CARD_LOCATOR: Final[str] = ".card-pf"
USERNAME_INPUT: Final[str] = 'input[placeholder*="Username"]'
PASSWORD_INPUT: Final[str] = 'input[placeholder*="Password"]'
LOGIN_BUTTON: Final[str] = 'input[type="submit"]'
ERROR_MESSAGE: Final[str] = "//h3[@data-test='error']"

__all__ = [
    'LOGIN_CARD_LOCATOR',
    'USERNAME_INPUT',
    'PASSWORD_INPUT',
    'LOGIN_BUTTON',
    'ERROR_MESSAGE',
]