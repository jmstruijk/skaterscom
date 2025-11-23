"""
Location routes for state and city hierarchy
"""

from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct
from pathlib import Path
from app.database import get_db
from app.models.venue import Venue, SportType
from app.dependencies import get_current_user_optional
from typing import Optional

router = APIRouter()
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

@router.get("/states", response_class=HTMLResponse)
async def list_states(request: Request, db: Session = Depends(get_db)):
    """List all states with venue counts"""
    # Valid US state codes (2 letters)
    us_states = ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 
                 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 
                 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 
                 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 
                 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY', 'DC']
    
    states = db.query(
        Venue.state,
        func.count(Venue.id).label('venue_count')
    ).filter(
        Venue.status == "ACTIVE",
        Venue.state.in_(us_states)
    ).group_by(
        Venue.state
    ).order_by(
        Venue.state
    ).all()
    
    current_user = get_current_user_optional(request, db)
    
    return templates.TemplateResponse(
        "states.html",
        {
            "request": request,
            "user": current_user,
            "states": [{"code": state, "venue_count": count} for state, count in states],
            "page_title": "Browse Skating Venues by State | Skaters.com",
            "meta_description": "Browse our comprehensive directory of skating venues across all 50 US states. Find skateparks, ice rinks, and roller rinks near you."
        }
    )

@router.get("/{state}", response_class=HTMLResponse)
async def state_detail(request: Request, state: str, db: Session = Depends(get_db)):
    """Show all cities in a state with venue counts"""
    from sqlalchemy.orm import joinedload
    from app.models.venue import VenuePhoto
    
    state_name = state.upper()
    
    # Get all cities in this state with venue counts
    cities = db.query(
        Venue.city,
        func.count(Venue.id).label('venue_count')
    ).filter(
        Venue.state == state_name,
        Venue.status == "ACTIVE"
    ).group_by(
        Venue.city
    ).order_by(
        Venue.city
    ).all()
    
    # Get featured venues from this state with their photos
    featured_venues = db.query(Venue)\
        .options(joinedload(Venue.photos))\
        .filter(
            Venue.state == state_name,
            Venue.status == "ACTIVE"
        ).order_by(
            Venue.rating.desc()
        ).limit(5).all()
    
    # Process venues to include photo URLs
    processed_venues = []
    for venue in featured_venues:
        # Get primary photo or first available
        photo = next((p for p in venue.photos if p.is_primary), 
                    venue.photos[0] if venue.photos else None)
        
        # Build image URL
        image_url = None
        if photo:
            if 'maxwidth=' not in photo.url:
                image_url = f"{photo.url}?maxwidth=800" if '?' not in photo.url else f"{photo.url}&maxwidth=800"
            else:
                image_url = photo.url
        
        processed_venues.append({
            "name": venue.name,
            "slug": venue.slug,
            "city": venue.city,
            "sport_type": venue.sport_type.value,
            "rating": venue.rating,
            "review_count": venue.review_count,
            "image_url": image_url or f"https://picsum.photos/seed/{venue.slug}/800/600?grayscale"
        })
    
    current_user = get_current_user_optional(request, db)
    
    return templates.TemplateResponse(
        "state_detail.html",
        {
            "request": request,
            "user": current_user,
            "state_code": state_name,
            "cities": [{"name": city, "venue_count": count, "slug": city.lower().replace(' ', '-')} for city, count in cities],
            "featured_venues": processed_venues,
            "page_title": f"Skating Venues in {state_name} | Skaters.com",
            "meta_description": f"Find the best skating venues in {state_name}. Browse our directory of skateparks, ice rinks, and roller rinks across {state_name}."
        }
    )

