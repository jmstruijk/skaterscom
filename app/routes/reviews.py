"""
Review routes
"""

from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pathlib import Path
from app.database import get_db
from app.models.venue import Review, Venue, User
from app.dependencies import require_auth
from datetime import datetime

router = APIRouter()
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@router.post("/submit")
async def submit_review(
    venue_id: int = Form(...),
    rating: int = Form(...),
    title: str = Form(""),
    comment: str = Form(...),
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Submit a new review - requires authentication"""
    
    user = current_user
    
    # Validate rating
    if rating < 1 or rating > 5:
        return RedirectResponse(url=f"/venues/{venue_id}?error=invalid_rating", status_code=303)
    
    # Get venue
    venue = db.query(Venue).filter(Venue.id == venue_id).first()
    if not venue:
        return RedirectResponse(url="/", status_code=303)
    
    # Create review
    new_review = Review(
        venue_id=venue_id,
        user_id=user.id,
        rating=rating,
        title=title if title else None,
        comment=comment,
        approved=False,  # Requires moderation
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(new_review)
    
    # Update venue rating (simple average for now)
    all_reviews = db.query(Review).filter(Review.venue_id == venue_id, Review.approved == True).all()
    if all_reviews:
        total_rating = sum(r.rating for r in all_reviews)
        venue.rating = round(total_rating / len(all_reviews), 1)
        venue.review_count = len(all_reviews)
    
    db.commit()
    
    # Redirect back to venue with success message
    return RedirectResponse(url=f"/venues/{venue.slug}?review=submitted", status_code=303)


@router.get("/add/{venue_slug}", response_class=HTMLResponse)
async def new_review_form(
    request: Request,
    venue_slug: str,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Display review submission form - requires authentication"""
    
    user = current_user
    
    # Get venue
    venue = db.query(Venue).filter(Venue.slug == venue_slug).first()
    if not venue:
        return RedirectResponse(url="/", status_code=303)
    
    return templates.TemplateResponse(
        "review_form.html",
        {
            "request": request,
            "venue": {
                "id": venue.id,
                "name": venue.name,
                "slug": venue.slug,
                "city": venue.city,
                "state": venue.state
            },
            "user": user,
            "page_title": f"Write Review for {venue.name} | Skaters.com",
            "meta_description": f"Share your experience at {venue.name}"
        }
    )
