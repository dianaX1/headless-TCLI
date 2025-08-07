@echo off
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                 HEADLESS TELEGRAM CLIENT                     ║
echo ║                      Setup Script                            ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

echo [INFO] Setting up Headless Telegram Client for Windows 11...
echo.

REM Check if Python is installed
echo [INFO] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo [INFO] Please install Python 3.8+ from https://python.org
    echo [INFO] Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

python --version
echo [SUCCESS] Python is installed
echo.

REM Check Python version (basic check)
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [INFO] Python version: %PYTHON_VERSION%
echo.

REM Create virtual environment
echo [INFO] Creating virtual environment...
if exist "venv" (
    echo [INFO] Virtual environment already exists, removing old one...
    rmdir /s /q venv
)

python -m venv venv
if errorlevel 1 (
    echo [ERROR] Failed to create virtual environment
    echo [INFO] Make sure you have the latest Python version installed
    pause
    exit /b 1
)
echo [SUCCESS] Virtual environment created
echo.

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)
echo [SUCCESS] Virtual environment activated
echo.

REM Upgrade pip
echo [INFO] Upgrading pip...
python -m pip install --upgrade pip
echo.

REM Install dependencies
echo [INFO] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    echo [INFO] This might be due to network issues or missing system dependencies
    echo [INFO] For TDLib on Windows, you might need Visual C++ Redistributable
    pause
    exit /b 1
)
echo [SUCCESS] Dependencies installed successfully
echo.

REM Create necessary directories
echo [INFO] Creating necessary directories...
if not exist "tdlib" mkdir tdlib
if not exist "static" mkdir static
if not exist "templates" mkdir templates
echo [SUCCESS] Directories created
echo.

echo ╔══════════════════════════════════════════════════════════════╗
echo ║                      SETUP COMPLETE                         ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
echo [SUCCESS] Headless Telegram Client setup completed successfully!
echo.
echo NEXT STEPS:
echo 1. Get your Telegram API credentials:
echo    - Go to https://my.telegram.org
echo    - Log in with your phone number
echo    - Go to "API development tools"
echo    - Create a new application
echo    - Note down your API ID and API Hash
echo.
echo 2. Run the application:
echo    - Double-click "run_web.bat" to start the web interface
echo    - Open your browser and go to http://127.0.0.1:8000
echo    - Enter your API credentials to authenticate
echo.
echo 3. Usage:
echo    - Use @username or numeric chat_id to send messages
echo    - Messages will appear in real-time in the web interface
echo    - The interface works like a terminal/CLI in your browser
echo.
echo [INFO] Press any key to exit...
pause >nul
