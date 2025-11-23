"""
Sport-specific city pages (SEO-optimized)
Routes: /skate-parks/{state}/{city}, /ice-rinks/{state}/{city}, etc.
"""

from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session, joinedload
from pathlib import Path
from app.database import get_db
from app.models.venue import Venue, SportType

router = APIRouter()
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


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
