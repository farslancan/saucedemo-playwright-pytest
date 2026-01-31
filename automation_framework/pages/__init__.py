from importlib import import_module

try:
    from automation_framework.pages.keywords.login_keywords import LoginPage
except Exception as exc:  # pragma: no cover - import guard for editor/runtime without deps
    class LoginPage:  # type: ignore
        def __init__(self, *_, **__):
            raise ImportError(
                "LoginPage could not be imported; ensure dependencies are installed."
            ) from exc

__all__ = ["LoginPage"]
