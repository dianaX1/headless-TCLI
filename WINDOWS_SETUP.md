# Windows 11 Setup Guide for Headless Telegram Client

This guide will help you set up the Headless Telegram Client on Windows 11 with the web-based CLI interface.

## Prerequisites

### 1. Install Python

1. **Download Python:**
   - Go to [python.org](https://python.org)
   - Download Python 3.8 or later (3.11+ recommended)

2. **Install Python:**
   - Run the installer
   - **IMPORTANT:** Check "Add Python to PATH" during installation
   - Choose "Install Now" or customize installation as needed

3. **Verify Installation:**
   - Open Command Prompt (Win+R, type `cmd`, press Enter)
   - Type: `python --version`
   - You should see something like: `Python 3.11.x`

### 2. Get Telegram API Credentials

1. **Visit Telegram API Portal:**
   - Go to [my.telegram.org](https://my.telegram.org)
   - Log in with your phone number

2. **Create Application:**
   - Navigate to "API development tools"
   - Click "Create new application"
   - Fill in the form:
     - App title: "Headless Telegram Client"
     - Short name: "headless-tg"
     - Platform: "Desktop"
     - Description: "Personal headless client"

3. **Save Credentials:**
   - Copy your `api_id` (numeric)
   - Copy your `api_hash` (string)
   - Keep these secure and private!

## Installation Methods

### Method 1: Automatic Setup (Recommended)

1. **Download the Project:**
   - Download/clone this repository to a folder (e.g., `C:\HeadlessTelegram`)

2. **Run Setup:**
   - Double-click `setup.bat`
   - The script will automatically:
     - Create a virtual environment
     - Install all dependencies
     - Set up the project structure

3. **Start the Web Interface:**
   - Double-click `run_web.bat`
   - Open your browser and go to `http://127.0.0.1:8000`

### Method 2: PowerShell (Alternative)

If batch files don't work:

1. **Enable PowerShell Scripts:**
   - Open PowerShell as Administrator
   - Run: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

2. **Run PowerShell Script:**
   - Right-click `run_web.ps1`
   - Select "Run with PowerShell"

### Method 3: Manual Setup

If automatic methods fail:

1. **Open Command Prompt:**
   - Navigate to the project folder
   - Example: `cd C:\HeadlessTelegram`

2. **Create Virtual Environment:**
   ```cmd
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install Dependencies:**
   ```cmd
   pip install -r requirements.txt
   ```

4. **Start Web Server:**
   ```cmd
   python web_server.py
   ```

## Using the Web Interface

### 1. Authentication

1. **Open Browser:**
   - Navigate to `http://127.0.0.1:8000`
   - You'll see a terminal-style interface

2. **Enter Credentials:**
   - API ID: Your numeric API ID
   - API Hash: Your API hash string
   - Phone: Your phone number (optional, can be entered later)

3. **Complete Authentication:**
   - Click "AUTHENTICATE"
   - Enter verification code when prompted
   - Enter 2FA password if enabled

### 2. Sending Messages

1. **Choose Target:**
   - Use `@username` for public usernames
   - Use numeric chat ID for specific chats
   - Example: `@telegram` or `123456789`

2. **Type Message:**
   - Enter your message text
   - Press Enter or click "SEND"

3. **View Messages:**
   - Incoming messages appear in real-time
   - Format: `[TIME] [SENDER | CHAT] > MESSAGE`

## Troubleshooting

### Python Issues

**Problem:** "Python was not found"
**Solution:**
- Reinstall Python with "Add to PATH" checked
- Or manually add Python to PATH:
  1. Find Python installation (usually `C:\Users\[username]\AppData\Local\Programs\Python\Python3x`)
  2. Add to System PATH in Environment Variables

**Problem:** "pip is not recognized"
**Solution:**
- Python installation issue, reinstall Python
- Or use: `python -m pip` instead of `pip`

### TDLib Issues

**Problem:** "Failed to import tdjson"
**Solution:**
- Install Visual C++ Redistributable from Microsoft
- Try: `pip install --upgrade tdjson`

**Problem:** "AuthorizationStateClosed"
**Solution:**
- Delete the `tdlib` folder
- Restart the application
- Re-authenticate

### Web Interface Issues

**Problem:** "WebSocket connection failed"
**Solution:**
- Check if port 8000 is available
- Try restarting the web server
- Check Windows Firewall settings

**Problem:** "Authentication failed"
**Solution:**
- Verify API credentials are correct
- Check internet connection
- Ensure phone number format is correct (+1234567890)

### Network Issues

**Problem:** "Connection timeout"
**Solution:**
- Check internet connection
- Try using VPN if Telegram is blocked
- Verify firewall isn't blocking the application

## Security Notes

1. **Keep API Credentials Safe:**
   - Never share your API ID and hash
   - Don't commit them to version control

2. **Session Data:**
   - The `tdlib` folder contains your session
   - Keep it secure with proper file permissions
   - Deleting it will require re-authentication

3. **Local Access Only:**
   - Web interface runs on localhost (127.0.0.1)
   - Not accessible from other computers by default
   - This is intentional for security

## Advanced Configuration

### Custom Port

To run on a different port, edit `web_server.py`:
```python
uvicorn.run(app, host="127.0.0.1", port=8080)  # Change 8000 to 8080
```

### Remote Access (Not Recommended)

To allow remote access (security risk):
```python
uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Multiple Sessions

To run multiple instances:
1. Create separate folders for each instance
2. Use different ports for each
3. Each will have its own `tdlib` session folder

## Support

If you encounter issues:

1. **Check the Console:**
   - Look for error messages in the command prompt
   - Note any Python tracebacks

2. **Verify Requirements:**
   - Python 3.8+ installed
   - All dependencies installed (`pip list`)
   - Valid API credentials

3. **Test Components:**
   - Try the CLI version: `python main.py --api-id X --api-hash Y`
   - Test Python imports: `python -c "import tdjson; print('OK')"`

4. **Common Solutions:**
   - Restart the application
   - Delete and recreate virtual environment
   - Reinstall dependencies
   - Check Windows Defender/antivirus

---

**Note:** This client is for personal use with your own Telegram account. It's not a bot and requires your personal phone number for authentication.
