# SauceDemo Automation Framework

## Project Overview

This project is an end-to-end automation framework for testing the SauceDemo e-commerce web application (https://www.saucedemo.com/). It focuses on frontend (FE) UI testing using Playwright, with support for API testing. The framework ensures reliable, maintainable, and scalable test automation through Docker containerization and CI/CD integration.

### Key Features
- **UI Testing**: Automated browser interactions for login, product selection, cart management, and checkout.
- **Reporting**: Comprehensive Allure reports with screenshots, traces, and logs.
- **Containerization**: Docker-based execution for consistent environments.
- **CI/CD**: Automated testing on GitHub Actions for every push/PR.
- **Multi-Environment Support**: Configurable via environment variables for different setups.

### Project Structure (Visual Overview)
```
saucedemo/
├── .github/workflows/          # CI/CD pipelines (GitHub Actions)
├── automation_framework/       # Main framework code
│   ├── config/                 # Global configuration (URLs, credentials)
│   ├── helpers/                # Utility helpers (API, FE)
│   ├── pages/                  # Page Object Model classes
│   │   ├── keywords/           # Action keywords for pages
│   │   └── locators/           # Element locators
│   ├── reports/                # Generated reports (Allure, HTML, traces)
│   ├── resources/              # Test data and assets
│   ├── tests/                  # Test suites (FE, API)
│   ├── utils/                  # Utilities (Allure utils, browser setup)
│   ├── conftest.py             # Pytest fixtures and setup
│   ├── pytest.ini              # Pytest configuration
│   └── requirements.txt        # Python dependencies
├── environment_builder/        # Docker setup
│   ├── Dockerfile              # Container image definition
│   ├── docker-compose.yml      # Container orchestration
│   ├── .env                    # Environment variables (example)
│   └── docker/entrypoint.sh    # Container entrypoint script
├── .gitignore                  # Git ignore rules
├── README.md                   # This documentation
└── .env                        # Local environment variables (not committed)
```

### Architecture Overview
- **Layered Architecture**: Separation of concerns with config, helpers, pages, and tests.
- **Page Object Model (POM)**: Encapsulates page elements and actions for maintainability.
- **Keyword-Driven Testing**: Reusable keywords for common actions.
- **Fixture-Based Setup**: Pytest fixtures for browser and data management.
- **Containerized Execution**: Docker ensures isolation and reproducibility.

### Dependencies
The framework relies on the following key dependencies (see `automation_framework/requirements.txt` for full list):
- **pytest**: Testing framework for running and organizing tests.
- **playwright**: Browser automation library for UI interactions.
- **pytest-playwright**: Integration for Playwright with Pytest.
- **allure-pytest**: Advanced reporting with Allure.
- **requests**: HTTP library for API testing (if implemented).
- **PyMySQL**: Database interactions (configured but not used in FE tests).
- **tenacity**: Retry mechanisms for flaky operations.
- **black & ruff**: Code formatting and linting.

### Configuration
Configuration is managed via environment variables for flexibility across environments:
- **Global Config** (`automation_framework/config/global_config.py`): Loads env vars with defaults.
- **Key Variables**:
  - `SAUCE_DEMO_URL`: Base URL for the application.
  - `USERNAME`/`PASSWORD`: Login credentials.
  - `HEADLESS`: Run browser in headless mode (true for CI).
  - `PW_TRACE`: Playwright trace level (on-failure, on, off).
- **.env File**: Local overrides (not committed to Git).
- **Docker Config**: Passed via `docker-compose.yml` and `.env`.

### Test Architecture
- **Test Structure**:
  - `tests/fe/`: Frontend UI tests (login, cart, checkout).
  - `tests/api/`: Placeholder for API tests (empty currently).
- **Fixtures** (`conftest.py`): Browser setup, page initialization, data loading.
- **Page Objects** (`pages/`): Classes for each page (LoginPage, InventoryPage) with locators and keywords.
- **Keywords** (`pages/keywords/`): Action methods (login, add_to_cart).
- **Locators** (`pages/locators/`): Element selectors (XPath, CSS).
- **Data Management**: Test data in `resources/test_data/`, loaded via utils.
- **Execution Flow**: Pytest collects tests → Fixtures set up browser → Keywords perform actions → Assertions validate → Reports generated.
- **Logging Mechanism**:
  - Uses Python's built-in `logging` module with custom configuration.
  - Logs are captured at DEBUG, INFO, WARNING, ERROR levels.
  - Suite-specific logs: Each test suite (e.g., authentication, cart) has dedicated loggers for categorization.
  - Case-specific logs: Individual test cases log steps, actions, and assertions for traceability.
  - Log renewal: Logs are refreshed per test run; old logs are overwritten to avoid accumulation.
  - Integration: Logs are attached to Allure reports and console output for real-time monitoring.

### Design Patterns
- **Page Object Model (POM)**: Each page has a class with elements and methods, reducing code duplication.
- **Factory Pattern**: Fixtures create browser instances dynamically.
- **Singleton Pattern**: Global config ensures single source of truth.
- **Keyword-Driven**: Reusable action keywords for test steps.
- **Data-Driven**: Parameterized tests for multiple scenarios (e.g., different users).
- **Decorator Pattern**: Allure annotations for reporting enhancements.

## Allure Reporting

- Results are written to `automation_framework/reports/allure-results` (default set in `global_config` and enforced in `conftest.py`).
- UI test failures automatically attach screenshot, page source, and current URL to Allure.
- All report artifacts live under `automation_framework/reports` (Allure results/report, Playwright traces, HTML report, JUnit XML).

### Prerequisites

- Python deps: `pip install -r automation_framework/requirements.txt`
- Playwright Chromium runtime: `python -m playwright install chromium`
- Allure CLI (for viewing reports):
  - Windows (Chocolatey): `choco install allure`
  - Windows (Scoop): `scoop install allure`
  - macOS (Homebrew): `brew install allure`
  - Linux: download from https://github.com/allure-framework/allure2/releases/latest | sed -E 's/.*"([^"]+)".*/\1/') \
  - Manual: Download from https://github.com/allure-framework/allure2/releases and add to PATH
 
### Run Tests (with Allure output)

- `pytest -c automation_framework/pytest.ini`
  - Overrides: `pytest -c automation_framework/pytest.ini --alluredir=automation_framework/reports/allure-results`

### HTML Report (auto-generated)

- Each test run also produces an HTML report via pytest-html at `automation_framework/reports/pytest-report.html`.
- The report is self-contained; open it directly in a browser.

## Assumptions and Limitations

### Assumptions:
- **Browser and Environment**: Tests run on Chrome/Chromium-based Playwright. Other browsers are not supported.
- **Data Persistence**: SauceDemo application does not persist data across sessions; tests run in isolation.
- **User Roles**: Only `standard_user` and `error_user` are tested; other roles (e.g., `locked_out_user`) are out of scope.
- **Network Stability**: Network connection is assumed stable; slow connections are not tested.
- **Screen Resolution**: Tests run at 1920x1080 resolution; mobile compatibility is not tested.
- **Execution Environment**: Tests can run locally, in Docker containers, or via CI/CD pipelines for consistency.

### Limitations:
- **Performance Testing**: No load testing or performance measurement; only functional tests.
- **Cross-Browser**: Only Chromium is supported; Firefox/Safari are not tested.
- **API Testing**: Only UI testing; backend APIs are not tested (though framework supports API tests).
- **Data Variability**: Random data reduces predictability; fixed data usage is limited.
- **CI/CD Integration**: Automated via GitHub Actions for seamless execution on push/PR.
- **Error Handling**: Network errors or application crashes are out of scope.
- **Scalability**: Large datasets or parallel tests are limited; 10+ parallel tests not recommended.

## Run In IDE

### VS Code

- Install the Python extension (ms-python.python).
- Optional: install Black formatter extension (ms-python.black-formatter) for best results.
- Create a `.env` in the repo root with required variables (example):
  - `USERNAME=standard_user`
  - `PASSWORD=secret_sauce`
  
- Add `.vscode/settings.json` (or update) so VS Code uses the project config and env file:
  - `{
      "python.testing.pytestEnabled": true,
      "python.testing.pytestArgs": ["-c", "automation_framework/pytest.ini"],
      "python.envFile": "${workspaceFolder}/.env",
      "editor.formatOnSave": true,
      "[python]": { "editor.defaultFormatter": "ms-python.black-formatter" }
    }`
- Open the Testing sidebar to run all tests, a single file, or an individual test. Use "Debug Test" to debug.

  - The HTML report is written to `automation_framework/reports/pytest-report.html` when running from the IDE.

### PyCharm

- Create a new Run/Debug Configuration of type “pytest”.
- Set fields:
  - Working directory: project root
  - Target: `automation_framework/tests`
  - Additional args: `-c automation_framework/pytest.ini`
  - Environment: add `USERNAME`, `PASSWORD`, etc.
- Run or debug the configuration; Allure results go to `automation_framework/reports/allure-results/`.
  - The HTML report is written to `automation_framework/reports/pytest-report.html`.

## Auto-Formatting

- Command line (one-time): `pip install -r requirements-dev.txt`
- Format all files: `black . && isort .`
- Git pre-commit hooks:
  - Install: `pre-commit install`
  - Run on all files once: `pre-commit run -a`
- VS Code: formatting on save is enabled via `.vscode/settings.json` and uses Black; imports are organized with isort profile Black.

Notes

- Ensure dependencies and Playwright Chromium are installed (see Prerequisites).
- UI tests: set `HEADLESS=1` for CI/stability; unset or `HEADLESS=0` to watch the browser while debugging.

### Generate and View Allure Report

- Quick serve: `allure serve automation_framework/reports/allure-results`
- Or generate then open:
  - `allure generate automation_framework/reports/allure-results -o automation_framework/reports/allure-report --clean`
  - `allure open automation_framework/reports/allure-report`

### Playwright Traces (Frontend)

- Traces are recorded per test and saved under `automation_framework/reports/playwright-traces/`.
- Default behavior keeps traces on failures only. Control via `PW_TRACE` env:
  - `PW_TRACE=on-failure` (default)
  - `PW_TRACE=on` (keep for all tests)
  - `PW_TRACE=off` (don’t keep)
- View a trace locally:
  - `python -m playwright show-trace automation_framework/reports/playwright-traces/<test_name>.zip`

### Browser Choice

- Only Chromium is used for UI tests. No Firefox/WebKit setup required.

### Environment Notes

- `HEADLESS=1` to run Playwright headless.
- `automation_framework/reports/allure-results/environment.properties` is auto-generated with key runtime details.

## Docker: Run Tests In Container (Automated)

### Prerequisites

- Docker Desktop (Windows/macOS) or Docker Engine (Linux)

### Run Tests with Docker Compose

- Navigate to `environment_builder` directory:
  - `cd environment_builder`
- Create a `.env` file with your credentials (example provided in the directory):
  - `SAUCE_DEMO_URL=https://www.saucedemo.com/`
  - `USERNAME=standard_user`
  - `PASSWORD=secret_sauce`
  - Other variables as needed
- Run tests:
  - `docker-compose up --build`
- This builds the image, starts the container, and automatically runs the FE test suite.
- Reports are saved to `automation_framework/reports` on your host via volume mounts.

### Viewing Reports After Docker Run

- Allure: `allure serve automation_framework/reports/allure-results`
- HTML Report: Open `automation_framework/reports/html-report/pytest-report.html` in a browser.
- Playwright Traces: `python -m playwright show-trace automation_framework/reports/playwright-traces/<trace_file>.zip`

### Notes

- The container runs tests in headless mode for stability.
- Configuration is passed via environment variables in `.env` and `docker-compose.yml`.
- If you need to run API tests instead, change `command: ["tests/fe"]` to `command: ["tests/api"]` in `docker-compose.yml`.

## CI/CD Pipeline

A GitHub Actions workflow is set up in `.github/workflows/ci.yml` to run tests automatically on push or pull request to any branch.

### What it does:
- Checks out the code.
- Sets up Docker.
- Creates a `.env` file with default credentials.
- Runs `docker-compose up --build` to execute FE tests.
- Uploads test artifacts (Allure results, HTML reports, Playwright traces, logs) for review.

### Viewing CI Results:
- Go to the Actions tab in your GitHub repository.
- Click on the latest workflow run.
- Download artifacts from the "Artifacts" section.
- Serve Allure report locally: `allure serve <downloaded-allure-results-folder>`.
