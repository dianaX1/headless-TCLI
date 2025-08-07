"""Handle the TDLib authorisation flow for user accounts.

TDLib exposes a state machine for user authentication.
...
The public entry point is :func:`authenticate`. ...
"""

from __future__ import annotations

import os
import asyncio
from typing import Any, Dict, Optional

# ✅ Updated import block with fallback
try:
    import tdjson  # type: ignore
except ImportError:
    try:
        from pywtdlib import tdjson  # type: ignore
    except ImportError as exc:
        raise RuntimeError(
            "Failed to import tdjson. Install it via 'pip install tdjson' or 'pip install pywtdlib'"
        ) from exc

# 👇 Add this if not already present
from telegram_headless.tdlib_client import TDLibClient


async def authenticate(
    client: TDLibClient,
    api_id: int,
    api_hash: str,
    *,
    phone_number: Optional[str] = None,
    encryption_key: str = "",
    database_directory: str = "tdlib",
    files_directory: str = "tdlib",
    device_model: str = "headless",
    system_version: str = "",
    application_version: str = "headless-client"
) -> None:
    """Perform the interactive TDLib authorisation flow."""

    while True:
        update = await client.receive()
        if update.get("@type") != "updateAuthorizationState":
            continue
        auth_state: Dict[str, Any] = update.get("authorization_state", {})
        state_type: str = auth_state.get("@type", "")

        if state_type == "authorizationStateWaitTdlibParameters":
            client.send({
                "@type": "setTdlibParameters",
                "parameters": {
                    "@type": "tdlibParameters",
                    "use_test_dc": False,
                    "database_directory": database_directory,
                    "files_directory": files_directory,
                    "use_file_database": True,
                    "use_chat_info_database": True,
                    "use_message_database": True,
                    "use_secret_chats": True,
                    "api_id": api_id,
                    "api_hash": api_hash,
                    "system_language_code": "en",
                    "device_model": device_model,
                    "system_version": system_version or os.name,
                    "application_version": application_version,
                    "enable_storage_optimizer": True,
                    "ignore_file_names": False,
                },
            })

        elif state_type == "authorizationStateWaitEncryptionKey":
            client.send({
                "@type": "checkDatabaseEncryptionKey",
                "encryption_key": encryption_key,
            })

        elif state_type == "authorizationStateWaitPhoneNumber":
            if not phone_number:
                phone_number = input("Enter your phone number (international format): ")
            client.send({
                "@type": "setAuthenticationPhoneNumber",
                "phone_number": phone_number,
                "settings": {
                    "@type": "phoneNumberAuthenticationSettings",
                    "allow_flash_call": False,
                    "allow_missed_call": False,
                    "is_current_phone_number": False,
                    "allow_sms_retriever_api": False,
                },
            })

        elif state_type == "authorizationStateWaitCode":
            code = input("Enter the authentication code you received: ")
            client.send({
                "@type": "checkAuthenticationCode",
                "code": code,
            })

        elif state_type == "authorizationStateWaitPassword":
            password = input("Enter your 2FA password: ")
            client.send({
                "@type": "checkAuthenticationPassword",
                "password": password,
            })

        elif state_type == "authorizationStateWaitRegistration":
            first_name = input("Enter your first name: ")
            last_name = input("Enter your last name: ")
            client.send({
                "@type": "registerUser",
                "first_name": first_name,
                "last_name": last_name,
            })

        elif state_type == "authorizationStateReady":
            print("Authentication successful.  You are now logged in.")
            return

        elif state_type == "authorizationStateClosed":
            raise RuntimeError("TDLib closed the authorisation process.")
