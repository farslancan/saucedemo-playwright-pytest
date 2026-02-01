# python
import json
import logging
import os
import pathlib
import re
import sys
import time
from datetime import datetime
from pathlib import Path

import allure
import pytest
import requests
from allure_commons.types import AttachmentType
from playwright.sync_api import sync_playwright
from automation_framework.config import global_config as gc
from automation_framework.pages import LoginPage
from automation_framework.pages import BurgerMenuKeywords
from automation_framework.pages.locators import burger_menu_locators as burger_locators

# Ensure repo root is on PYTHONPATH when tests are run from inside automation_framework
ROOT_DIR = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


HTTP_LOGGER = logging.getLogger("automation_framework.http")
_SENSITIVE_HEADER_KEYS = {"authorization", "proxy-authorization"}
_MAX_LOG_BODY_CHARS = int(os.getenv("HTTP_LOG_MAX_BODY", "2000"))


def _ensure_dir(path: pathlib.Path) -> pathlib.Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def _bool_str(value) -> bool:
    return str(value).lower() in {"1", "true", "yes", "on"}


def _resolve_report_path(
    config, attr_name: str, default_path: pathlib.Path
) -> pathlib.Path:
    raw_value = getattr(config.option, attr_name, None)
    path = pathlib.Path(raw_value) if raw_value else pathlib.Path(default_path)
    target_dir = path if path.suffix == "" else path.parent
    _ensure_dir(target_dir)
    setattr(config.option, attr_name, str(path))
    return path


def _get_playwright_traces_dir(config) -> pathlib.Path:
    configured = getattr(config, "_playwright_traces_dir", None)
    traces_dir = (
        pathlib.Path(configured)
        if configured
        else pathlib.Path(gc.PLAYWRIGHT_TRACES_DIR)
    )
    return _ensure_dir(traces_dir)


def _scrub_headers(headers):
    if not headers:
        return {}
    sanitized = {}
    for key, value in headers.items():
        if key.lower() in _SENSITIVE_HEADER_KEYS:
            sanitized[key] = "***"
        else:
            sanitized[key] = value
    return sanitized



class LoggingSession(requests.Session):
    def __init__(self):
        super().__init__()


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    _ensure_dir(pathlib.Path(gc.REPORTS_DIR))

    # Ensure report destinations are derived from global_config by default
    allure_results_dir = _resolve_report_path(
        config, "allure_report_dir", pathlib.Path(gc.ALLURE_RESULTS_DIR)
    )
    config._allure_results_dir = allure_results_dir

    html_report_file = _resolve_report_path(
        config, "htmlpath", pathlib.Path(gc.PYTEST_HTML_REPORT_FILE)
    )
    config._html_report_file = html_report_file

    junit_attr = "xmlpath" if hasattr(config.option, "xmlpath") else "junitxml"
    junit_report_file = _resolve_report_path(
        config, junit_attr, pathlib.Path(gc.JUNIT_XML_REPORT_FILE)
    )
    # Persist to both possible option names so downstream hooks see the value
    config.option.xmlpath = str(junit_report_file)
    config.option.junitxml = str(junit_report_file)
    config._junit_report_file = junit_report_file

    config._playwright_traces_dir = _ensure_dir(pathlib.Path(gc.PLAYWRIGHT_TRACES_DIR))
    _ensure_dir(pathlib.Path(gc.ALLURE_REPORT_DIR))

    if not HTTP_LOGGER.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
        )
        HTTP_LOGGER.addHandler(handler)
    HTTP_LOGGER.setLevel(logging.INFO)
    HTTP_LOGGER.propagate = False

    # Write Allure environment.properties for better context in reports
    env_props = {
        "HAUD_BASE_URL": gc.SAUCE_DEMO_URL.rstrip("/"),
        "HEADLESS": _bool_str(gc.HEADLESS),
        "PYTEST_ADDOPTS": os.environ.get("PYTEST_ADDOPTS", ""),
    }
    lines = [f"{k}={v}" for k, v in env_props.items()]
    (allure_results_dir / "environment.properties").write_text(
        "\n".join(lines), encoding="utf-8"
    )


@pytest.fixture(scope="session")
def creds():
    base_url = gc.SAUCE_DEMO_URL
    username = gc.STANDART_USERNAME
    password = gc.PASSWORD

    missing = [k for k, v in {"PASSWORD": password}.items() if not v]
    if missing:
        raise RuntimeError(
            f"Missing required environment variable(s): {', '.join(missing)}"
        )

    return {"base_url": base_url, "username": username, "password": password}


