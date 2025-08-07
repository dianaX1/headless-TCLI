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

# Updated import block
try:
    # Prefer the 'tdjson' package (provided via pip install tdjson)
    import tdjson  # type: ignore
except ImportError:
    try:
        # Fallback to the older 'pywtdlib' package if tdjson isn't installed
        from pywtdlib import tdjson  # type: ignore
    except ImportError as exc:
        raise RuntimeError(
            "Failed to import tdjson. Install it via 'pip install tdjson' or 'pip install pywtdlib'"
        ) from exc


class TDLibClient:
    """Encapsulate a TDLib client instance."""

    def __init__(self) -> None:
        self.client_id: int = tdjson.td_create_client_id()
        self._running: bool = True

        try:
            self._loop = asyncio.get_running_loop()
        except RuntimeError:
            self._loop = asyncio.get_event_loop()

        self._update_queue: asyncio.Queue[Dict[str, Any]] = asyncio.Queue()

        try:
            tdjson.td_set_log_verbosity_level(1)
        except AttributeError:
            pass

        self._recv_thread = threading.Thread(
            target=self._recv_loop, name="tdlib-recv", daemon=True
        )
        self._recv_thread.start()

    def _recv_loop(self) -> None:
        while self._running:
            try:
                raw_update: Optional[str] = tdjson.td_receive(1.0)
            except Exception:
                continue

            if not raw_update:
                continue
            try:
                update: Dict[str, Any] = json.loads(raw_update)
            except Exception:
                continue
            try:
                self._loop.call_soon_threadsafe(
                    self._update_queue.put_nowait, update
                )
            except RuntimeError:
                break

    def send(self, query: Dict[str, Any]) -> None:
        tdjson.td_send(self.client_id, json.dumps(query))

    def execute(self, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        result = tdjson.td_execute(json.dumps(query))
        if result:
            try:
                return json.loads(result)
            except Exception:
                return None
        return None

    async def receive(self) -> Dict[str, Any]:
        return await self._update_queue.get()

    def close(self) -> None:
        self._running = False
        try:
            self.send({"@type": "close"})
        except Exception:
            pass
        if self._recv_thread.is_alive():
            self._recv_thread.join(timeout=2.0)