@router.get("/{state}/{city}", response_class=HTMLResponse)
async def city_venues(request: Request, state: str, city: str, db: Session = Depends(get_db)):
    """Show all venues in a specific city"""
    from sqlalchemy.orm import joinedload
    
    state_code = state.upper()
    
    # Get all venues in this city with their photos
    venues = db.query(Venue)\
        .options(joinedload(Venue.photos))\
        .filter(
            Venue.state == state_code,
            Venue.city.ilike(city.replace('-', ' ')),
            Venue.status == "ACTIVE"
        ).order_by(
            Venue.rating.desc()
        ).all()
    
    if not venues:
        raise HTTPException(status_code=404, detail="No venues found in this location")
    
    # Get unique sport types in this city
    sport_types = db.query(
        Venue.sport_type
    ).filter(
        Venue.state == state_code,
        Venue.city.ilike(city.replace('-', ' ')),
        Venue.status == "ACTIVE"
    ).distinct().all()
    
    # Process venues to include photo URLs
    processed_venues = []
    for venue in venues:
        # Get primary photo or first available
        photo = next((p for p in venue.photos if p.is_primary), 
                    venue.photos[0] if venue.photos else None)
        
        # Build image URL
        image_url = None
        if photo:
            if 'maxwidth=' not in photo.url:
                image_url = f"{photo.url}?maxwidth=800" if '?' not in photo.url else f"{photo.url}&maxwidth=800"
            else:
                image_url = photo.url
        
        processed_venues.append({
            "name": venue.name,
            "slug": venue.slug,
            "sport_type": venue.sport_type.value,
            "address": venue.address,
            "rating": venue.rating,
            "review_count": venue.review_count,
            "description": venue.description[:150] + '...' if venue.description else '',
            "image_url": image_url or f"https://picsum.photos/seed/{venue.slug}/800/600?grayscale",
            "latitude": venue.latitude,
            "longitude": venue.longitude
        })
    
    current_user = get_current_user_optional(request, db)
    
    return templates.TemplateResponse(
        "city_venues.html",
        {
            "request": request,
            "user": current_user,
            "state_code": state_code,
            "city": city.replace('-', ' ').title(),
            "venues": processed_venues,
            "sport_types": [st[0].value for st in sport_types],
            "page_title": f"Skating Venues in {city.replace('-', ' ').title()}, {state_code} | Skaters.com",
            "meta_description": f"Find the best skating venues in {city.replace('-', ' ').title()}, {state_code}. Browse our directory of skateparks, ice rinks, and roller rinks in the area."
        }
    )

@router.get("/skate-parks/{state}/{city}", response_class=HTMLResponse)
async def city_skate_parks(request: Request, state: str, city: str, db: Session = Depends(get_db)):
    """SEO-optimized page for skate parks in a specific city"""
    return await _sport_city_page(request, state, city, SportType.SKATEBOARDING, db)

@router.get("/ice-rinks/{state}/{city}", response_class=HTMLResponse)
async def city_ice_rinks(request: Request, state: str, city: str, db: Session = Depends(get_db)):
    """SEO-optimized page for ice rinks in a specific city"""
    return await _sport_city_page(request, state, city, SportType.ICE_SKATING, db)

@router.get("/roller-rinks/{state}/{city}", response_class=HTMLResponse)
async def city_roller_rinks(request: Request, state: str, city: str, db: Session = Depends(get_db)):
    """SEO-optimized page for roller rinks in a specific city"""
    return await _sport_city_page(request, state, city, SportType.ROLLER_SKATING, db)

