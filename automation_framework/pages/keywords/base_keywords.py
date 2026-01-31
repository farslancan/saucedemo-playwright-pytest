import logging
from typing import Optional
from urllib.parse import urljoin

from playwright.sync_api import Page

from automation_framework.helpers.fe import BaseHelper


logger = logging.getLogger(__name__)


class BaseKeywords(BaseHelper):
    """
        Base keywords for frontend interactions built atop BaseHelper.
    """
    def __init__(self, page: Page):
        super().__init__(page)

    def navigate_to_url(self, url: str, base_url: Optional[str] = None) -> None:
        full_url = urljoin(base_url or self.page.context.base_url or "", url)
        logger.info(f"Navigating to URL: {full_url}")
        self.page.goto(full_url)
