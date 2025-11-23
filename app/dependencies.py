"""
Authentication and authorization dependencies
"""

from fastapi import Request, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.venue import User
from typing import Optional


def get_current_user(request: Request, db: Session = Depends(get_db)) -> Optional[User]:
    """
    Get the currently logged-in user from session.
    Returns None if not authenticated.
    """
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    
    user = db.query(User).filter(User.id == user_id).first()
    return user


def require_auth(request: Request, db: Session = Depends(get_db)) -> User:
    """
    Require user to be authenticated.
    Raises 401 if not logged in.
    """
    user = get_current_user(request, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please log in.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been deactivated."
        )
    
    return user


def require_admin(request: Request, db: Session = Depends(get_db)) -> User:
    """
    Require user to be an admin.
    Raises 401 if not logged in, 403 if not admin.
    """
    user = require_auth(request, db)
    
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required."
        )
    
    return user


def get_current_user_optional(request: Request, db: Session = Depends(get_db)) -> Optional[User]:
    """
    Get current user if logged in, None otherwise.
    Useful for pages that work both logged in and out.
    """
    return get_current_user(request, db)
