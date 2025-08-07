"""FastAPI web server for the headless Telegram client.

This module provides a web-based CLI-style interface for the Telegram client.
It uses FastAPI to serve a terminal-like interface accessible via web browser,
with WebSocket support for real-time message updates.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from tdlib_client import TDLibClient
from auth import authenticate
from message_handler import listen_for_messages

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Headless Telegram Client", description="CLI-style web interface for Telegram")

# Create directories if they don't exist
Path("static").mkdir(exist_ok=True)
Path("templates").mkdir(exist_ok=True)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Global state
telegram_client: Optional[TDLibClient] = None
is_authenticated = False
connected_websockets: List[WebSocket] = []
message_history: List[Dict] = []
auth_status = {"status": "not_started", "message": ""}


class TelegramWebClient:
    def __init__(self):
        self.client: Optional[TDLibClient] = None
        self.is_running = False
        self.auth_data = {}
        
    async def start_client(self, api_id: int, api_hash: str, phone: Optional[str] = None):
        """Initialize and authenticate the Telegram client."""
        global is_authenticated, auth_status
        
        try:
            self.client = TDLibClient()
            auth_status = {"status": "authenticating", "message": "Starting authentication..."}
            await self.broadcast_auth_status()
            
            # Start authentication
            await authenticate(
                self.client,
                api_id=api_id,
                api_hash=api_hash,
                phone_number=phone,
                database_directory="tdlib",
                files_directory="tdlib"
            )
            
            is_authenticated = True
            auth_status = {"status": "authenticated", "message": "Successfully authenticated!"}
            await self.broadcast_auth_status()
            
            # Start message listener
            asyncio.create_task(self.message_listener())
            
            return True
            
        except Exception as e:
            auth_status = {"status": "error", "message": f"Authentication failed: {str(e)}"}
            await self.broadcast_auth_status()
            return False
    
    async def message_listener(self):
        """Listen for incoming messages and broadcast them to connected clients."""
        if not self.client:
            return
            
        users_cache: Dict[int, str] = {}
        chats_cache: Dict[int, str] = {}
        pending_user_ids: set[int] = set()
        pending_chat_ids: set[int] = set()
        
        while True:
            try:
                update = await self.client.receive()
                
                if update.get("@type") == "updateNewMessage":
                    message = update.get("message", {})
                    formatted_message = await self.format_message(
                        message, users_cache, chats_cache, pending_user_ids, pending_chat_ids
                    )
                    
                    if formatted_message:
                        message_history.append(formatted_message)
                        # Keep only last 100 messages in memory
                        if len(message_history) > 100:
                            message_history.pop(0)
                        
                        await self.broadcast_message(formatted_message)
                
                # Handle user and chat info updates
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
                
                elif update.get("@type") == "chat":
                    chat_id = update.get("id")
                    if isinstance(chat_id, int):
                        title = update.get("title", f"chat:{chat_id}")
                        chats_cache[chat_id] = title
                        pending_chat_ids.discard(chat_id)
                        
            except Exception as e:
                logger.error(f"Error in message listener: {e}")
                await asyncio.sleep(1)
    
    async def format_message(self, message, users_cache, chats_cache, pending_user_ids, pending_chat_ids):
        """Format a message for display."""
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
                    if user_id not in pending_user_ids:
                        self.client.send({"@type": "getUser", "user_id": user_id})
                        pending_user_ids.add(user_id)
                    sender_name = f"user:{user_id}"
        elif sender.get("@type") == "messageSenderChat":
            chat_sender_id = sender.get("chat_id")
            if chat_sender_id in chats_cache:
                sender_name = chats_cache[chat_sender_id]
            else:
                if chat_sender_id not in pending_chat_ids:
                    self.client.send({"@type": "getChat", "chat_id": chat_sender_id})
                    pending_chat_ids.add(chat_sender_id)
                sender_name = f"chat:{chat_sender_id}"
        
        # Resolve chat name
        if chat_id is not None:
            if chat_id in chats_cache:
                chat_name = chats_cache[chat_id]
            else:
                if chat_id not in pending_chat_ids:
                    self.client.send({"@type": "getChat", "chat_id": chat_id})
                    pending_chat_ids.add(chat_id)
                chat_name = f"chat:{chat_id}"
        
        # Extract message content
        content = message.get("content", {})
        if content.get("@type") == "messageText":
            text_dict = content.get("text", {})
            message_text = text_dict.get("text", "")
        else:
            message_text = f"<Unsupported message type {content.get('@type')}>"
        
        # Format timestamp
        timestamp = message.get("date")
        if timestamp is not None:
            dt = datetime.fromtimestamp(int(timestamp))
            time_str = dt.strftime("%H:%M:%S")
        else:
            time_str = "--:--:--"
        
        return {
            "timestamp": time_str,
            "sender": sender_name,
            "chat": chat_name,
            "text": message_text,
            "chat_id": chat_id
        }
    
    async def send_message(self, chat_identifier: str, text: str):
        """Send a message to a chat."""
        if not self.client or not is_authenticated:
            return {"success": False, "error": "Client not authenticated"}
        
        try:
            chat_id = None
            
            if chat_identifier.startswith("@"):
                # Resolve username
                username = chat_identifier[1:]
                self.client.send({"@type": "searchPublicChat", "username": username})
                
                # Wait for response (simplified - in production you'd want timeout)
                timeout = 10
                start_time = asyncio.get_event_loop().time()
                
                while asyncio.get_event_loop().time() - start_time < timeout:
                    update = await self.client.receive()
                    if (update.get("@type") == "chat" and 
                        update.get("username", "").lower() == username.lower()):
                        chat_id = update.get("id")
                        break
                    await asyncio.sleep(0.1)
            else:
                try:
                    chat_id = int(chat_identifier)
                except ValueError:
                    return {"success": False, "error": "Invalid chat identifier"}
            
            if chat_id is None:
                return {"success": False, "error": f"Could not resolve chat '{chat_identifier}'"}
            
            # Send message
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
            self.client.send(request)
            
            return {"success": True, "message": "Message sent successfully"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def broadcast_message(self, message):
        """Broadcast a message to all connected WebSocket clients."""
        if connected_websockets:
            message_data = {
                "type": "message",
                "data": message
            }
            disconnected = []
            for websocket in connected_websockets:
                try:
                    await websocket.send_text(json.dumps(message_data))
                except:
                    disconnected.append(websocket)
            
            # Remove disconnected clients
            for ws in disconnected:
                connected_websockets.remove(ws)
    
    async def broadcast_auth_status(self):
        """Broadcast authentication status to all connected clients."""
        if connected_websockets:
            status_data = {
                "type": "auth_status",
                "data": auth_status
            }
            disconnected = []
            for websocket in connected_websockets:
                try:
                    await websocket.send_text(json.dumps(status_data))
                except:
                    disconnected.append(websocket)
            
            # Remove disconnected clients
            for ws in disconnected:
                connected_websockets.remove(ws)


# Global client instance
telegram_web_client = TelegramWebClient()


@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    """Serve the main CLI-style interface."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time communication."""
    await websocket.accept()
    connected_websockets.append(websocket)
    
    # Send current auth status and message history
    try:
        await websocket.send_text(json.dumps({
            "type": "auth_status",
            "data": auth_status
        }))
        
        # Send recent message history
        for message in message_history[-20:]:  # Last 20 messages
            await websocket.send_text(json.dumps({
                "type": "message",
                "data": message
            }))
        
        while True:
            data = await websocket.receive_text()
            try:
                command = json.loads(data)
                
                if command["type"] == "authenticate":
                    api_id = command["data"]["api_id"]
                    api_hash = command["data"]["api_hash"]
                    phone = command["data"].get("phone")
                    
                    success = await telegram_web_client.start_client(api_id, api_hash, phone)
                    
                elif command["type"] == "send_message":
                    chat_id = command["data"]["chat_id"]
                    text = command["data"]["text"]
                    
                    result = await telegram_web_client.send_message(chat_id, text)
                    await websocket.send_text(json.dumps({
                        "type": "send_result",
                        "data": result
                    }))
                    
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "data": {"message": "Invalid JSON format"}
                }))
            except Exception as e:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "data": {"message": str(e)}
                }))
                
    except WebSocketDisconnect:
        connected_websockets.remove(websocket)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
