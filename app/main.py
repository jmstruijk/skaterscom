"""
Skaters.com - Professional Skating Venue Directory
Built with FastAPI for reliability and SEO optimization
"""

from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct
from pathlib import Path
from typing import List, Dict, Any
from app.database import get_db
from app.models.venue import Venue
from starlette.middleware.sessions import SessionMiddleware
import os
import logging
from app.logging_config import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Skaters.com",
    description="The most comprehensive directory of skating venues in the United States",
    version="1.0.0"
)

# Add session middleware for authentication
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SECRET_KEY", "skaters-secret-key-change-in-production-please"),
    max_age=30 * 24 * 60 * 60,  # 30 days
    same_site="lax",
    https_only=os.getenv("ENVIRONMENT") == "production"
)

# Add flash messages and CSRF to template context
@app.middleware("http")
async def add_template_context(request: Request, call_next):
    """Add flash messages and CSRF token to all template contexts"""
    from app.flash import get_flashed_messages
    from app.csrf import generate_csrf_token
    
    # Get flash messages before processing request
    messages = get_flashed_messages(request)
    
    # Generate CSRF token
    csrf_token = generate_csrf_token(request)
    
    # Store in request state for templates
    request.state.messages = messages
    request.state.csrf_token = csrf_token
    
    response = await call_next(request)
    return response

# Add security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Add security headers to all responses"""
    response = await call_next(request)
    
    # Prevent MIME type sniffing
    response.headers["X-Content-Type-Options"] = "nosniff"
    
    # Prevent clickjacking
    response.headers["X-Frame-Options"] = "DENY"
    
    # Enable XSS protection
    response.headers["X-XSS-Protection"] = "1; mode=block"
    
    # Force HTTPS in production
    if os.getenv("ENVIRONMENT") == "production":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    
    # Content Security Policy (basic)
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com https://maps.googleapis.com; "
        "style-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com; "
        "img-src 'self' data: https: http:; "
        "font-src 'self' data:; "
        "connect-src 'self' https://maps.googleapis.com;"
    )
    
    return response

# Setup static files and templates
BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Import routes
from app.routes import venues, search, auth, reviews, dashboard, locations, seo, admin, near_me, sport_pages

