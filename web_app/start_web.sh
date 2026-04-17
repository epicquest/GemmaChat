#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/../.venv"   # share venv with the CLI tool

cd "$SCRIPT_DIR"

if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"

echo "Installing / updating dependencies..."
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt

LOG_FILE="$SCRIPT_DIR/gemmachat_web.log"
PID_FILE="$SCRIPT_DIR/gemmachat_web.pid"

# Kill any previously running instance
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if kill -0 "$OLD_PID" 2>/dev/null; then
        echo "Stopping previous instance (PID $OLD_PID)..."
        kill "$OLD_PID"
    fi
    rm -f "$PID_FILE"
fi

echo "Starting GemmaChat web server in background..."
echo "  URL : http://${HOST:-127.0.0.1}:${PORT:-8000}"
echo "  Log : $LOG_FILE"
echo "  PID : $PID_FILE"

nohup python manage.py runserver "${HOST:-127.0.0.1}:${PORT:-8000}" \
    >> "$LOG_FILE" 2>&1 &

echo $! > "$PID_FILE"
echo "Server started with PID $(cat "$PID_FILE")"
