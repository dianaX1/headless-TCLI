"""Entry point for the headless Telegram client.

This script ties together the low level TDLib client, the
authentication flow and the message handler into a cohesive command
line application.  It parses required configuration from command
line arguments, initiates the login process and then launches
concurrent tasks for receiving incoming messages and sending
outgoing ones.

Example usage::

    python main.py --api-id <YOUR_API_ID> --api-hash <YOUR_API_HASH>

On first run you will be prompted for your phone number and the
verification code delivered by Telegram.  Once authorised the
session is stored in the ``tdlib`` directory and you will remain
logged in across runs unless you explicitly log out from another
device.
"""

from __future__ import annotations

import argparse
import asyncio
import sys

from tdlib_client import TDLibClient
from auth import authenticate
from message_handler import listen_for_messages, interactive_send_loop


def parse_args(argv: list[str]) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Run a headless Telegram client using TDLib."
    )
    parser.add_argument(
        "--api-id",
        type=int,
        required=True,
        help="Telegram API ID obtained from https://my.telegram.org",
    )
    parser.add_argument(
        "--api-hash",
        type=str,
        required=True,
        help="Telegram API hash obtained from https://my.telegram.org",
    )
    parser.add_argument(
        "--phone",
        type=str,
        default=None,
        help="Phone number in international format.  If omitted the client prompts for it.",
    )
    parser.add_argument(
        "--database-directory",
        type=str,
        default="tdlib",
        help="Directory where TDLib stores its database.  Defaults to './tdlib'",
    )
    parser.add_argument(
        "--files-directory",
        type=str,
        default="tdlib",
        help="Directory where TDLib stores downloaded files.  Defaults to './tdlib'",
    )
    return parser.parse_args(argv)


async def run_async(args: argparse.Namespace) -> None:
    """Instantiate the TDLib client, perform authentication and start the I/O loops."""
    client = TDLibClient()
    try:
        await authenticate(
            client,
            api_id=args.api_id,
            api_hash=args.api_hash,
            phone_number=args.phone,
            database_directory=args.database_directory,
            files_directory=args.files_directory,
        )

        # After successful authentication run both the message listener
        # and the interactive send loop concurrently.  gather returns
        # when the first task completes; since the loops run until
        # cancelled this typically only happens on Ctrl+C.
        listener_task = asyncio.create_task(
            listen_for_messages(client, log_file="messages.log", print_to_console=True)
        )
        sender_task = asyncio.create_task(interactive_send_loop(client))
        done, pending = await asyncio.wait(
            {listener_task, sender_task}, return_when=asyncio.FIRST_COMPLETED
        )
        # Cancel any remaining task
        for task in pending:
            task.cancel()
        # Wait for cancellation to propagate
        await asyncio.gather(*pending, return_exceptions=True)
    finally:
        client.close()


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    try:
        asyncio.run(run_async(args))
    except KeyboardInterrupt:
        print("\nExiting...")


if __name__ == "__main__":  # pragma: no cover
    main()