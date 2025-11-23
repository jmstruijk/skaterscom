"""
Flash message system for user feedback
"""

from fastapi import Request
from typing import Literal

MessageType = Literal["success", "error", "warning", "info"]


def flash(request: Request, message: str, category: MessageType = "info"):
    """Add a flash message to the session"""
    if "_messages" not in request.session:
        request.session["_messages"] = []
    request.session["_messages"].append({"message": message, "category": category})


def get_flashed_messages(request: Request) -> list:
    """Get and clear flash messages from session"""
    # Check if session is available
    if "session" not in request.scope:
        return []
    
    messages = request.session.pop("_messages", [])
    return messages
