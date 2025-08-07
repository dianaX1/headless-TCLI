"""High‑level wrapper around TDLib's JSON interface.

This module provides an asynchronous wrapper for the TDLib JSON API
exposed through the ``tdjson`` Python package.  It hides the low
level details of maintaining a receive loop, deserialising JSON
messages and dispatching updates to the rest of the application.  All
communication with Telegram servers happens through TDLib; no direct
network calls are made by this module.

Usage
-----
The client exposes a handful of methods:

* ``send(query: dict)`` – enqueue a JSON request to TDLib.
* ``execute(query: dict)`` – synchronously execute a local TDLib
  request (for example, reading local configuration options).  This
  call must not be used for network requests.
* ``receive()`` – asynchronously await the next update or response
  from TDLib.  All updates are delivered through this queue.
* ``close()`` – gracefully shut down the receive loop and the TDLib
  client.

Behind the scenes a dedicated background thread polls TDLib for
updates using ``tdjson.td_receive``.  Each result is parsed from
JSON and pushed onto an ``asyncio.Queue`` that you can await using
``receive()``.  This design decouples the synchronous TDLib API from
the asynchronous parts of your program.

This wrapper does not perform any authorisation or high‑level
message handling; see :mod:`auth` for the login flow and
:mod:`message_handler` for incoming/outgoing message logic.
"""

from __future__ import annotations

import json
import threading
import asyncio
from typing import Any, Dict, Optional

try:
    from pywtdlib import tdjson # type: ignore
except ImportError as exc:
    raise RuntimeError(
        "Failed to import tdjson. Install it via 'pip install pywtdlib'"
    ) from exc


class TDLibClient:
    """Encapsulate a TDLib client instance.

    The class hides all boilerplate needed to create a TDLib client
    identifier, poll for updates on a background thread and expose an
    asynchronous queue for consumers.  You can send arbitrary JSON
    requests via :meth:`send` and synchronously execute local queries
    via :meth:`execute`.
    """

    def __init__(self) -> None:
        # Create a new TDLib client.  tdjson returns an opaque integer
        # identifying this client.  According to the tdjson
        # documentation, you can send requests using this client ID and
        # receive events globally【89978177518156†L533-L555】.
        self.client_id: int = tdjson.td_create_client_id()

        # Internal state to control the background receive loop.
        self._running: bool = True

        # The asyncio loop used to marshal updates from the background
        # thread into the coroutine world.  Note: get_event_loop will
        # return the current running loop when called from within an
        # async context.  If called from a synchronous context, it
        # returns the default loop.
        try:
            self._loop = asyncio.get_running_loop()
        except RuntimeError:
            self._loop = asyncio.get_event_loop()

        # Queue where parsed updates are stored.  Coroutines awaiting
        # ``receive()`` consume from this queue.
        self._update_queue: asyncio.Queue[Dict[str, Any]] = asyncio.Queue()

        # Attempt to set a low verbosity level for TDLib logging.  This
        # makes TDLib less chatty on stdout/stderr.
        try:
            # 1 means fatal errors only.  0 disables logging entirely.
            tdjson.td_set_log_verbosity_level(1)
        except AttributeError:
            # tdjson may not expose this helper; it's safe to ignore.
            pass

        # Start the background thread responsible for polling
        # tdjson.td_receive.  Using a thread allows us to call the
        # blocking C function without blocking the asyncio event loop.
        self._recv_thread = threading.Thread(
            target=self._recv_loop, name="tdlib-recv", daemon=True
        )
        self._recv_thread.start()

    def _recv_loop(self) -> None:
        """Continuously poll TDLib for updates and dispatch them.

        TDLib exposes a single polling function ``td_receive`` which
        blocks for up to the specified timeout and returns either a
        JSON‑encoded string or ``None`` if nothing has arrived.  This
        method runs in a dedicated thread, decodes each JSON payload
        and forwards it to the asyncio queue.  Exceptions are
        intentionally swallowed to keep the receive loop alive.
        """
        while self._running:
            try:
                # Poll for up to one second; adjust the timeout to
                # trade off between latency and CPU usage.
                raw_update: Optional[str] = tdjson.td_receive(1.0)
            except Exception:
                continue

            if not raw_update:
                continue
            try:
                update: Dict[str, Any] = json.loads(raw_update)
            except Exception:
                # Ignore malformed JSON responses; unlikely under normal
                # circumstances but better safe than sorry.
                continue
            # Push the update onto the asyncio queue.  Use call_soon to
            # ensure thread safety when interacting with the event loop.
            try:
                self._loop.call_soon_threadsafe(
                    self._update_queue.put_nowait, update
                )
            except RuntimeError:
                # Event loop closed; stop polling.
                break

    def send(self, query: Dict[str, Any]) -> None:
        """Send an arbitrary request to TDLib.

        Parameters
        ----------
        query: dict
            A dictionary representing the JSON object to send.  The
            dictionary must contain the ``@type`` key specifying the
            TDLib method to invoke.  The object is serialised to JSON
            before being passed to the underlying C function.
        """
        tdjson.td_send(self.client_id, json.dumps(query))

    def execute(self, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Synchronously execute a local TDLib request.

        ``td_execute`` may only be used for requests that do not
        involve network communication.  For example, reading local
        options or setting the log verbosity level.  The call returns
        ``None`` if the request could not be executed synchronously.
        See the TDLib documentation for details.
        """
        result = tdjson.td_execute(json.dumps(query))
        if result:
            try:
                return json.loads(result)
            except Exception:
                return None
        return None

    async def receive(self) -> Dict[str, Any]:
        """Await the next update or response from TDLib.

        Returns
        -------
        dict
            The next update object decoded from TDLib.  The caller is
            responsible for inspecting the ``@type`` field to
            distinguish between authorisation updates, new messages
            and responses to previous requests.
        """
        return await self._update_queue.get()

    def close(self) -> None:
        """Gracefully shut down the client and background thread."""
        # Signal the receive loop to stop.  Sending the ``close``
        # request tells TDLib to terminate the session.  After closing
        # the session you should discard the client instance.
        self._running = False
        try:
            self.send({"@type": "close"})
        except Exception:
            pass
        # Wait for the receive thread to exit
        if self._recv_thread.is_alive():
            self._recv_thread.join(timeout=2.0)