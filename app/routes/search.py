"""
Search routes with advanced filtering
"""

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, func
from pathlib import Path
from app.database import get_db
from app.models.venue import Venue, SportType, VenuePhoto
from app.dependencies import get_current_user_optional

router = APIRouter()
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@router.get("/search", response_class=HTMLResponse)
async def search_venues(
    request: Request,
    q: str = "",
    sport_type: str = "",
    state: str = "",
    city: str = "",
    sort: str = "rating",
    page: int = 1,
    db: Session = Depends(get_db)
):
    """Advanced venue search with filters and pagination"""
    
    per_page = 24
    offset = (page - 1) * per_page
    
    # Start with base query - load photos eagerly
    query = db.query(Venue).options(joinedload(Venue.photos)).filter(Venue.status == "ACTIVE")
    
    # Apply keyword search
    if q:
        search_term = f"%{q}%"
        query = query.filter(
            or_(
                Venue.name.ilike(search_term),
                Venue.city.ilike(search_term),
                Venue.description.ilike(search_term),
                Venue.address.ilike(search_term)
            )
        )
    
    # Apply sport type filter
    if sport_type:
        try:
            sport_enum = SportType(sport_type)
            query = query.filter(Venue.sport_type == sport_enum)
        except ValueError:
            pass  # Invalid sport type, ignore
    
    # Apply state filter
    if state:
        query = query.filter(Venue.state == state.upper())
    
    # Apply city filter
    if city:
        query = query.filter(Venue.city.ilike(f"%{city}%"))
    
    # Apply sorting
    if sort == "reviews":
        query = query.order_by(Venue.review_count.desc())
    elif sort == "name":
        query = query.order_by(Venue.name)
    else:  # Default to rating
        query = query.order_by(Venue.rating.desc())
    
    # Get total count for pagination
    total = query.count()
    
    # Execute query with pagination
    venues = query.offset(offset).limit(per_page).all()
    
    # Calculate pagination info
    total_pages = (total + per_page - 1) // per_page
    has_prev = page > 1
    has_next = page < total_pages
    
    # Convert to dict for template with real images
    results = []
    for v in venues:
        # Get primary photo or first available
        photo = next((p for p in v.photos if p.is_primary), 
                    v.photos[0] if v.photos else None)
        
        # Build image URL
        image_url = None
        if photo:
            if 'maxwidth=' not in photo.url:
                image_url = f"{photo.url}?maxwidth=400" if '?' not in photo.url else f"{photo.url}&maxwidth=400"
            else:
                image_url = photo.url
        
        results.append({
            "id": v.id,
            "name": v.name,
            "slug": v.slug,
            "city": v.city,
            "state": v.state,
            "sport_type": v.sport_type.value,
            "rating": v.rating,
            "review_count": v.review_count,
            "description": v.description[:200] + '...' if v.description and len(v.description) > 200 else v.description,
            "image_url": image_url or f"https://picsum.photos/seed/{v.slug}/400/300?grayscale"
        })
    
    # Build query params for sort links
    query_params = []
    if q:
        query_params.append(f"q={q}")
    if sport_type:
        query_params.append(f"sport_type={sport_type}")
    if state:
        query_params.append(f"state={state}")
    if city:
        query_params.append(f"city={city}")
    
    # Get current user for navigation
    current_user = get_current_user_optional(request, db)
    
    # Get all states for dropdown
    all_states = db.query(Venue.state).filter(Venue.status == "ACTIVE").distinct().order_by(Venue.state).all()
    states_list = [{"code": s[0], "name": get_state_name(s[0])} for s in all_states]
    
    # Dynamic titles based on sport type
    sport_titles = {
        "skateboarding": {
            "title": "Skate Parks",
            "singular": "Skate Park",
            "page_title": "Find Skate Parks Near You | Skaters.com",
            "meta_description": "Discover the best skate parks in the United States. Find skateboarding venues near you with ratings, reviews, and photos."
        },
        "ice_skating": {
            "title": "Ice Rinks",
            "singular": "Ice Rink",
            "page_title": "Find Ice Skating Rinks Near You | Skaters.com",
            "meta_description": "Discover the best ice skating rinks in the United States. Find ice rinks near you with ratings, reviews, and photos."
        },
        "roller_skating": {
            "title": "Roller Rinks",
            "singular": "Roller Rink",
            "page_title": "Find Roller Skating Rinks Near You | Skaters.com",
            "meta_description": "Discover the best roller skating rinks in the United States. Find roller rinks near you with ratings, reviews, and photos."
        },
        "inline_skating": {
            "title": "Inline Skating Venues",
            "singular": "Inline Skating Venue",
            "page_title": "Find Inline Skating Venues Near You | Skaters.com",
            "meta_description": "Discover the best inline skating venues in the United States. Find inline skating spots near you with ratings, reviews, and photos."
        }
    }
    
    # Get sport-specific info
    sport_info = sport_titles.get(sport_type, {
        "title": "Skating Venues",
        "singular": "Skating Venue",
        "page_title": "Search Skating Venues | Skaters.com",
        "meta_description": "Search for skating venues across the United States"
    })
    
    return templates.TemplateResponse(
        "search.html",
        {
            "request": request,
            "user": current_user,
            "results": results,
            "query": q,
            "sport_type": sport_type,
            "state": state,
            "city": city,
            "sort": sort,
            "query_params": "&".join(query_params),
            "page": page,
            "total_pages": total_pages,
            "total": total,
            "has_prev": has_prev,
            "has_next": has_next,
            "states": states_list,
            "sport_title": sport_info["title"],
            "sport_singular": sport_info["singular"],
            "page_title": sport_info["page_title"],
            "meta_description": sport_info["meta_description"]
        }
    )

def get_state_name(code: str) -> str:
    """Convert state code to full name"""
    state_names = {
        "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas", "CA": "California",
        "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware", "FL": "Florida", "GA": "Georgia",
        "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois", "IN": "Indiana", "IA": "Iowa",
        "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
        "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi", "MO": "Missouri",
        "MT": "Montana", "NE": "Nebraska", "NV": "Nevada", "NH": "New Hampshire", "NJ": "New Jersey",
        "NM": "New Mexico", "NY": "New York", "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio",
        "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina",
        "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah", "VT": "Vermont",
        "VA": "Virginia", "WA": "Washington", "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming"
    }
    return state_names.get(code, code)
