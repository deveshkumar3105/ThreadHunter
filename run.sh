#!/usr/bin/env bash
# ThreadHunter Startup Script

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

echo "=========================================================="
echo "🛍️  Starting ThreadHunter - AI Clothing Deal Finder"
echo "=========================================================="

# Check if .env exists, if not copy from .env.example
if [ ! -f .env ]; then
  if [ -f .env.example ]; then
    cp .env.example .env
    echo "Created .env from .env.example"
  fi
fi

# Detect Python
PYTHON_BIN="/Library/Frameworks/Python.framework/Versions/3.14/bin/python3"
if [ ! -f "$PYTHON_BIN" ]; then
  PYTHON_BIN=$(which python3)
fi

echo "Using Python: $PYTHON_BIN"
echo "Launching server on http://127.0.0.1:8000 ..."
echo "Press Ctrl+C to stop."
echo "=========================================================="

exec "$PYTHON_BIN" -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
