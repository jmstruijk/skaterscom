"""
Authentication routes
"""

from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pathlib import Path
from app.database import get_db
from app.models.venue import User
from app.auth import hash_password, verify_password, get_user_by_username, get_user_by_email
from app.flash import flash, get_flashed_messages
from app.csrf import require_csrf
from slugify import slugify
import re

router = APIRouter()
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Display login page - Currently in maintenance"""
    return templates.TemplateResponse(
        "maintenance.html",
        {
            "request": request,
            "page_title": "Login - Under Maintenance | Skaters.com",
            "meta_description": "Login is temporarily unavailable",
            "feature_name": "Login",
            "message": "We're working on improving our user authentication system. Please check back soon!"
        }
    )


@router.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    csrf_token: str = Form(...),
    db: Session = Depends(get_db)
):
    """Handle login"""
    
    # Validate CSRF token
    require_csrf(request, csrf_token)
    
    # Try to find user by username or email
    user = get_user_by_username(db, username)
    if not user:
        user = get_user_by_email(db, username)
    
    # Verify credentials
    if not user or not verify_password(password, user.hashed_password):
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error": "Invalid username or password",
                "page_title": "Login | Skaters.com",
                "meta_description": "Sign in to your Skaters.com account"
            }
        )
    
    # Check if user is active
    if not user.is_active:
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error": "Your account has been deactivated",
                "page_title": "Login | Skaters.com",
                "meta_description": "Sign in to your Skaters.com account"
            }
        )
    
    # Set session
    request.session["user_id"] = user.id
    request.session["username"] = user.username
    request.session["email"] = user.email
    
    # Add success message
    flash(request, f"Welcome back, {user.username}!", "success")
    
    # Get next URL from query params or default to homepage
    next_url = request.query_params.get("next", "/")
    response = RedirectResponse(url=next_url, status_code=303)
    return response


@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """Display registration page - Currently in maintenance"""
    return templates.TemplateResponse(
        "maintenance.html",
        {
            "request": request,
            "page_title": "Registration - Under Maintenance | Skaters.com",
            "meta_description": "Registration is temporarily unavailable",
            "feature_name": "Registration",
            "message": "We're working on improving our user registration system. Please check back soon!"
        }
    )


@router.post("/register")
async def register(
    request: Request,
    full_name: str = Form(...),
    email: str = Form(...),
    username: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    csrf_token: str = Form(...),
    db: Session = Depends(get_db)
):
    """Handle registration"""
    
    # Validate CSRF token
    require_csrf(request, csrf_token)
    
    # Validate email format
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return templates.TemplateResponse(
            "register.html",
            {
                "request": request,
                "error": "Invalid email format",
                "page_title": "Create Account | Skaters.com",
                "meta_description": "Join Skaters.com"
            }
        )
    
    # Validate passwords match
    if password != confirm_password:
        return templates.TemplateResponse(
            "register.html",
            {
                "request": request,
                "error": "Passwords do not match",
                "page_title": "Create Account | Skaters.com",
                "meta_description": "Join Skaters.com"
            }
        )
    
    # Validate password strength
    if len(password) < 8:
        return templates.TemplateResponse(
            "register.html",
            {
                "request": request,
                "error": "Password must be at least 8 characters long",
                "page_title": "Create Account | Skaters.com",
                "meta_description": "Join Skaters.com"
            }
        )
    
    if not any(c.isupper() for c in password):
        return templates.TemplateResponse(
            "register.html",
            {
                "request": request,
                "error": "Password must contain at least one uppercase letter",
                "page_title": "Create Account | Skaters.com",
                "meta_description": "Join Skaters.com"
            }
        )
    
    if not any(c.islower() for c in password):
        return templates.TemplateResponse(
            "register.html",
            {
                "request": request,
                "error": "Password must contain at least one lowercase letter",
                "page_title": "Create Account | Skaters.com",
                "meta_description": "Join Skaters.com"
            }
        )
    
    if not any(c.isdigit() for c in password):
        return templates.TemplateResponse(
            "register.html",
            {
                "request": request,
                "error": "Password must contain at least one number",
                "page_title": "Create Account | Skaters.com",
                "meta_description": "Join Skaters.com"
            }
        )
    
    # Check if username exists
    if get_user_by_username(db, username):
        return templates.TemplateResponse(
            "register.html",
            {
                "request": request,
                "error": "Username already taken",
                "page_title": "Create Account | Skaters.com",
                "meta_description": "Join Skaters.com"
            }
        )
    
    # Check if email exists
    if get_user_by_email(db, email):
        return templates.TemplateResponse(
            "register.html",
            {
                "request": request,
                "error": "Email already registered",
                "page_title": "Create Account | Skaters.com",
                "meta_description": "Join Skaters.com"
            }
        )
    
    # Create new user
    new_user = User(
        email=email,
        username=username,
        hashed_password=hash_password(password),
        full_name=full_name,
        is_active=True,
        is_admin=False
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Redirect to login with success message
    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "success": "Account created successfully! Please sign in.",
            "page_title": "Login | Skaters.com",
            "meta_description": "Sign in to your Skaters.com account"
        }
    )


@router.get("/logout")
async def logout(request: Request):
    """Handle logout"""
    # Add success message before clearing session
    flash(request, "You have been logged out successfully", "success")
    request.session.clear()
    response = RedirectResponse(url="/", status_code=303)
    return response
