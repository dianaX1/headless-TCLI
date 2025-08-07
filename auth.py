"""Handle the TDLib authorisation flow for user accounts.

TDLib exposes a state machine for user authentication.  After
creating a client the library enters ``authorizationStateWaitTdlibParameters``
and repeatedly transitions through several states until the user is
fully authorised.  This module guides the user through that process:

* Provide TDLib parameters such as ``api_id``, ``api_hash`` and
  storage directories.
* Prompt for a phone number, verification code and two‑factor
  password where necessary.
* Register a new account when required.

The public entry point is :func:`authenticate`.  It takes a
configured :class:`telegram_headless.tdlib_client.TDLibClient` and
blocks until the user is authenticated.  Once complete the
``authorizationStateReady`` update is returned and the caller may
proceed with message handling.
"""

from __future__ import annotations

import os
import asyncio
from typing import Any, Dict, Optional

from pywtdlib import tdjson


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
    """Perform the interactive TDLib authorisation flow.

    Parameters
    ----------
    client : TDLibClient
        An instance of :class:`telegram_headless.tdlib_client.TDLibClient`.
    api_id : int
        Telegram API ID obtained from https://my.telegram.org.
    api_hash : str
        Telegram API hash obtained from https://my.telegram.org.
    phone_number : str, optional
        The user's phone number in international format.  If not
        provided the user will be prompted on the console.
    encryption_key : str, optional
        Key used to encrypt the local TDLib database.  Use an empty
        string for an unencrypted database.  Changing this value on
        subsequent runs will invalidate the existing session.
    database_directory : str
        Directory where TDLib stores its database.  Must persist
        between runs to avoid re‑authorising each time.
    files_directory : str
        Directory where TDLib stores downloaded files.
    device_model : str
        Arbitrary string identifying the device model shown in Telegram
        settings.  Defaults to ``"headless"``.
    system_version : str
        Arbitrary string describing the operating system version.
    application_version : str
        Version string shown in Telegram sessions.
    """

    # Wait until authorisation is complete
    while True:
        update = await client.receive()
        if update.get("@type") != "updateAuthorizationState":
            # Not an authorisation update; ignore
            continue
        auth_state: Dict[str, Any] = update.get("authorization_state", {})
        state_type: str = auth_state.get("@type", "")

        if state_type == "authorizationStateWaitTdlibParameters":
            # TDLib requests basic parameters required for operation.
            params: Dict[str, Any] = {
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
            }
            client.send(params)

        elif state_type == "authorizationStateWaitEncryptionKey":
            # Provide the encryption key for the local database.  An
            # empty string disables encryption.  If the key differs
            # from the one used previously TDLib will not be able to
            # open the database.
            client.send({
                "@type": "checkDatabaseEncryptionKey",
                "encryption_key": encryption_key,
            })

        elif state_type == "authorizationStateWaitPhoneNumber":
            # Prompt the user for their phone number.  On the first
            # login TDLib requires the phone number to which the code
            # will be delivered.
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
            # Ask for the authentication code sent via Telegram.  The
            # code might arrive via SMS, in an active Telegram session
            # or through the app itself depending on your account
            # settings.
            code = input("Enter the authentication code you received: ")
            client.send({
                "@type": "checkAuthenticationCode",
                "code": code,
            })

        elif state_type == "authorizationStateWaitPassword":
            # If two‑factor authentication is enabled, request the
            # password.  Note: do not log or expose this password.
            password = input("Enter your 2FA password: ")
            client.send({
                "@type": "checkAuthenticationPassword",
                "password": password,
            })

        elif state_type == "authorizationStateWaitRegistration":
            # This state is reached when the phone number is not
            # associated with any Telegram account.  Register a new
            # account by providing a first and last name.
            first_name = input("Enter your first name: ")
            last_name = input("Enter your last name: ")
            client.send({
                "@type": "registerUser",
                "first_name": first_name,
                "last_name": last_name,
            })

        elif state_type == "authorizationStateReady":
            # All necessary steps have been completed.  The client is
            # authorised and ready to send/receive messages.
            print("Authentication successful.  You are now logged in.")
            return

        elif state_type == "authorizationStateClosed":
            # TDLib reported a fatal error or the user logged out from
            # another session.  In this case there is nothing to do
            # except exit.
            raise RuntimeError("TDLib closed the authorisation process.")

        # Other states (authorizationStateLoggingOut,
        # authorizationStateClosing, etc.) are transient and do not
        # require explicit handling here.