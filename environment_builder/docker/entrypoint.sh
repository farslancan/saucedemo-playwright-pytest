#!/bin/bash
set -euo pipefail

cd /app/automation_framework

# Allow passing extra pytest args: `docker run image -k "login"` etc.
exec pytest -c pytest.ini "$@"
