#!/bin/bash

# Always run from the project directory where this file is located
cd "$(dirname "$0")" || exit 1

echo "======================================================="
echo "  🐾 PawConnect - macOS Auto-Setup & Offline Launcher"
echo "  Atlantia International STEM Olympiad (SW01)"
echo "======================================================="
echo ""

# -------------------------------------------------------
# 1. Locate a working Python 3 (3.10+) on macOS
# -------------------------------------------------------
find_python() {
    # Check official Python.org installs & Homebrew paths first
    for candidate in \
        "/Library/Frameworks/Python.framework/Versions/3.13/bin/python3" \
        "/Library/Frameworks/Python.framework/Versions/3.12/bin/python3" \
        "/Library/Frameworks/Python.framework/Versions/3.11/bin/python3" \
        "/Library/Frameworks/Python.framework/Versions/3.10/bin/python3" \
        "/opt/homebrew/bin/python3" \
        "/usr/local/bin/python3"
    do
        if [ -x "$candidate" ]; then
            if "$candidate" -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)" >/dev/null 2>&1; then
                echo "$candidate"
                return 0
            fi
        fi
    done

    # Check PATH python3, avoiding the macOS /usr/bin/python3 stub if Xcode CLT is not installed
    if command -v python3 >/dev/null 2>&1; then
        PY_PATH="$(command -v python3)"
        if [ "$PY_PATH" != "/usr/bin/python3" ] || xcode-select -p >/dev/null 2>&1; then
            if "$PY_PATH" -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)" >/dev/null 2>&1; then
                echo "$PY_PATH"
                return 0
            fi
        fi
    fi

    return 1
}

PYTHON_BIN="$(find_python)"

# -------------------------------------------------------
# 2. Install Python 3 automatically if not found
# -------------------------------------------------------
if [ -z "$PYTHON_BIN" ]; then
    echo "[!] Python 3.10+ was not found on this Mac."
    echo "[*] Downloading official Python 3.12 Universal Installer (works on M1/M2/M3/M4 & Intel)..."
    PKG_PATH="/tmp/python-3.12.8-macos11.pkg"
    curl -L --progress-bar "https://www.python.org/ftp/python/3.12.8/python-3.12.8-macos11.pkg" -o "$PKG_PATH"

    if [ ! -f "$PKG_PATH" ]; then
        echo "[X] Download failed. Please check your internet connection and try again."
        read -n 1 -s -r -p "Press any key to close..."
        exit 1
    fi

    echo ""
    echo "[*] Installing Python 3.12..."
    echo "    (If prompted, enter your Mac login password, or complete the installer window)"
    if ! sudo installer -pkg "$PKG_PATH" -target /; then
        echo "[*] Opening graphical Python installer... Please complete the installation window."
        open -W "$PKG_PATH"
    fi
    rm -f "$PKG_PATH"

    PYTHON_BIN="$(find_python)"
    if [ -z "$PYTHON_BIN" ]; then
        echo "[X] Python installation was not completed. Please run this file again after installing Python."
        read -n 1 -s -r -p "Press any key to close..."
        exit 1
    fi
fi

echo "[OK] Using Python: $PYTHON_BIN ($("$PYTHON_BIN" --version 2>&1))"

# -------------------------------------------------------
# 3. Create or repair the macOS Virtual Environment (venv)
# -------------------------------------------------------
# If venv was copied from Windows or is broken on this Mac, recreate it
if [ ! -x "./venv/bin/python" ] || ! ./venv/bin/python -c "import sys" >/dev/null 2>&1; then
    echo "[*] Creating fresh macOS virtual environment (venv)..."
    rm -rf ./venv
    "$PYTHON_BIN" -m venv venv
    if [ $? -ne 0 ]; then
        echo "[X] Failed to create virtual environment."
        read -n 1 -s -r -p "Press any key to close..."
        exit 1
    fi
fi

# -------------------------------------------------------
# 4. Install dependencies if not already installed
# -------------------------------------------------------
if ! ./venv/bin/python -c "import fastapi, uvicorn, sqlalchemy, pydantic, jinja2, multipart, aiofiles, pytest" >/dev/null 2>&1; then
    echo "[*] Installing required packages into venv (one-time setup)..."
    ./venv/bin/python -m pip install --upgrade pip
    ./venv/bin/python -m pip install -r requirements.txt pytest
    if [ $? -ne 0 ]; then
        echo "[X] Failed to install packages. Make sure you are connected to the internet for the first run."
        read -n 1 -s -r -p "Press any key to close..."
        exit 1
    fi
    echo "[OK] All requirements installed successfully!"
else
    echo "[OK] All dependencies are ready (Offline mode supported)."
fi

# -------------------------------------------------------
# 5. Start the Offline Server & Open Browser
# -------------------------------------------------------
echo ""
echo "🚀 Starting PawConnect at http://localhost:8000 ..."
echo "   (Press Ctrl+C in this window to stop the server)"
echo ""

# Open the browser once the server is listening
(sleep 1.5 && open "http://localhost:8000") &

./venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