# Include routers (order matters! More specific routes first)
app.include_router(sport_pages.router, tags=["sport-pages"])  # Sport-specific city pages (must be before locations)
app.include_router(near_me.router, tags=["near-me"])  # Geolocation "near me" searches (must be before locations)
app.include_router(venues.router, prefix="/venues", tags=["venues"])
app.include_router(search.router, tags=["search"])  # No prefix, route handles /search
app.include_router(auth.router, prefix="/auth", tags=["authentication"])
app.include_router(reviews.router, prefix="/reviews", tags=["reviews"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
app.include_router(locations.router, prefix="/locations", tags=["locations"])  # Location-based pages (after near_me)
app.include_router(seo.router, tags=["seo"])  # SEO routes (robots.txt, sitemap.xml)
app.include_router(admin.router, prefix="/admin", tags=["admin"])  # Admin panel


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Handle 404 errors"""
    logger.warning(f"404 error: {request.url}")
    return templates.TemplateResponse(
        "errors/404.html",
        {"request": request, "user": None},
        status_code=404
    )


@app.exception_handler(403)
async def forbidden_handler(request: Request, exc):
    """Handle 403 errors"""
    logger.warning(f"403 error: {request.url} - {exc}")
    return templates.TemplateResponse(
        "errors/403.html",
        {"request": request, "user": None},
        status_code=403
    )


@app.exception_handler(500)
async def server_error_handler(request: Request, exc):
    """Handle 500 errors"""
    logger.error(f"500 error: {request.url} - {exc}", exc_info=True)
    return templates.TemplateResponse(
        "errors/500.html",
        {"request": request, "user": None},
        status_code=500
    )


def get_popular_states(db: Session, limit: int = 12) -> List[Dict[str, Any]]:
    """Get list of states with the most venues"""
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
        func.count(Venue.id).desc()
    ).limit(limit).all()
    
    return [{"code": state, "venue_count": count} for state, count in states]

def get_popular_cities(db: Session, limit: int = 6) -> List[Dict[str, Any]]:
    """Get list of cities with the most venues, including a representative image"""
    from sqlalchemy.orm import joinedload
    
    cities = db.query(
        Venue.city,
        Venue.state,
        func.count(Venue.id).label('venue_count')
    ).filter(
        Venue.status == "ACTIVE"
    ).group_by(
        Venue.city,
        Venue.state
    ).order_by(
        func.count(Venue.id).desc()
    ).limit(limit).all()
    
    result = []
    for city, state, count in cities:
        # Get a top-rated venue from this city that has photos
        # First try to find a venue with photos
        venue_with_photo = db.query(Venue)\
            .options(joinedload(Venue.photos))\
            .join(Venue.photos)\
            .filter(
                Venue.city == city,
                Venue.state == state,
                Venue.status == "ACTIVE"
            ).order_by(
                Venue.rating.desc()
            ).first()
        
        # If no venue with photos found, try without the join (fallback)
        if not venue_with_photo:
            venue_with_photo = db.query(Venue)\
                .options(joinedload(Venue.photos))\
                .filter(
                    Venue.city == city,
                    Venue.state == state,
                    Venue.status == "ACTIVE"
                ).order_by(
                    Venue.rating.desc()
                ).first()
        
        # Get image URL from the venue
        image_url = None
        if venue_with_photo and venue_with_photo.photos:
            photo = next((p for p in venue_with_photo.photos if p.is_primary), 
                        venue_with_photo.photos[0] if venue_with_photo.photos else None)
            if photo:
                if 'maxwidth=' in photo.url:
                    image_url = photo.url.replace('maxwidth=1600', 'maxwidth=600').replace('maxwidth=800', 'maxwidth=600')
                elif '?' in photo.url:
                    image_url = f"{photo.url}&maxwidth=600"
                else:
                    image_url = f"{photo.url}?maxwidth=600"
        
        result.append({
            "name": city, 
            "state": state, 
            "venue_count": count,
            "image_url": image_url,
            "slug": f"/locations/{state.lower()}/{city.lower().replace(' ', '-')}"
        })
    
    return result

@app.get("/", response_class=HTMLResponse)
async def homepage(request: Request, db: Session = Depends(get_db)):
    """Homepage with featured venues and location-based navigation"""
    from app.dependencies import get_current_user_optional
    
    # Get current user for navigation
    current_user = get_current_user_optional(request, db)
    
    # Query top-rated venues from database with their photos
    from sqlalchemy.orm import joinedload
    from app.models.venue import VenuePhoto
    
    venues = db.query(Venue)\
        .options(joinedload(Venue.photos))\
        .filter(Venue.status == "ACTIVE")\
        .order_by(Venue.rating.desc())\
        .limit(6)\
        .all()
    
    featured_venues = []
    for venue in venues:
        # Get the primary photo if available, otherwise the first photo, or use a placeholder
        primary_photo = next((p for p in venue.photos if p.is_primary), None) if venue.photos else None
        first_photo = venue.photos[0] if venue.photos else None
        photo = primary_photo or first_photo
        
        # Construct the image URL
        image_url = None
        if photo:
            # Ensure maxwidth parameter is included for Google Photos (use 400px for thumbnails)
            if 'maxwidth=' in photo.url:
                # Replace existing maxwidth with 400 for faster loading
                image_url = photo.url.replace('maxwidth=1600', 'maxwidth=400').replace('maxwidth=800', 'maxwidth=400')
            elif '?' in photo.url:
                image_url = f"{photo.url}&maxwidth=400"
            else:
                image_url = f"{photo.url}?maxwidth=400"
        
        featured_venues.append({
            "id": venue.id,
            "name": venue.name,
            "slug": venue.slug,
            "city": venue.city,
            "state": venue.state,
            "sport_type": venue.sport_type.value,
            "rating": venue.rating,
            "review_count": venue.review_count,
            "description": venue.description or f"{venue.name} in {venue.city}, {venue.state}",
            "image_url": image_url or f"https://picsum.photos/seed/{venue.slug}/800/600?grayscale"
        })
    
    # Get location-based data
    popular_states = get_popular_states(db)
    popular_cities = get_popular_cities(db)
    
    # Valid US state codes
    us_states = ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 
                 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 
                 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 
                 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 
                 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY', 'DC']
    
    # Get real stats from database (US venues only)
    total_venues = db.query(Venue).filter(Venue.status == "ACTIVE", Venue.state.in_(us_states)).count()
    total_cities = db.query(func.count(func.distinct(Venue.city + Venue.state))).filter(Venue.status == "ACTIVE", Venue.state.in_(us_states)).scalar()
    total_states = db.query(func.count(func.distinct(Venue.state))).filter(Venue.status == "ACTIVE", Venue.state.in_(us_states)).scalar()
    total_reviews = db.query(func.sum(Venue.review_count)).filter(Venue.status == "ACTIVE", Venue.state.in_(us_states)).scalar() or 0
    
    stats = {
        "total_venues": total_venues,
        "cities": total_cities,
        "states": total_states,
        "reviews": int(total_reviews)
    }
    
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "user": current_user,
            "venues": featured_venues,
            "popular_states": popular_states,
            "popular_cities": popular_cities,
            "stats": stats,
            "page_title": "Skate Parks & Ice Rinks Near You | Skaters.com",
            "meta_description": "Find the best skate parks, ice skating rinks, and roller rinks in the United States. Search by location, read reviews, see photos, and get directions to skating facilities near you."
        }
    )


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "skaters.com"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
