"""
User dashboard routes
"""

from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pathlib import Path
from app.database import get_db
from app.models.venue import User, Review, SavedVenue, Venue
from app.dependencies import require_auth
from datetime import datetime

router = APIRouter()
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@router.get("", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """User dashboard - requires authentication"""
    
    user = current_user
    
    # Get user stats
    saved_count = db.query(SavedVenue).filter(SavedVenue.user_id == user.id).count()
    reviews_count = db.query(Review).filter(Review.user_id == user.id).count()
    
    # Get recent reviews
    recent_reviews = db.query(Review).filter(Review.user_id == user.id).order_by(Review.created_at.desc()).limit(5).all()
    
    reviews_data = []
    for review in recent_reviews:
        venue = db.query(Venue).filter(Venue.id == review.venue_id).first()
        if venue:
            reviews_data.append({
                "venue_name": venue.name,
                "venue_slug": venue.slug,
                "rating": review.rating,
                "title": review.title,
                "comment": review.comment,
                "approved": review.approved,
                "created_at": review.created_at
            })
    
    # Get saved venues
    saved_venues_query = db.query(SavedVenue).filter(SavedVenue.user_id == user.id).limit(4).all()
    saved_venues = []
    for saved in saved_venues_query:
        venue = db.query(Venue).filter(Venue.id == saved.venue_id).first()
        if venue:
            saved_venues.append({
                "name": venue.name,
                "slug": venue.slug,
                "city": venue.city,
                "state": venue.state,
                "rating": venue.rating
            })
    
    stats = {
        "saved_venues": saved_count,
        "reviews": reviews_count,
        "visited": reviews_count,  # Assume visited = reviewed
    }
    
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "user": user,
            "stats": stats,
            "recent_reviews": reviews_data,
            "saved_venues": saved_venues,
            "page_title": f"Dashboard | {user.full_name} | Skaters.com",
            "meta_description": "Manage your skating venue reviews and favorites"
        }
    )
