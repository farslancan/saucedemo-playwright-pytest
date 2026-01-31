import logging
from playwright.sync_api import Page, expect

logger = logging.getLogger(__name__)


DEFAULT_TIMEOUT = 10000
SHORT_WAIT = 500


class BaseHelper:
    """
        Lightweight helper wrapper for common frontend interactions.
        Keeps routine waits and interactions centralized so keyword classes can compose them.
    """
    def __init__(self, page: Page):
        self.page = page

    def click(self, selector: str, timeout: int = DEFAULT_TIMEOUT) -> None:
        logger.info(f"Clicking selector: {selector}", extra={"selector": selector, "timeout": timeout})
        locator = self.page.locator(selector).first
        expect(locator).to_be_visible(timeout=timeout)
        locator.click()
        logger.info(f"Clicked selector: {selector}", extra={"selector": selector})

    def input_text(
        self,
        selector: str,
        value: str,
        *,
        clear: bool = True,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> None:
        preview = (value or "")[:3] + "***" if value else ""
        logger.info(
            f"Inputting text into {selector} | preview={preview or '(empty)'}",
            extra={"selector": selector, "clear": clear, "timeout": timeout, "value_preview": preview},
        )
        locator = self.page.locator(selector).first
        expect(locator).to_be_visible(timeout=timeout)
        if clear:
            try:
                locator.fill("")
            except Exception:
                logger.debug("Clear failed; continuing fill", exc_info=True)
        locator.fill(value or "")
        logger.info(
            f"Input completed for {selector} | preview={preview or '(empty)'}",
            extra={"selector": selector, "value_preview": preview},
        )

    def get_text(self, selector: str, timeout: int = DEFAULT_TIMEOUT) -> str:
        logger.info(f"Getting text from {selector}", extra={"selector": selector, "timeout": timeout})
        locator = self.page.locator(selector).first
        expect(locator).to_be_visible(timeout=timeout)
        text = locator.inner_text().strip()
        logger.info(
            f"Got text from {selector} | len={len(text)} | preview={text[:20]}",
            extra={"selector": selector, "length": len(text), "text_preview": text[:20]},
        )
        return text