@pytest.fixture(scope="session")
def pw():
    with sync_playwright() as p:
        yield p


@pytest.fixture(scope="session")
def browser(pw):
    # Default to headful; set HEADLESS=1 to run headless in CI.
    # headless = os.environ.get("HEADLESS", "").lower() in {"1", "true", "yes", "on"}
    headless = _bool_str(gc.HEADLESS)
    browser = pw.chromium.launch(headless=headless, args=["--start-maximized"])
    yield browser
    browser.close()


@pytest.fixture(scope="session")
def ui_context(browser):
    # headless = os.environ.get("HEADLESS", "").lower() in {"1", "true", "yes", "on"}
    headless = _bool_str(gc.HEADLESS)
    if headless:
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
    else:
        context = browser.new_context(no_viewport=True)

    keep_mode = gc.PW_TRACE.lower()
    keep_always = keep_mode in {"on", "all", "always"}
    keep_on_fail = keep_mode in {"on-failure", "fail", "failed"}

    if keep_always or keep_on_fail:
        try:
            context.tracing.start(screenshots=True, snapshots=True, sources=True)
        except Exception:
            keep_always = False
            keep_on_fail = False

    context._trace_settings = {
        "keep_mode": keep_mode,
        "keep_always": keep_always,
        "keep_on_fail": keep_on_fail,
    }

    yield context

    if keep_always or keep_on_fail:
        try:
            context.tracing.stop()
        except Exception:
            pass
    context.close()


@pytest.fixture()
def page(ui_context, request):
    context = ui_context
    settings = getattr(context, "_trace_settings", {})
    keep_mode = settings.get("keep_mode", "off")
    keep_always = settings.get("keep_always", False)
    keep_on_fail = settings.get("keep_on_fail", False)
    record_traces = keep_always or keep_on_fail

    if record_traces:
        try:
            context.tracing.start_chunk()
        except Exception:
            record_traces = False

    page = context.new_page()
    request.node._trace_path = None
    request.node._trace_context = context

    yield page

    failed = bool(
        getattr(request.node, "rep_call", None) and request.node.rep_call.failed
    )

    if record_traces:
        start = time.perf_counter()
        if keep_always or (keep_on_fail and failed):
            traces_dir = _get_playwright_traces_dir(request.config)
            # traces_dir = os.getenv("TRACE_DIR", gc.PLAYWRIGHT_TRACES_DIR)
            nodeid = request.node.nodeid
            safe_name = re.sub(r"[^A-Za-z0-9_.\-]", "_", nodeid)
            trace_path = traces_dir / f"{safe_name}.zip"
            request.node._trace_path = trace_path
            try:
                context.tracing.stop_chunk(path=str(trace_path))
            except Exception:
                trace_path = None
            else:
                if trace_path and failed:
                    try:
                        allure.attach.file(
                            str(trace_path), name="playwright-trace", extension="zip"
                        )
                    except Exception:
                        pass
        else:
            try:
                context.tracing.stop_chunk()
            except Exception:
                pass
        stop_trace_duration = time.perf_counter() - start
        print(
            f"[teardown] tracing stop took {stop_trace_duration:.2f}s for {request.node.nodeid}"
        )
    else:
        stop_trace_duration = 0.0

    page_close_start = time.perf_counter()
    try:
        page.close()
    except Exception:
        pass
    page_close_duration = time.perf_counter() - page_close_start
    print(
        f"[teardown] page.close took {page_close_duration:.2f}s for {request.node.nodeid}"
    )


@pytest.fixture(autouse=True)
def per_test_file_logger(request):
    """Create a log file per test under reports/logs/<suitename>/<testname>.log; overwrite on reruns of the same nodeid."""
    base_logs_dir = _ensure_dir(pathlib.Path(gc.REPORTS_DIR) / "logs")
    suite_name = request.module.__name__.replace('test_', '')
    test_name = re.sub(r"[^A-Za-z0-9_.\-]", "_", getattr(request.node, "originalname", request.node.name))
    suite_dir = _ensure_dir(base_logs_dir / suite_name)
    log_file = suite_dir / f"{test_name}.log"

    handler = logging.FileHandler(log_file, mode="w", encoding="utf-8")
    handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    )

    root_logger = logging.getLogger()
    root_logger.addHandler(handler)

    yield

    root_logger.removeHandler(handler)
    handler.close()