async def _sport_city_page(request: Request, state: str, city: str, sport_type: SportType, db: Session):
    """Helper function for sport-specific city pages"""
    from sqlalchemy.orm import joinedload
    
    state_code = state.upper()
    city_name = city.replace('-', ' ').title()
    
    # Map sport type to friendly names
    sport_names = {
        SportType.SKATEBOARDING: {"singular": "Skate Park", "plural": "Skate Parks", "keyword": "skate park"},
        SportType.ICE_SKATING: {"singular": "Ice Rink", "plural": "Ice Rinks", "keyword": "ice rink"},
        SportType.ROLLER_SKATING: {"singular": "Roller Rink", "plural": "Roller Rinks", "keyword": "roller rink"},
        SportType.INLINE_SKATING: {"singular": "Inline Skating", "plural": "Inline Skating Venues", "keyword": "inline skating"}
    }
    
    sport_info = sport_names.get(sport_type, {"singular": "Venue", "plural": "Venues", "keyword": "venue"})
    
    # Get all venues of this sport type in this city
    venues = db.query(Venue)\
        .options(joinedload(Venue.photos))\
        .filter(
            Venue.state == state_code,
            Venue.city.ilike(city.replace('-', ' ')),
            Venue.sport_type == sport_type,
            Venue.status == "ACTIVE"
        ).order_by(
            Venue.rating.desc()
        ).all()
    
    if not venues:
        raise HTTPException(status_code=404, detail=f"No {sport_info['plural'].lower()} found in {city_name}, {state_code}")
    
    # Calculate stats
    total_venues = len(venues)
    avg_rating = sum(v.rating for v in venues) / total_venues if total_venues > 0 else 0
    total_reviews = sum(v.review_count for v in venues)
    
    # Process venues
    processed_venues = []
    for venue in venues:
        photo = next((p for p in venue.photos if p.is_primary), 
                    venue.photos[0] if venue.photos else None)
        
        image_url = None
        if photo:
            if 'maxwidth=' in photo.url:
                image_url = photo.url.replace('maxwidth=1600', 'maxwidth=400').replace('maxwidth=800', 'maxwidth=400')
            elif '?' in photo.url:
                image_url = f"{photo.url}&maxwidth=400"
            else:
                image_url = f"{photo.url}?maxwidth=400"
        
        processed_venues.append({
            "name": venue.name,
            "slug": venue.slug,
            "address": venue.address,
            "rating": venue.rating,
            "review_count": venue.review_count,
            "description": venue.description[:150] + '...' if venue.description else '',
            "image_url": image_url or f"https://picsum.photos/seed/{venue.slug}/400/300?grayscale",
            "latitude": venue.latitude,
            "longitude": venue.longitude
        })
    
    # SEO-optimized meta tags
    page_title = f"{total_venues} Best {sport_info['plural']} in {city_name}, {state_code} (2024) | Skaters.com"
    meta_description = f"Find the top-rated {sport_info['plural'].lower()} in {city_name}, {state_code}. Browse {total_venues} venues with photos, reviews, addresses, and hours. Indoor & outdoor options."
    
    # Create FAQ schema
    faq_items = [
        {
            "question": f"How many {sport_info['plural'].lower()} are in {city_name}?",
            "answer": f"There are {total_venues} {sport_info['plural'].lower()} in {city_name}, {state_code} with an average rating of {avg_rating:.1f} stars."
        },
        {
            "question": f"What is the best {sport_info['singular'].lower()} in {city_name}?",
            "answer": f"{venues[0].name} is the highest-rated {sport_info['singular'].lower()} in {city_name} with {venues[0].rating} stars and {venues[0].review_count} reviews."
        },
        {
            "question": f"Are there indoor {sport_info['plural'].lower()} in {city_name}?",
            "answer": f"Yes, several {sport_info['plural'].lower()} in {city_name} offer indoor facilities. Check individual venue details for specific amenities."
        }
    ]
    
    return templates.TemplateResponse(
        "sport_city_page.html",
        {
            "request": request,
            "state_code": state_code,
            "city": city_name,
            "sport_type": sport_type.value,
            "sport_singular": sport_info["singular"],
            "sport_plural": sport_info["plural"],
            "sport_keyword": sport_info["keyword"],
            "venues": processed_venues,
            "total_venues": total_venues,
            "avg_rating": round(avg_rating, 1),
            "total_reviews": total_reviews,
            "faq_items": faq_items,
            "page_title": page_title,
            "meta_description": meta_description
        }
    )
