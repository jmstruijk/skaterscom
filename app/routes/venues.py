"""
Venue routes for displaying venue details
"""

from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pathlib import Path
from app.database import get_db
from app.models.venue import Venue, VenuePhoto, VenueAmenity, VenueHours, VenuePricing, SavedVenue, User
from app.dependencies import require_auth, get_current_user_optional
from datetime import datetime

router = APIRouter()
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@router.get("/{slug}", response_class=HTMLResponse)
async def venue_detail(request: Request, slug: str, db: Session = Depends(get_db)):
    """Display venue detail page - Server-side rendered for SEO"""
    
    # Query database for venue
    venue = db.query(Venue).filter(Venue.slug == slug).first()
    
    if not venue:
        raise HTTPException(status_code=404, detail="Venue not found")
    
    # Load relationships
    photos = db.query(VenuePhoto).filter(VenuePhoto.venue_id == venue.id).order_by(VenuePhoto.is_primary.desc()).all()
    amenities = db.query(VenueAmenity).filter(VenueAmenity.venue_id == venue.id).all()
    hours = db.query(VenueHours).filter(VenueHours.venue_id == venue.id).first()
    pricing = db.query(VenuePricing).filter(VenuePricing.venue_id == venue.id).first()
    
    # Process photos - ensure primary photo is first
    photo_list = []
    for p in photos:
        # Ensure the URL has the maxwidth parameter set to 1600 for better quality
        photo_url = p.url
        if 'maxwidth=' not in photo_url:
            if '?' in photo_url:
                photo_url += '&maxwidth=1600'
            else:
                photo_url += '?maxwidth=1600'
        
        photo_list.append({
            "url": photo_url, 
            "caption": p.caption or f"{venue.name} - {venue.city}, {venue.state}",
            "is_primary": p.is_primary
        })
    
    # Convert to dict for template
    venue_data = {
        "id": venue.id,
        "name": venue.name,
        "slug": venue.slug,
        "sport_type": venue.sport_type.value,
        "city": venue.city,
        "state": venue.state,
        "address": venue.address,
        "zip_code": venue.zip_code,
        "latitude": venue.latitude,
        "longitude": venue.longitude,
        "rating": venue.rating,
        "review_count": venue.review_count,
        "description": venue.description,
        "phone": venue.phone,
        "website": venue.website,
        "year_opened": venue.year_opened,
        "verified": venue.verified,
        "amenities": [{"name": a.amenity_name, "available": a.available} for a in amenities],
        "photos": photo_list,
        "hours": {
            "monday": hours.monday if hours else None,
            "tuesday": hours.tuesday if hours else None,
            "wednesday": hours.wednesday if hours else None,
            "thursday": hours.thursday if hours else None,
            "friday": hours.friday if hours else None,
            "saturday": hours.saturday if hours else None,
            "sunday": hours.sunday if hours else None,
        } if hours else None,
        "pricing": {
            "admission": pricing.admission,
            "rental": pricing.rental,
        } if pricing and (pricing.admission or pricing.rental) else None
    }
    
    # Get current user for navigation
    current_user = get_current_user_optional(request, db)
    
    return templates.TemplateResponse(
        "venue_detail.html",
        {
            "request": request,
            "user": current_user,
            "venue": venue_data,
            "page_title": f"{venue.name} | {venue.city}, {venue.state} | Skaters.com",
            "meta_description": venue.description
        }
    )


@router.get("/", response_class=HTMLResponse)
async def list_venues(
    request: Request,
    sport_type: str = None,
    city: str = None,
    state: str = None,
    db: Session = Depends(get_db)
):
    """List all venues with optional filters"""
    
    query = db.query(Venue).filter(Venue.status == "ACTIVE")
    
    if sport_type:
        query = query.filter(Venue.sport_type == sport_type)
    if city:
        query = query.filter(Venue.city.ilike(f"%{city}%"))
    if state:
        query = query.filter(Venue.state == state.upper())
    
    venues = query.order_by(Venue.rating.desc()).limit(50).all()
    
    venues_data = [
        {
            "id": v.id,
            "name": v.name,
            "slug": v.slug,
            "city": v.city,
            "state": v.state,
            "sport_type": v.sport_type.value,
            "rating": v.rating,
            "review_count": v.review_count,
            "description": v.description,
            "image_url": f"https://picsum.photos/seed/{v.slug}/400/300"
        }
        for v in venues
    ]
    
    return templates.TemplateResponse(
        "venues_list.html",
        {
            "request": request,
            "venues": venues_data,
            "page_title": "All Venues | Skaters.com",
            "meta_description": "Browse all skating venues"
        }
    )


@router.post("/{venue_id}/save", response_class=JSONResponse)
async def save_venue(
    venue_id: int,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Save a venue to user's favorites - requires authentication"""
    
    # Check if venue exists
    venue = db.query(Venue).filter(Venue.id == venue_id).first()
    if not venue:
        return JSONResponse(
            status_code=404,
            content={"success": False, "message": "Venue not found"}
        )
    
    # Check if already saved
    existing = db.query(SavedVenue).filter(
        SavedVenue.user_id == current_user.id,
        SavedVenue.venue_id == venue_id
    ).first()
    
    if existing:
        # Already saved, so unsave it
        db.delete(existing)
        db.commit()
        return JSONResponse(
            content={"success": True, "message": "Venue removed from favorites", "saved": False}
        )
    
    # Save the venue
    saved_venue = SavedVenue(
        user_id=current_user.id,
        venue_id=venue_id,
        created_at=datetime.utcnow()
    )
    db.add(saved_venue)
    db.commit()
    
    return JSONResponse(
        content={"success": True, "message": "Venue saved to favorites!", "saved": True}
    )
