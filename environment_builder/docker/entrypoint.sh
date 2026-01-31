#!/usr/bin/env bash
set -euo pipefail

cd /app

# Allow passing extra pytest args: `docker run image -k "login"` etc.
exec pytest -c automation_framework/pytest.ini "$@"