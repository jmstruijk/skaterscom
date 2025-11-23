"""
Utility functions for the application
"""

from fastapi import Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Dict, Any
from app.dependencies import get_current_user_optional


def render_template(
    templates: Jinja2Templates,
    request: Request,
    template_name: str,
    context: Dict[str, Any],
    db: Session
):
    """
    Render a template with automatic user context injection.
    
    Args:
        templates: Jinja2Templates instance
        request: FastAPI Request object
        template_name: Name of the template file
        context: Template context dictionary
        db: Database session
    
    Returns:
        TemplateResponse with user context injected
    """
    # Get current user for navigation
    current_user = get_current_user_optional(request, db)
    
    # Inject standard context
    context["request"] = request
    context["user"] = current_user
    
    return templates.TemplateResponse(template_name, context)
