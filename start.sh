#!/bin/bash
# ============================================================
#  Housing Market News Bot — Linux / macOS Launcher
#  Usage: bash start.sh
# ============================================================
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
VENV_DIR="$SCRIPT_DIR/venv"

PYTHON=""
for cmd in python3 python; do
    if command -v "$cmd" &>/dev/null; then PYTHON="$cmd"; break; fi
done
[ -z "$PYTHON" ] && echo "ERROR: Python not found." && exit 1

echo "============================================"
echo "  Housing Market News Bot"
echo "  Python : $($PYTHON --version)"
echo "  Folder : $SCRIPT_DIR"
echo "============================================"
echo ""

if [ ! -d "$VENV_DIR" ]; then
    echo "[1/4] Creating virtual environment..."
    $PYTHON -m venv "$VENV_DIR"
else
    echo "[1/4] Virtual environment found"
fi

echo "[2/4] Activating..."
source "$VENV_DIR/bin/activate"

echo "[3/4] Installing dependencies..."
pip install -q -r requirements.txt
echo "      OK"

echo "[4/4] Setting up directories..."
mkdir -p logs
echo "      OK"

echo ""
echo "  Outputs:"
echo "    housing_news.db    — SQLite database"
echo "    housing_news.csv   — CSV flat file"
echo "    logs/              — Rotating log files"
echo ""
echo "  Browse data (new terminal):"
echo "    source venv/bin/activate"
echo "    python housing_inspect.py stats"
echo "    python housing_inspect.py tag mortgage"
echo "    python housing_inspect.py tag luxury"
echo "    python housing_inspect.py tag india"
echo "    python housing_inspect.py search 'interest rate'"
echo ""
echo "  Press Ctrl+C to stop."
echo "============================================"
echo ""
python main.py
