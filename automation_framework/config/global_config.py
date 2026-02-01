import os
from pathlib import Path


# --- Endpoints ---
SAUCE_DEMO_URL = os.environ.get('SAUCE_DEMO_URL', 'https://www.saucedemo.com/')

# --- Credentials ---
STANDART_USERNAME = os.environ.get('STANDART_USERNAME', 'standard_user')
LOCKED_OUT_USERNAME = os.environ.get('LOCKED_OUT_USERNAME', 'locked_out_user')
PROBLEM_USERNAME = os.environ.get('PROBLEM_USERNAME', 'problem_user')
PERFORMANCE_GLITCH_USERNAME = os.environ.get('PERFORMANCE_GLITCH_USERNAME', 'performance_glitch_user')
ERROR_USERNAME = os.environ.get('ERROR_USERNAME', 'error_user')
VISUAL_USERNAME = os.environ.get('VISUAL_USERNAME', 'visual_user')
PASSWORD = os.environ.get('PASSWORD', 'secret_sauce')

# --- UI / Browser ---
HEADLESS = os.environ.get('HEADLESS', 'true')
PW_TRACE = os.environ.get('PW_TRACE', 'on')  # on, off, always, on-failure

# Database properties
DB_HOST = os.environ.get('DB_HOST', '192.168.000.00')
DEV_NODE = os.environ.get('DEV_NODE', 'Test')
DB_PORT = os.environ.get('DB_PORT', '3036')
DB_USERNAME = os.environ.get('DB_USERNAME', 'admin')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'root')

# --- DATA ---
BASE_DIR = Path(__file__).parent.parent  # automation_framework dir
REPO_ROOT = BASE_DIR.parent
DATA_DIR = BASE_DIR / "resources" / "test_data"
RESOURCE_DIR = BASE_DIR / "resources"
REPORTS_DIR = BASE_DIR / "reports"
ALLURE_REPORT_DIR = REPORTS_DIR / "allure-report"
ALLURE_RESULTS_DIR = REPORTS_DIR / "allure-results"
PLAYWRIGHT_TRACES_DIR = REPORTS_DIR / "playwright-traces"
PYTEST_HTML_REPORT_FILE = REPORTS_DIR / "html-report" / "pytest-report.html"
JUNIT_XML_REPORT_FILE = REPORTS_DIR / "junit" / "pytest-junit.xml"
