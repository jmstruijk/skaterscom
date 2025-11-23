"""
CSRF Protection for forms
"""

from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from fastapi import Request, HTTPException
import os

# Secret key for CSRF tokens
SECRET_KEY = os.getenv("SECRET_KEY", "skaters-secret-key-change-in-production-please")
serializer = URLSafeTimedSerializer(SECRET_KEY)


def generate_csrf_token(request: Request) -> str:
    """Generate a CSRF token for the current session"""
    # Check if session is available
    if "session" not in request.scope:
        # Return empty token for static files
        return ""
    
    # Use session ID or create a unique identifier
    session_id = request.session.get("_csrf_session_id")
    if not session_id:
        import secrets
        session_id = secrets.token_urlsafe(32)
        request.session["_csrf_session_id"] = session_id
    
    # Generate token
    token = serializer.dumps(session_id)
    return token


def validate_csrf_token(request: Request, token: str, max_age: int = 3600) -> bool:
    """Validate a CSRF token"""
    try:
        session_id = request.session.get("_csrf_session_id")
        if not session_id:
            return False
        
        # Verify token
        data = serializer.loads(token, max_age=max_age)
        return data == session_id
    except (BadSignature, SignatureExpired):
        return False


def require_csrf(request: Request, token: str):
    """Require valid CSRF token or raise HTTPException"""
    if not validate_csrf_token(request, token):
        raise HTTPException(status_code=403, detail="Invalid CSRF token")
