from importlib import import_module

try:
    from automation_framework.pages.keywords.login_keywords import LoginPage
    from automation_framework.pages.keywords.burger_menu_keywords import BurgerMenuKeywords
    from automation_framework.pages.keywords.products_keywords import ProductsKeywords
    from automation_framework.pages.keywords.cart_and_checkout_keywords import CartKeywords
except Exception as exc:  # pragma: no cover - import guard for editor/runtime without deps
    class LoginPage:  # type: ignore
        def __init__(self, *_, **__):
            raise ImportError(
                "LoginPage could not be imported; ensure dependencies are installed."
            ) from exc
    class BurgerMenuKeywords:  # type: ignore
        def __init__(self, *_, **__):
            raise ImportError(
                "BurgerMenuKeywords could not be imported; ensure dependencies are installed."
            ) from exc
    class ProductsKeywords:  # type: ignore
        def __init__(self, *_, **__):
            raise ImportError(
                "ProductsKeywords could not be imported; ensure dependencies are installed."
            ) from exc
    class CartKeywords:  # type: ignore
        def __init__(self, *_, **__):
            raise ImportError(
                "CartKeywords could not be imported; ensure dependencies are installed."
            ) from exc

__all__ = ["LoginPage", "BurgerMenuKeywords", "ProductsKeywords", "CartKeywords"]

