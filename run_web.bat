@echo off
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                 HEADLESS TELEGRAM CLIENT                     ║
echo ║                    Web Interface Launcher                    ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

echo [INFO] Starting Headless Telegram Client Web Interface...
echo [INFO] The web interface will be available at: http://127.0.0.1:8000
echo [INFO] Press Ctrl+C to stop the server
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo [INFO] Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

REM Check if virtual environment exists, create if not
if not exist "venv" (
    echo [INFO] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat
set PATH=%CD%\venv\Lib\site-packages\pywtdlib\lib\Windows\AMD64;%PATH%

REM Install/upgrade dependencies
echo [INFO] Installing/updating dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)

REM Start the web server
echo [INFO] Starting web server...
echo [INFO] Open your browser and go to: http://127.0.0.1:8000
echo.
python web_server.py

REM If we get here, the server stopped
echo.
echo [INFO] Server stopped.
pause
