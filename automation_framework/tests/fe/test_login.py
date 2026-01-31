import csv
import logging
import pytest

from automation_framework.config import global_config as gc
from automation_framework.pages import LoginPage

logger = logging.getLogger(__name__)

DATA_FILE = gc.DATA_DIR / "login_test_data.csv"


def _parse_is_valid(raw_value: str, row_num: int):
    value = raw_value.strip().lower()
    if value in {"", "none"}:
        return None
    if value in {"true", "1", "yes"}:
        return True
    if value in {"false", "0", "no"}:
        return False
    raise ValueError(
        f"Row {row_num}: isValid must be true/false/blank, got '{raw_value}'."
    )


def _load_login_cases():
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Login data file not found: {DATA_FILE}")

    cases = []
    ids = []
    with DATA_FILE.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(
            reader, start=2
        ):  # start=2 for 1-based line number incl. header
            username = (row.get("username") or "").strip()
            password = row.get("password") or ""
            is_valid = _parse_is_valid(row.get("isValid", ""), idx)
            validation_message = (row.get("validationMessage") or "").strip()

            validation = None
            if is_valid is not None:
                validation = {"isValid": is_valid}
                if validation_message:
                    validation["validationMessage"] = validation_message
            if is_valid is False and not validation_message:
                raise ValueError(
                    f"Row {idx}: validationMessage is required when isValid is false."
                )

            label = row.get("id") or f"row{idx-1}"
            cases.append((username, password, validation))
            ids.append(label)
    return cases, ids


_LOGIN_CASES, _LOGIN_CASE_IDS = _load_login_cases()


@pytest.mark.parametrize(
    "username,password,validation", _LOGIN_CASES, ids=_LOGIN_CASE_IDS
)
def test_login_success(page, creds, username, password, validation):
    is_valid = validation.get("isValid") if isinstance(validation, dict) else None
    if is_valid is False:
        resolved_username = username
        resolved_password = password
    else:
        resolved_username = username or creds["username"]
        resolved_password = password or creds["password"]

    LoginPage(page).login(
        creds["base_url"],
        resolved_username,
        resolved_password,
        validation,
    )


def test_something(page, creds):
    logger.info("This is a placeholder test to demonstrate logging.")