@echo off
REM ============================================================
REM  Housing Market News Bot — Windows Launcher
REM  Usage: Double-click start.bat
REM ============================================================
cd /d "%~dp0"

echo ============================================
echo   Housing Market News Bot
echo ============================================
echo.

set PYTHON=
for %%p in (python python3 py) do (
    if not defined PYTHON ( %%p --version >nul 2>&1 && set PYTHON=%%p )
)
if not defined PYTHON (
    echo ERROR: Python not found. Install from https://www.python.org/downloads/
    pause & exit /b 1
)

for /f "tokens=*" %%v in ('%PYTHON% --version 2^>^&1') do set PY_VER=%%v
echo   Python : %PY_VER%
echo   Folder : %~dp0
echo.

if not exist "venv\Scripts\activate.bat" (
    echo [1/4] Creating virtual environment...
    %PYTHON% -m venv venv
) else (
    echo [1/4] Virtual environment found
)

echo [2/4] Activating...
call venv\Scripts\activate.bat

echo [3/4] Installing dependencies...
pip install -q -r requirements.txt
echo       OK

echo [4/4] Setting up directories...
if not exist logs mkdir logs
echo       OK

echo.
echo   Outputs:
echo     housing_news.db    - SQLite database
echo     housing_news.csv   - CSV flat file
echo     logs\              - Rotating log files
echo.
echo   Browse data ^(new window^):
echo     venv\Scripts\activate
echo     python housing_inspect.py stats
echo     python housing_inspect.py tag mortgage
echo     python housing_inspect.py tag luxury
echo     python housing_inspect.py search "interest rate"
echo.
echo   Press Ctrl+C to stop.
echo ============================================
echo.

python main.py
echo. & echo Bot stopped. & pause