def _attach_ui_artifacts_when_failed(item, report):
    try:
        page = item.funcargs.get("page")
    except Exception:
        page = None

    if page is None:
        return

    # Attach current URL
    try:
        allure.attach(
            str(page.url), name="page_url", attachment_type=AttachmentType.TEXT
        )
    except Exception:
        pass

    # Attach screenshot
    try:
        png = page.screenshot(full_page=True)
        allure.attach(png, name="screenshot", attachment_type=AttachmentType.PNG)
    except Exception:
        pass

    # Attach page content (can be large; keep as text)
    try:
        html = page.content()
        allure.attach(html, name="page_source", attachment_type=AttachmentType.HTML)
    except Exception:
        pass


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    # Run all other hooks to obtain the report object
    outcome = yield
    report = outcome.get_result()

    # Only on test call phase failures
    if report.when == "call":
        # store for fixtures to decide about artifacts
        setattr(item, "rep_call", report)

        if report.failed:
            # Attach UI artifacts for UI tests
            _attach_ui_artifacts_when_failed(item, report)

            # Attach captured stdout/stderr for any failed test
            if hasattr(report, "sections"):
                for section_name, content in report.sections:
                    if "Captured stdout" in section_name and content:
                        allure.attach(
                            content,
                            name=f"{section_name.replace(' ', '_').lower()}",
                            attachment_type=AttachmentType.TEXT,
                            extension="txt",
                        )
                    if "Captured stderr" in section_name and content:
                        allure.attach(
                            content,
                            name=f"{section_name.replace(' ', '_').lower()}",
                            attachment_type=AttachmentType.TEXT,
                            extension="txt",
                        )
            # Also attach the longrepr (traceback + captured output) as a general log
            if report.longrepr:
                allure.attach(
                    str(report.longrepr),
                    name="full_test_log_and_traceback",
                    attachment_type=AttachmentType.TEXT,
                    extension="txt",
                )


def pytest_sessionfinish(session, exitstatus):
    results_dir = pathlib.Path(gc.ALLURE_RESULTS_DIR).resolve()
    report_hint = f"Allure results saved to: {results_dir}\nGenerate report: allure serve {results_dir}"
    print(report_hint)
    try:
        logging.getLogger(__name__).info(report_hint)
    except Exception:
        pass

    # Auto-generate Allure report
    import subprocess
    try:
        subprocess.run([
            "allure", "generate", str(results_dir), "-o", gc.ALLURE_REPORT_DIR, "--clean"
        ], check=True)
        report_dir = pathlib.Path(gc.ALLURE_REPORT_DIR).resolve()
        print(f"Allure report generated at: {report_dir}")
        print(f"Open report: allure open {report_dir}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to generate Allure report: {e}")
    except FileNotFoundError:
        print("Allure CLI not found. Install Allure to generate reports automatically.")


@pytest.fixture(scope="session")
def auth_storage_state(tmp_path_factory, browser, creds):
    """Log in once and persist storage state for reuse in logged_in_page."""
    state_path = Path(tmp_path_factory.mktemp("auth")) / "state.json"
    headless = _bool_str(gc.HEADLESS)
    context = (
        browser.new_context(no_viewport=True)
        if not headless
        else browser.new_context(viewport={"width": 1920, "height": 1080})
    )
    page = context.new_page()
    LoginPage(page).login(
        creds["base_url"],
        creds["username"],
        creds["password"],
        {"isValid": True},
    )
    context.storage_state(path=str(state_path))
    context.close()
    return str(state_path)


@pytest.fixture()
def logged_in_page(browser, auth_storage_state):
    """Yields a page already authenticated via stored session state."""
    headless = _bool_str(gc.HEADLESS)
    context = (
        browser.new_context(storage_state=auth_storage_state, no_viewport=True)
        if not headless
        else browser.new_context(
            storage_state=auth_storage_state, viewport={"width": 1920, "height": 1080}
        )
    )
    context.base_url = "https://www.saucedemo.com"  # Add base_url attribute to context
    page = context.new_page()
    page.goto("https://www.saucedemo.com/inventory.html", wait_until="networkidle")
    yield page
    context.close()


@pytest.fixture(autouse=True)
def reset_after_test(logged_in_page):
    yield
    # Reset app state after each test, only if on a page with burger menu
    menu = BurgerMenuKeywords(logged_in_page)
    if menu.page.locator(burger_locators.BURGER_MENU).is_visible():
        menu.page.wait_for_load_state("networkidle")
        # Close menu if already open
        if menu.page.locator(burger_locators.BURGER_MENU_CLOSE).is_visible():
            menu.close_menu_and_verify_hidden()
        menu.open_menu()
        menu.reset_app_state_and_verify()
