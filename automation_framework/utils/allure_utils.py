# python
import json
from typing import Any, Dict, Optional

import allure
from allure_commons.types import AttachmentType


def attach_json(data: Any, name: str = "data") -> None:
    try:
        payload = json.dumps(data, indent=2, ensure_ascii=False)
    except Exception:
        payload = str(data)
    allure.attach(payload, name=name, attachment_type=AttachmentType.JSON)


def attach_text(text: str, name: str = "text") -> None:
    allure.attach(text, name=name, attachment_type=AttachmentType.TEXT)


def attach_response(resp, name: str = "response") -> None:
    try:
        meta = {
            "status_code": resp.status_code,
            "url": getattr(resp.request, "url", ""),
            "method": getattr(resp.request, "method", ""),
            "headers": dict(resp.headers or {}),
        }
        attach_json(meta, name=f"{name}_meta")
    except Exception:
        pass

    # Attach body as JSON if possible, otherwise text
    try:
        body = resp.json()
        attach_json(body, name=f"{name}_body")
    except Exception:
        try:
            attach_text(resp.text, name=f"{name}_body_raw")
        except Exception:
            pass


def attach_request(
    method: str, url: str, headers: Optional[Dict[str, str]] = None, body: Any = None
) -> None:
    allure.attach(
        json.dumps(
            {"method": method, "url": url, "headers": headers or {}, "body": body},
            indent=2,
            ensure_ascii=False,
        ),
        name="request",
        attachment_type=AttachmentType.JSON,
    )


def attach_screenshot_bytes(png_bytes: bytes, name: str = "screenshot") -> None:
    allure.attach(png_bytes, name=name, attachment_type=AttachmentType.PNG)
