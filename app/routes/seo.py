"""
SEO routes - sitemap, robots.txt, etc.
"""

from fastapi import APIRouter, Request, Depends, Response
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from app.database import get_db
from app.models.venue import Venue, SportType

router = APIRouter()


@router.get("/robots.txt", response_class=Response)
async def robots_txt():
    """Generate robots.txt file"""
    content = """User-agent: *
Allow: /
Disallow: /dashboard
Disallow: /admin
Disallow: /api

Sitemap: https://skaters.com/sitemap.xml
"""
    return Response(content=content, media_type="text/plain")


@router.get("/sitemap.xml", response_class=Response)
async def sitemap_xml(db: Session = Depends(get_db)):
    """Generate XML sitemap for SEO"""
    
    # Get all active venues
    venues = db.query(Venue).filter(Venue.status == "ACTIVE").all()
    
    # Get all states
    states = db.query(Venue.state).filter(Venue.status == "ACTIVE").distinct().all()
    
    # Get all cities
    cities = db.query(Venue.city, Venue.state).filter(Venue.status == "ACTIVE").distinct().all()
    
    # Build sitemap XML
    xml = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    
    # Homepage
    xml.append('  <url>')
    xml.append('    <loc>https://skaters.com/</loc>')
    xml.append('    <changefreq>daily</changefreq>')
    xml.append('    <priority>1.0</priority>')
    xml.append('  </url>')
    
    # States page
    xml.append('  <url>')
    xml.append('    <loc>https://skaters.com/locations/states</loc>')
    xml.append('    <changefreq>weekly</changefreq>')
    xml.append('    <priority>0.9</priority>')
    xml.append('  </url>')
    
    # Individual state pages
    for (state,) in states:
        xml.append('  <url>')
        xml.append(f'    <loc>https://skaters.com/locations/{state.lower()}</loc>')
        xml.append('    <changefreq>weekly</changefreq>')
        xml.append('    <priority>0.8</priority>')
        xml.append('  </url>')
    
    # City pages
    for city, state in cities:
        city_slug = city.lower().replace(' ', '-')
        xml.append('  <url>')
        xml.append(f'    <loc>https://skaters.com/locations/{state.lower()}/{city_slug}</loc>')
        xml.append('    <changefreq>weekly</changefreq>')
        xml.append('    <priority>0.7</priority>')
        xml.append('  </url>')
    
    # SEO-optimized "Near Me" pages
    near_me_pages = [
        ('ice-rinks', 0.95),  # Hub page - 110K searches
        ('near-me', 0.9),  # Main near me landing page
        ('skate-parks/near-me', 0.9),
        ('ice-rinks/near-me', 0.9),
        ('roller-rinks/near-me', 0.9),
        ('indoor-skate-parks/near-me', 0.85),
        ('outdoor-skate-parks/near-me', 0.85),
        ('outdoor-ice-rinks/near-me', 0.85),  # 18K searches
        ('indoor-ice-rinks/near-me', 0.85),
    ]
    for path, priority in near_me_pages:
        xml.append('  <url>')
        xml.append(f'    <loc>https://skaters.com/{path}</loc>')
        xml.append('    <changefreq>weekly</changefreq>')
        xml.append(f'    <priority>{priority}</priority>')
        xml.append('  </url>')
    
    # Sport-specific city pages (top 20 cities for each sport type)
    top_cities = db.query(
        Venue.city,
        Venue.state,
        Venue.sport_type,
        func.count(Venue.id).label('count')
    ).filter(
        Venue.status == "ACTIVE"
    ).group_by(
        Venue.city,
        Venue.state,
        Venue.sport_type
    ).order_by(
        func.count(Venue.id).desc()
    ).limit(100).all()
    
    sport_url_map = {
        SportType.SKATEBOARDING: 'skate-parks',
        SportType.ICE_SKATING: 'ice-rinks',
        SportType.ROLLER_SKATING: 'roller-rinks',
        SportType.INLINE_SKATING: 'inline-skating'
    }
    
    for city, state, sport_type, count in top_cities:
        city_slug = city.lower().replace(' ', '-')
        sport_slug = sport_url_map.get(sport_type, 'venues')
        xml.append('  <url>')
        xml.append(f'    <loc>https://skaters.com/{sport_slug}/{state.lower()}/{city_slug}</loc>')
        xml.append('    <changefreq>weekly</changefreq>')
        xml.append('    <priority>0.85</priority>')
        xml.append('  </url>')
    
    # Venue detail pages
    for venue in venues:
        xml.append('  <url>')
        xml.append(f'    <loc>https://skaters.com/venues/{venue.slug}</loc>')
        xml.append('    <changefreq>monthly</changefreq>')
        xml.append('    <priority>0.6</priority>')
        xml.append('  </url>')
    
    xml.append('</urlset>')
    
    return Response(content='\n'.join(xml), media_type="application/xml")
