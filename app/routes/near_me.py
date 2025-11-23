"""
Near Me routes for geolocation-based venue discovery
Targets high-volume "near me" keywords (201,000+ monthly searches)
"""

from fastapi import APIRouter, Request, Depends, Query
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func
from pathlib import Path
from typing import Optional
from app.database import get_db
from app.models.venue import Venue, SportType
import math

router = APIRouter()
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two coordinates using Haversine formula (in miles)"""
    R = 3959  # Earth's radius in miles
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    return R * c

@router.get("/ice-rinks", response_class=HTMLResponse)
async def ice_rinks_hub(request: Request):
    """Ice rinks hub page - targets 'ice rink ice' keyword (110,000 monthly searches)"""
    return templates.TemplateResponse(
        "ice_rinks_hub.html",
        {
            "request": request,
            "page_title": "Ice Rinks - Find Ice Skating Rinks Near You | Skaters.com",
            "meta_description": "Discover ice rinks near you. Find indoor and outdoor ice skating facilities for hockey, figure skating, and recreational fun. Browse by location with ratings and reviews."
        }
    )

@router.get("/skate-parks", response_class=HTMLResponse)
async def skate_parks_hub(request: Request):
    """Skate parks hub page - targets 'skate park' keyword (301,000 monthly searches)"""
    return templates.TemplateResponse(
        "skate_parks_hub.html",
        {
            "request": request,
            "page_title": "Skate Parks - Find Skateboarding Venues Near You | Skaters.com",
            "meta_description": "Discover skate parks near you. Find indoor and outdoor skateboarding venues with ramps, bowls, and street features. Browse by location with ratings and reviews."
        }
    )

@router.get("/roller-rinks", response_class=HTMLResponse)
async def roller_rinks_hub(request: Request):
    """Roller rinks hub page"""
    return templates.TemplateResponse(
        "roller_rinks_hub.html",
        {
            "request": request,
            "page_title": "Roller Rinks - Find Roller Skating Rinks Near You | Skaters.com",
            "meta_description": "Discover roller skating rinks near you. Find indoor and outdoor roller rinks for recreational skating, parties, and events. Browse by location with ratings and reviews."
        }
    )

@router.get("/inline-skating", response_class=HTMLResponse)
async def inline_skating_hub(request: Request):
    """Inline skating hub page"""
    return templates.TemplateResponse(
        "inline_skating_hub.html",
        {
            "request": request,
            "page_title": "Inline Skating - Find Inline Skating Venues Near You | Skaters.com",
            "meta_description": "Discover inline skating venues near you. Find paved trails, boardwalks, and skate parks for inline skating. Browse by location with ratings and reviews."
        }
    )

@router.get("/inline-skating/near-me", response_class=HTMLResponse)
async def inline_skating_near_me(request: Request):
    """SEO-optimized landing page for inline skating near me"""
    return templates.TemplateResponse(
        "near_me_generic.html",
        {
            "request": request,
            "sport_type": "inline_skating",
            "sport_title": "Inline Skating Venues",
            "page_title": "Find Inline Skating Venues Near You | Skaters.com",
            "meta_description": "Discover inline skating venues near your location. Find the best inline skating spots with directions, hours, and reviews."
        }
    )

@router.get("/indoor-roller-rinks/near-me", response_class=HTMLResponse)
async def indoor_roller_rinks_near_me(request: Request):
    """SEO-optimized landing page for indoor roller rinks near me"""
    return templates.TemplateResponse(
        "near_me_generic.html",
        {
            "request": request,
            "sport_type": "roller_skating",
            "sport_title": "Indoor Roller Rinks",
            "page_title": "Find Indoor Roller Rinks Near You | Skaters.com",
            "meta_description": "Discover indoor roller skating rinks near your location. Find the best indoor roller rinks with directions, hours, and reviews."
        }
    )

@router.get("/outdoor-roller-rinks/near-me", response_class=HTMLResponse)
async def outdoor_roller_rinks_near_me(request: Request):
    """SEO-optimized landing page for outdoor roller rinks near me"""
    return templates.TemplateResponse(
        "near_me_generic.html",
        {
            "request": request,
            "sport_type": "roller_skating",
            "sport_title": "Outdoor Roller Rinks",
            "page_title": "Find Outdoor Roller Rinks Near You | Skaters.com",
            "meta_description": "Discover outdoor roller skating rinks near your location. Find the best outdoor roller rinks with directions, hours, and reviews."
        }
    )

@router.get("/near-me", response_class=HTMLResponse)
async def near_me_landing(request: Request):
    """Landing page for near me searches with geolocation prompt"""
    return templates.TemplateResponse(
        "near_me.html",
        {
            "request": request,
            "page_title": "Skate Parks & Ice Rinks Near Me | Skaters.com",
            "meta_description": "Find skate parks, ice rinks, and roller rinks near your location. Get directions, hours, reviews, and photos for skating facilities near you."
        }
    )

@router.get("/api/venues/nearby", response_class=JSONResponse)
async def find_nearby_venues(
    lat: float = Query(..., description="User latitude"),
    lng: float = Query(..., description="User longitude"),
    radius: int = Query(100, description="Search radius in miles"),
    sport_type: Optional[str] = Query(None, description="Filter by sport type"),
    limit: int = Query(50, description="Maximum number of results"),
    db: Session = Depends(get_db)
):
    """API endpoint to find venues near a location"""
    
    # Build query
    query = db.query(Venue).filter(
        Venue.status == "ACTIVE",
        Venue.latitude.isnot(None),
        Venue.longitude.isnot(None)
    )
    
    # Filter by sport type if specified
    if sport_type:
        try:
            sport_enum = SportType(sport_type)
            query = query.filter(Venue.sport_type == sport_enum)
        except ValueError:
            pass
    
    # Get all venues (we'll filter by distance in Python)
    all_venues = query.all()
    
    # Calculate distances and filter
    nearby_venues = []
    for venue in all_venues:
        distance = calculate_distance(lat, lng, venue.latitude, venue.longitude)
        if distance <= radius:
            nearby_venues.append({
                "id": venue.id,
                "name": venue.name,
                "slug": venue.slug,
                "sport_type": venue.sport_type.value,
                "address": venue.address,
                "city": venue.city,
                "state": venue.state,
                "latitude": venue.latitude,
                "longitude": venue.longitude,
                "rating": venue.rating,
                "review_count": venue.review_count,
                "distance": round(distance, 1)
            })
    
    # Sort by distance
    nearby_venues.sort(key=lambda x: x['distance'])
    
    # Limit results
    nearby_venues = nearby_venues[:limit]
    
    return {
        "success": True,
        "count": len(nearby_venues),
        "venues": nearby_venues,
        "search_params": {
            "latitude": lat,
            "longitude": lng,
            "radius": radius,
            "sport_type": sport_type
        }
    }

@router.get("/skate-parks/near-me", response_class=HTMLResponse)
async def skate_parks_near_me(request: Request):
    """SEO-optimized landing page for skate parks near me"""
    return templates.TemplateResponse(
        "sport_near_me.html",
        {
            "request": request,
            "sport_type": "skateboarding",
            "sport_singular": "Skate Park",
            "sport_plural": "Skate Parks",
            "sport_keyword": "skate park",
            "page_title": "Skate Parks Near Me | Find Local Skateparks | Skaters.com",
            "meta_description": "Find skate parks near your location. Browse local skateparks with ratings, reviews, photos, and directions. Indoor and outdoor options available."
        }
    )

@router.get("/ice-rinks/near-me", response_class=HTMLResponse)
async def ice_rinks_near_me(request: Request):
    """SEO-optimized landing page for ice rinks near me"""
    return templates.TemplateResponse(
        "sport_near_me.html",
        {
            "request": request,
            "sport_type": "ice_skating",
            "sport_singular": "Ice Rink",
            "sport_plural": "Ice Rinks",
            "sport_keyword": "ice rink",
            "page_title": "Ice Rinks Near Me | Find Local Ice Skating Rinks | Skaters.com",
            "meta_description": "Find ice rinks near your location. Browse local ice skating rinks with ratings, reviews, photos, and directions. Public skate times and lessons available."
        }
    )

@router.get("/roller-rinks/near-me", response_class=HTMLResponse)
async def roller_rinks_near_me(request: Request):
    """SEO-optimized landing page for roller rinks near me"""
    return templates.TemplateResponse(
        "sport_near_me.html",
        {
            "request": request,
            "sport_type": "roller_skating",
            "sport_singular": "Roller Rink",
            "sport_plural": "Roller Rinks",
            "sport_keyword": "roller rink",
            "page_title": "Roller Rinks Near Me | Find Local Roller Skating Rinks | Skaters.com",
            "meta_description": "Find roller rinks near your location. Browse local roller skating rinks with ratings, reviews, photos, and directions. Family-friendly skating sessions."
        }
    )

@router.get("/indoor-skate-parks/near-me", response_class=HTMLResponse)
async def indoor_skate_parks_near_me(request: Request):
    """SEO-optimized landing page for indoor skate parks near me (18,100 monthly searches, SD: 11)"""
    return templates.TemplateResponse(
        "sport_near_me.html",
        {
            "request": request,
            "sport_type": "skateboarding",
            "sport_singular": "Indoor Skate Park",
            "sport_plural": "Indoor Skate Parks",
            "sport_keyword": "indoor skate park",
            "indoor_only": True,
            "page_title": "Indoor Skate Parks Near Me | Find Indoor Skateparks | Skaters.com",
            "meta_description": "Find indoor skate parks near your location. Browse climate-controlled skateparks with ratings, reviews, and photos. Skate year-round regardless of weather."
        }
    )

@router.get("/outdoor-skate-parks/near-me", response_class=HTMLResponse)
async def outdoor_skate_parks_near_me(request: Request):
    """SEO-optimized landing page for outdoor skate parks near me"""
    return templates.TemplateResponse(
        "sport_near_me.html",
        {
            "request": request,
            "sport_type": "skateboarding",
            "sport_singular": "Outdoor Skate Park",
            "sport_plural": "Outdoor Skate Parks",
            "sport_keyword": "outdoor skate park",
            "outdoor_only": True,
            "page_title": "Outdoor Skate Parks Near Me | Find Outdoor Skateparks | Skaters.com",
            "meta_description": "Find outdoor skate parks near your location. Discover street courses, bowls, and ramps with ratings, reviews, and photos. Perfect for sunny day skating."
        }
    )

@router.get("/outdoor-ice-rinks/near-me", response_class=HTMLResponse)
async def outdoor_ice_rinks_near_me(request: Request):
    """SEO-optimized landing page for outdoor ice rinks near me (18,100 monthly searches)"""
    return templates.TemplateResponse(
        "sport_near_me.html",
        {
            "request": request,
            "sport_type": "ice_skating",
            "sport_singular": "Outdoor Ice Rink",
            "sport_plural": "Outdoor Ice Rinks",
            "sport_keyword": "outdoor ice rink",
            "outdoor_only": True,
            "page_title": "Outdoor Ice Rinks Near Me | Find Open-Air Ice Skating | Skaters.com",
            "meta_description": "Find outdoor ice rinks near your location. Discover open-air ice skating rinks with natural ice, seasonal hours, and beautiful outdoor settings. Perfect for winter skating."
        }
    )

@router.get("/indoor-ice-rinks/near-me", response_class=HTMLResponse)
async def indoor_ice_rinks_near_me(request: Request):
    """SEO-optimized landing page for indoor ice rinks near me"""
    return templates.TemplateResponse(
        "sport_near_me.html",
        {
            "request": request,
            "sport_type": "ice_skating",
            "sport_singular": "Indoor Ice Rink",
            "sport_plural": "Indoor Ice Rinks",
            "sport_keyword": "indoor ice rink",
            "indoor_only": True,
            "page_title": "Indoor Ice Rinks Near Me | Find Indoor Ice Skating | Skaters.com",
            "meta_description": "Find indoor ice rinks near your location. Browse climate-controlled ice skating facilities with year-round availability, ratings, reviews, and photos."
        }
    )
