# Headless Telegram Client using TDLib

This repository contains a minimal, headless Telegram client built on
top of [TDLib](https://github.com/tdlib/td).  It is intended for
developers who need to interact with their personal Telegram account
without a graphical interface. The project now includes both a 
command-line interface and a **web-based CLI-style interface** that
runs in your browser.

## Features

* **Headless operation** – no GUI; works via terminal or web browser.
* **Web-based CLI interface** – terminal-style interface accessible via web browser.
* **User accounts** – log in with your phone number just like the
  official apps (bots are *not* used).
* **Real‑time message streaming** – displays new messages as they
  arrive with WebSocket support.
* **Interactive sending** – send messages to any chat using @username or chat ID.
* **Session persistence** – session data is stored on disk so you
  only need to authorise once.
* **Windows 11 optimized** – includes batch files for easy setup and launching.

## Installation

### Quick Setup for Windows 11 (Recommended)

1. **Get Telegram API credentials first:**
   - Go to [my.telegram.org](https://my.telegram.org)
   - Log in with your phone number
   - Navigate to *API development tools*
   - Create a new application
   - Record your numeric `api_id` and `api_hash` string

2. **Download and setup:**
   - Download/clone this repository
   - Double-click `setup.bat` to automatically install everything
   - The script will create a virtual environment and install all dependencies

3. **Run the web interface:**
   - Double-click `run_web.bat` to start the web server
   - Open your browser and go to `http://127.0.0.1:8000`
   - Enter your API credentials in the web interface

### Manual Installation (Advanced Users)

If you prefer manual setup or are using a different operating system:

#### 1. Install Python Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### 2. Install TDLib

The `tdjson` package provides pre-compiled TDLib binaries and is automatically
installed via requirements.txt. It includes TDLib support for Windows, Linux, and macOS.

#### 3. Start the Application

**Web Interface (Recommended):**
```bash
python web_server.py
```
Then open `http://127.0.0.1:8000` in your browser.

**Command Line Interface:**
```bash
python main.py --api-id <API_ID> --api-hash <API_HASH>
```

## Usage

### Web Interface (Recommended)

1. **Start the web server:**
   - Double-click `run_web.bat` (Windows)
   - Or run: `python web_server.py`

2. **Open your browser:**
   - Navigate to `http://127.0.0.1:8000`
   - You'll see a terminal-style interface

3. **Authenticate:**
   - Enter your API ID and API Hash
   - Optionally enter your phone number (or leave blank to be prompted)
   - Click "AUTHENTICATE"
   - Follow the prompts for verification code and 2FA if needed

4. **Send messages:**
   - Use `@username` for public usernames
   - Use numeric `chat_id` for specific chats
   - Type your message and press Enter or click "SEND"
   - Messages appear in real-time in the terminal-style display

### Command Line Interface

For traditional command-line usage:

```bash
python main.py --api-id <API_ID> --api-hash <API_HASH>
```

The CLI version runs two concurrent loops:
1. **Message listener** – displays incoming messages and logs them to `messages.log`
2. **Send loop** – interactive prompt for sending messages

## Project structure

```text
telegram_headless/
├── tdlib/               # TDLib's database and session data
├── templates/           # HTML templates for web interface
│   └── index.html       # main CLI-style web interface
├── static/              # static files (created automatically)
├── tdlib_client.py      # low‑level wrapper around tdjson
├── auth.py              # interactive authorisation helper
├── message_handler.py   # incoming/outgoing message logic
├── main.py              # CLI entry point
├── web_server.py        # FastAPI web server with WebSocket support
├── requirements.txt     # Python dependencies
├── setup.bat            # Windows setup script
├── run_web.bat          # Windows web server launcher
└── README.md            # this file
```

## Security considerations

* **Keep your API hash secret.** Never commit it to version control
  or share it with others.
* The session stored in the `tdlib` directory contains sensitive
  authentication tokens.  Protect it with appropriate filesystem
  permissions.  Deleting this directory will require you to log in
  again.
* When two‑factor authentication is enabled TDLib will prompt for
  your password during login.  This client reads the password from
  standard input and sends it directly to TDLib; it is not stored.

## Extending the client

This project intentionally implements only the basics: logging and
sending simple text messages.  TDLib exposes a rich API for working
with media, contacts, stickers, channels and much more.  You can
inspect any TDLib function or type via the [official reference
documentation](https://core.telegram.org/tdlib/docs/classtd_1_1td__api_1_1_function.html).

For example, the [`python-telegram`](https://pypi.org/project/python-telegram/)
library builds on TDLib and offers a more batteries‑included
experience.  Its documentation contains a basic example showing how
to send a message by instantiating a `Telegram` object with your
`api_id`, `api_hash` and phone number and calling `send_message`
【368021729070146†L602-L630】.  In this repository we choose to use
`tdjson` directly for educational purposes, but you may adopt a
higher‑level library in your own projects.

## Troubleshooting

* **ImportError: No module named 'tdjson'** – ensure you have run
  `pip install tdjson` in the correct virtual environment.  The
  `tdjson` package includes a pre‑built TDLib shared library and
  should work on Linux and macOS.
* **AuthorizationStateClosed** – TDLib closed the authorisation
  process.  This can happen if you log out from another device.  Try
  deleting the `tdlib` directory and running the client again.
* **Unsupported message type** – the client currently only
  displays plain text messages.  Other content types are shown as
  placeholders.  Extend `message_handler.py` to add support for
  photos, videos and documents.

---

© 2025 Headless Telegram Client Authors.  Distributed under the
MIT Licence.