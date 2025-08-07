"""Message handling utilities for the headless Telegram client.

This module implements two primary features:

* An asynchronous listener for new messages from TDLib.  It
  continuously consumes updates from the client, formats them into
  human readable strings and writes them to both standard output and
  a log file.  Where possible it resolves chat and user names.
* An interactive sender that prompts the user for a destination chat
  and message text and sends that message via TDLib.

The functions defined here operate at a relatively low level.  They
handle only a subset of possible TDLib update types and message
contents.  Unsupported content types are represented as placeholder
strings.  Additional functionality (such as media downloads or
filters) could be layered on top in future phases.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple

from pywtdlib import tdjson


async def listen_for_messages(
    client: TDLibClient,
    *,
    log_file: str = "messages.log",
    print_to_console: bool = True,
) -> None:
    """Continuously listen for new messages across all chats.

    For each ``updateNewMessage`` event received from TDLib the
    message is formatted and appended to ``log_file``.  Known users
    and chats are cached as they are encountered to avoid repeated
    lookups.  Names are resolved lazily by dispatching ``getUser``
    and ``getChat`` requests when necessary and processing their
    responses as they arrive in the update stream.

    Parameters
    ----------
    client : TDLibClient
        Connected and authorised TDLib client instance.
    log_file : str, optional
        Path to the text file where incoming messages should be
        appended.  Defaults to ``"messages.log"``.
    print_to_console : bool, optional
        Whether to print incoming messages to standard output.  If
        False, messages are only written to the log file.
    """
    # Caches to map IDs to human readable names.  These are filled
    # gradually as TDLib delivers ``user`` and ``chat`` objects.
    users_cache: Dict[int, str] = {}
    chats_cache: Dict[int, str] = {}

    # Sets to track outstanding name lookups.  When a new ID is
    # encountered we send a request to TDLib and record the ID here to
    # avoid duplicate requests while we wait for the response.
    pending_user_ids: set[int] = set()
    pending_chat_ids: set[int] = set()

    # Open the log file in append mode.  Use aios open?  The file
    # handle lives for the duration of the coroutine.
    log_f = open(log_file, "a", encoding="utf-8")
    try:
        while True:
            update: Dict[str, Any] = await client.receive()

            # Handle new incoming messages
            if update.get("@type") == "updateNewMessage":
                message = update.get("message", {})
                chat_id = message.get("chat_id")
                sender_name = ""
                chat_name = ""

                # Resolve sender name
                sender = message.get("sender_id", {})
                if sender.get("@type") == "messageSenderUser":
                    user_id = sender.get("user_id")
                    if user_id is not None:
                        if user_id in users_cache:
                            sender_name = users_cache[user_id]
                        else:
                            # Request user details if not already pending
                            if user_id not in pending_user_ids:
                                client.send({"@type": "getUser", "user_id": user_id})
                                pending_user_ids.add(user_id)
                            # Fallback to raw ID until we resolve
                            sender_name = f"user:{user_id}"
                elif sender.get("@type") == "messageSenderChat":
                    # Messages can also be sent on behalf of a chat (e.g.
                    # channels).  Use the chat name when available.
                    chat_sender_id = sender.get("chat_id")
                    if chat_sender_id in chats_cache:
                        sender_name = chats_cache[chat_sender_id]
                    else:
                        if chat_sender_id not in pending_chat_ids:
                            client.send({"@type": "getChat", "chat_id": chat_sender_id})
                            pending_chat_ids.add(chat_sender_id)
                        sender_name = f"chat:{chat_sender_id}"

                # Resolve chat name
                if chat_id is not None:
                    if chat_id in chats_cache:
                        chat_name = chats_cache[chat_id]
                    else:
                        if chat_id not in pending_chat_ids:
                            client.send({"@type": "getChat", "chat_id": chat_id})
                            pending_chat_ids.add(chat_id)
                        chat_name = f"chat:{chat_id}"

                # Extract the textual content of the message.  TDLib
                # distinguishes many content types; we only handle plain
                # text here.  Other types are represented with a placeholder.
                content = message.get("content", {})
                if content.get("@type") == "messageText":
                    text_dict = content.get("text", {})
                    message_text = text_dict.get("text", "")
                else:
                    message_text = f"<Unsupported message type {content.get('@type')}>"

                # Format the timestamp.  TDLib stores seconds since the
                # Unix epoch in UTC.  Convert to the local timezone.
                timestamp = message.get("date")
                if timestamp is not None:
                    dt = datetime.fromtimestamp(int(timestamp), tz=timezone.utc).astimezone()
                    time_str = dt.strftime("%H:%M")
                else:
                    time_str = "--:--"

                # Construct the display strings and write them to the log.
                header_line = f"[{time_str}] [{sender_name} | {chat_name}]"
                body_line = f"> {message_text}"
                if print_to_console:
                    print(header_line)
                    print(body_line)
                    print()
                log_f.write(header_line + "\n")
                log_f.write(body_line + "\n")
                log_f.flush()

            # Capture user info delivered by TDLib in response to
            # getUser requests.  The update type for user objects is
            # documented in TDLib as simply ``user``.
            elif update.get("@type") == "user":
                user_id = update.get("id")
                if isinstance(user_id, int):
                    username = update.get("username")
                    first_name = update.get("first_name", "")
                    last_name = update.get("last_name", "")
                    if username:
                        display = f"@{username}"
                    else:
                        name_parts = (first_name.strip(), last_name.strip())
                        display = " ".join(part for part in name_parts if part)
                    users_cache[user_id] = display or f"user:{user_id}"
                    pending_user_ids.discard(user_id)

            # Capture chat info delivered by TDLib.  Chat objects are
            # delivered as ``chat`` updates.  The ``title`` field holds
            # the human readable name.
            elif update.get("@type") == "chat":
                chat_id = update.get("id")
                if isinstance(chat_id, int):
                    title = update.get("title", f"chat:{chat_id}")
                    chats_cache[chat_id] = title
                    pending_chat_ids.discard(chat_id)

            # Additional update types can be handled here as needed.

    finally:
        log_f.close()


async def interactive_send_loop(client: TDLibClient) -> None:
    """Prompt the user for messages to send.

    This coroutine runs in a loop, prompting the user to provide a
    destination and message body.  The destination can be either a
    numeric chat ID or a public username prefixed with ``@``.  If a
    username is provided the function will resolve it via
    ``searchPublicChat``.  Enter ``exit`` or press Ctrl+C to return.

    Parameters
    ----------
    client : TDLibClient
        An authorised TDLib client used to dispatch the ``sendMessage``
        request.
    """
    print("\nYou can now send messages.  Type 'exit' to quit the send loop.")
    while True:
        try:
            dest = input("Enter chat ID or @username: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not dest:
            continue
        if dest.lower() in {"exit", "quit", ":q", "q"}:
            break

        # Resolve a username to a chat ID if necessary.  For public
        # usernames TDLib exposes the ``searchPublicChat`` method.  The
        # response will be delivered asynchronously as a ``chat`` object.
        chat_id: Optional[int] = None
        if dest.startswith("@"):  # username
            username = dest[1:]
            # Send search request
            client.send({"@type": "searchPublicChat", "username": username})
            # Wait for the result
            while True:
                update = await client.receive()
                if update.get("@type") == "chat" and update.get("username", "").lower() == username.lower():
                    chat_id = update.get("id")
                    break
                # Allow other updates (e.g. new messages) to be processed
                # concurrently by ignoring them here.  Consumers
                # listening to the same queue will see the same updates.
        else:
            try:
                chat_id = int(dest)
            except ValueError:
                print("Invalid chat identifier.  Provide an integer ID or a public @username.")
                continue

        if chat_id is None:
            print(f"Could not resolve destination '{dest}'.  Try again.")
            continue

        text = input("Enter your message: ")
        if not text:
            continue
        request = {
            "@type": "sendMessage",
            "chat_id": chat_id,
            "input_message_content": {
                "@type": "inputMessageText",
                "text": {
                    "@type": "formattedText",
                    "text": text,
                    "entities": [],
                },
            },
        }
        client.send(request)
        print("Message sent!\n")