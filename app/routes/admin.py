"""
Admin panel routes for venue management
"""

from fastapi import APIRouter, Request, Depends, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, desc, or_
from pathlib import Path
from app.database import get_db
from app.models.venue import Venue, VenuePhoto, Review, User, SportType
from app.dependencies import require_admin
from app.csrf import require_csrf
from app.flash import flash

router = APIRouter()
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@router.get("/", response_class=HTMLResponse)
async def admin_dashboard(
    request: Request, 
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Admin dashboard with statistics - requires admin access"""
    
    # Get statistics
    total_venues = db.query(Venue).filter(Venue.status == "ACTIVE").count()
    total_photos = db.query(VenuePhoto).count()
    total_reviews = db.query(Review).count()
    total_users = db.query(User).count()
    
    # Get venues by state
    venues_by_state = db.query(
        Venue.state,
        func.count(Venue.id).label('count')
    ).filter(
        Venue.status == "ACTIVE"
    ).group_by(
        Venue.state
    ).order_by(
        desc('count')
    ).limit(10).all()
    
    # Get recent venues
    recent_venues = db.query(Venue)\
        .filter(Venue.status == "ACTIVE")\
        .order_by(desc(Venue.created_at))\
        .limit(10)\
        .all()
    
    # Get venues needing review (low rating or no photos)
    venues_needing_review = db.query(Venue)\
        .options(joinedload(Venue.photos))\
        .filter(Venue.status == "ACTIVE")\
        .filter(
            (Venue.rating < 3.0) | (Venue.review_count == 0)
        )\
        .limit(10)\
        .all()
    
    return templates.TemplateResponse(
        "admin/dashboard.html",
        {
            "request": request,
            "stats": {
                "total_venues": total_venues,
                "total_photos": total_photos,
                "total_reviews": total_reviews,
                "total_users": total_users
            },
            "venues_by_state": venues_by_state,
            "recent_venues": recent_venues,
            "venues_needing_review": venues_needing_review,
            "page_title": "Admin Dashboard | Skaters.com"
        }
    )


@router.get("/venues", response_class=HTMLResponse)
async def admin_venues_list(
    request: Request,
    page: int = 1,
    search: str = "",
    db: Session = Depends(get_db)
):
    """List all venues with management options"""
    
    per_page = 50
    offset = (page - 1) * per_page
    
    # Build query
    query = db.query(Venue).options(joinedload(Venue.photos))
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Venue.name.ilike(search_term)) |
            (Venue.city.ilike(search_term)) |
            (Venue.state.ilike(search_term))
        )
    
    # Get total count
    total = query.count()
    
    # Get paginated results
    venues = query.order_by(desc(Venue.created_at)).offset(offset).limit(per_page).all()
    
    # Calculate pagination
    total_pages = (total + per_page - 1) // per_page
    
    return templates.TemplateResponse(
        "admin/venues.html",
        {
            "request": request,
            "venues": venues,
            "page": page,
            "total_pages": total_pages,
            "total": total,
            "search": search,
            "page_title": "Manage Venues | Admin"
        }
    )


@router.get("/venues/{venue_id}/edit", response_class=HTMLResponse)
async def admin_edit_venue(
    request: Request,
    venue_id: int,
    db: Session = Depends(get_db)
):
    """Edit venue details"""
    
    venue = db.query(Venue)\
        .options(joinedload(Venue.photos))\
        .options(joinedload(Venue.amenities))\
        .options(joinedload(Venue.hours))\
        .options(joinedload(Venue.pricing))\
        .filter(Venue.id == venue_id)\
        .first()
    
    if not venue:
        raise HTTPException(status_code=404, detail="Venue not found")
    
    return templates.TemplateResponse(
        "admin/edit_venue.html",
        {
            "request": request,
            "venue": venue,
            "page_title": f"Edit {venue.name} | Admin"
        }
    )


@router.post("/venues/{venue_id}/delete")
async def admin_delete_venue(
    venue_id: int,
    db: Session = Depends(get_db)
):
    """Soft delete a venue"""
    
    venue = db.query(Venue).filter(Venue.id == venue_id).first()
    
    if not venue:
        raise HTTPException(status_code=404, detail="Venue not found")
    
    venue.status = "deleted"
    db.commit()
    
    return RedirectResponse(url="/admin/venues", status_code=303)


@router.post("/venues/{venue_id}/verify")
async def admin_verify_venue(
    venue_id: int,
    db: Session = Depends(get_db)
):
    """Mark venue as verified"""
    
    venue = db.query(Venue).filter(Venue.id == venue_id).first()
    
    if not venue:
        raise HTTPException(status_code=404, detail="Venue not found")
    
    venue.verified = True
    db.commit()
    
    return RedirectResponse(url=f"/admin/venues/{venue_id}/edit", status_code=303)


@router.get("/venues", response_class=HTMLResponse)
async def list_venues(
    request: Request,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
    page: int = 1,
    q: str = "",
    status: str = "",
    sport_type: str = ""
):
    """List all venues with filters"""
    
    per_page = 50
    offset = (page - 1) * per_page
    
    # Base query
    query = db.query(Venue)
    
    # Apply filters
    if q:
        search_term = f"%{q}%"
        query = query.filter(
            or_(
                Venue.name.ilike(search_term),
                Venue.city.ilike(search_term),
                Venue.address.ilike(search_term)
            )
        )
    
    if status:
        query = query.filter(Venue.status == status)
    
    if sport_type:
        query = query.filter(Venue.sport_type == sport_type)
    
    # Get total count
    total = query.count()
    total_pages = (total + per_page - 1) // per_page
    
    # Get venues
    venues = query.order_by(desc(Venue.created_at)).offset(offset).limit(per_page).all()
    
    return templates.TemplateResponse(
        "admin/venues_list.html",
        {
            "request": request,
            "user": current_user,
            "venues": venues,
            "total": total,
            "page": page,
            "total_pages": total_pages,
            "query": q,
            "status": status,
            "sport_type": sport_type,
            "page_title": "Manage Venues | Admin | Skaters.com"
        }
    )


@router.get("/venues/{venue_id}/edit", response_class=HTMLResponse)
async def edit_venue_page(
    request: Request,
    venue_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Display venue edit form"""
    
    venue = db.query(Venue).filter(Venue.id == venue_id).first()
    
    if not venue:
        raise HTTPException(status_code=404, detail="Venue not found")
    
    return templates.TemplateResponse(
        "admin/venue_edit.html",
        {
            "request": request,
            "user": current_user,
            "venue": venue,
            "page_title": f"Edit {venue.name} | Admin | Skaters.com"
        }
    )


@router.post("/venues/{venue_id}/update")
async def update_venue(
    request: Request,
    venue_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
    csrf_token: str = Form(...),
    name: str = Form(...),
    sport_type: str = Form(...),
    status: str = Form(...),
    address: str = Form(...),
    city: str = Form(...),
    state: str = Form(...),
    zip_code: str = Form(None),
    phone: str = Form(None),
    latitude: float = Form(None),
    longitude: float = Form(None),
    description: str = Form(None),
    website: str = Form(None)
):
    """Update venue"""
    
    # Validate CSRF
    require_csrf(request, csrf_token)
    
    venue = db.query(Venue).filter(Venue.id == venue_id).first()
    
    if not venue:
        raise HTTPException(status_code=404, detail="Venue not found")
    
    # Update fields
    venue.name = name
    venue.sport_type = SportType(sport_type)
    venue.status = status
    venue.address = address
    venue.city = city
    venue.state = state.upper()
    venue.zip_code = zip_code
    venue.phone = phone
    venue.latitude = latitude
    venue.longitude = longitude
    venue.description = description
    venue.website = website
    
    db.commit()
    
    flash(request, f"Venue '{venue.name}' updated successfully!", "success")
    return RedirectResponse(url=f"/admin/venues/{venue_id}/edit", status_code=303)


@router.post("/venues/{venue_id}/delete")
async def delete_venue(
    request: Request,
    venue_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Delete venue"""
    
    venue = db.query(Venue).filter(Venue.id == venue_id).first()
    
    if not venue:
        return JSONResponse({"error": "Venue not found"}, status_code=404)
    
    # Delete related data
    db.query(VenuePhoto).filter(VenuePhoto.venue_id == venue_id).delete()
    db.query(Review).filter(Review.venue_id == venue_id).delete()
    
    # Delete venue
    db.delete(venue)
    db.commit()
    
    return JSONResponse({"success": True})
