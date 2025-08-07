# PowerShell script to run the Headless Telegram Client Web Interface
Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║                 HEADLESS TELEGRAM CLIENT                     ║" -ForegroundColor Green
Write-Host "║                    Web Interface Launcher                    ║" -ForegroundColor Green
Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""

Write-Host "[INFO] Starting Headless Telegram Client Web Interface..." -ForegroundColor Yellow
Write-Host "[INFO] The web interface will be available at: http://127.0.0.1:8000" -ForegroundColor Yellow
Write-Host "[INFO] Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Python not found"
    }
    Write-Host "[SUCCESS] Python is installed: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "[INFO] Please install Python 3.8+ from https://python.org" -ForegroundColor Yellow
    Write-Host "[INFO] Make sure to check 'Add Python to PATH' during installation" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if virtual environment exists, create if not
if (-not (Test-Path "venv")) {
    Write-Host "[INFO] Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Failed to create virtual environment" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Activate virtual environment
Write-Host "[INFO] Activating virtual environment..." -ForegroundColor Yellow
try {
    . ".\venv\Scripts\Activate.ps1"
    Write-Host "[SUCCESS] Virtual environment activated." -ForegroundColor Green
}
catch {
    Write-Host "[ERROR] Failed to activate virtual environment." -ForegroundColor Red
    Write-Host "[INFO] You may need to enable script execution by running this command in an Administrator PowerShell:" -ForegroundColor Yellow
    Write-Host "       Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}


# Install/upgrade dependencies
Write-Host "[INFO] Installing/updating dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Failed to install dependencies" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Start the web server
Write-Host "[INFO] Starting web server..." -ForegroundColor Yellow
Write-Host "[INFO] Open your browser and go to: http://127.0.0.1:8000" -ForegroundColor Green
Write-Host ""

# Run the python server
python web_server.py

# Script finished
Write-Host ""
Write-Host "[INFO] Server stopped." -ForegroundColor Yellow
Read-Host "Press Enter to exit"
