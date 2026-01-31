# python
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Optional, Tuple

from playwright.sync_api import Browser, BrowserContext, Page, sync_playwright

from automation_framework.config import global_config as gc


def _resolve_headless_flag() -> bool:
    """Convert HEADLESS env/config flag to a boolean."""
    value = gc.HEADLESS
    if isinstance(value, str):
        return value.lower() in {"1", "true", "yes", "on"}
    return bool(value)


def _get_browser_type(pw, browser_type: str):
    kind = (browser_type or "chromium").lower()
    if kind not in {"chromium", "firefox", "webkit"}:
        raise ValueError(
            "Unsupported browser type; choose chromium, firefox, or webkit."
        )
    return getattr(pw, kind)


@contextmanager
def open_browser(
    url: str,
    *,
    browser_type: str = "chromium",
    download_dir: Optional[str] = None,
) -> Iterator[Tuple[BrowserContext, Page, Optional[Browser]]]:
    """
    Launch a Playwright browser, navigate to the given URL, and yield context/page/browser.

    Example:
        with open_browser("https://example.com") as (context, page, browser):
            page.click("text=Login")
    """
    headless = _resolve_headless_flag()
    download_path = Path(download_dir).expanduser().resolve() if download_dir else None

    with sync_playwright() as pw:
        browser_kind = _get_browser_type(pw, browser_type)

        launch_kwargs = {"headless": headless, "args": ["--start-maximized"]}
        context_kwargs = {"accept_downloads": bool(download_path)}
        if headless:
            context_kwargs["viewport"] = {"width": 1920, "height": 1080}
        else:
            # viewport=None keeps the browser window size when not running headless
            context_kwargs["viewport"] = None

        browser: Optional[Browser] = None
        if download_path:
            download_path.mkdir(parents=True, exist_ok=True)
            context = browser_kind.launch_persistent_context(
                user_data_dir=str(download_path / "user-data"),
                downloads_path=str(download_path),
                **launch_kwargs,
                **context_kwargs,
            )
        else:
            browser = browser_kind.launch(**launch_kwargs)
            context = browser.new_context(**context_kwargs)

        page = context.new_page()
        page.goto(url)

        try:
            yield context, page, browser
        finally:
            try:
                context.close()
            finally:
                if browser:
                    browser.close()
