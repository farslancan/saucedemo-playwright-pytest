FROM mcr.microsoft.com/playwright/python:v1.54.0

WORKDIR /app

# Install Python dependencies first for better layer caching
COPY automation_framework/requirements.txt automation_framework/requirements.txt
RUN pip install --no-cache-dir -r automation_framework/requirements.txt \
    && python -m playwright install chromium \
    && pip list

# Install Allure CLI for generating/serving reports inside the container
RUN apt-get update \
    && apt-get install -y --no-install-recommends wget unzip ca-certificates openjdk-17-jre-headless curl \
    && ALLURE_TAG=$(curl -s https://api.github.com/repos/allure-framework/allure2/releases/latest | grep '"tag_name":' | sed -E 's/.*"([^"]+)".*/\1/') \
    && VERSION=${ALLURE_TAG#v} \
    && echo "Downloading Allure release ${ALLURE_TAG} (version ${VERSION})" \
    && wget -qO /tmp/allure.zip "https://github.com/allure-framework/allure2/releases/download/${ALLURE_TAG}/allure-${VERSION}.zip" \
    && unzip -q /tmp/allure.zip -d /opt \
    && ln -s /opt/allure-${VERSION}/bin/allure /usr/local/bin/allure \
    && echo "${VERSION}" > /opt/allure-version \
    && rm -rf /var/lib/apt/lists/* /tmp/allure.zip

# Copy the project
COPY automation_framework ./automation_framework

# Copy entrypoint script
COPY environment_builder/docker/entrypoint.sh /app/entrypoint.sh

# Make entrypoint script executable
RUN chmod +x /app/entrypoint.sh

# Set entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]

# Default to headless in containers
ENV HEADLESS=0
ENV PYTHONPATH=/app

# Ensure Chromium only is used (already set in fixtures)
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
ENV TRACE_DIR=/app

# Do not auto-run tests; keep the container alive for manual runs
CMD ["sleep", "infinity"]