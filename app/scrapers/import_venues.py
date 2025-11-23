"""
Import scraped venues into database
"""

import sys
import logging
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.database import SessionLocal, init_db
from app.models.venue import Venue, VenuePhoto, VenueAmenity, VenueHours, VenuePricing, SportType, VenueStatus
from app.scrapers.concrete_disciples import ConcreteDisciplesMockScraper
from app.scrapers.rinkatlas import RinkAtlasMockScraper
from app.scrapers.rinktime import RinkTimeMockScraper
from app.scrapers.traillink import TrailLinkMockScraper
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def import_venue_to_db(venue_data: dict, db):
    """Import a single venue into the database"""
    
    # Check if venue already exists (by slug)
    existing = db.query(Venue).filter(Venue.slug == venue_data['slug']).first()
    if existing:
        logger.info(f"Venue already exists: {venue_data['name']} - skipping")
        return None
    
    # Convert sport_type string to enum
    try:
        sport_type_enum = SportType(venue_data['sport_type'])
    except ValueError:
        logger.error(f"Invalid sport type: {venue_data['sport_type']}")
        return None
    
    # Create venue
    venue = Venue(
        name=venue_data['name'],
        slug=venue_data['slug'],
        sport_type=sport_type_enum,
        discipline=venue_data.get('discipline'),
        venue_type=venue_data.get('venue_type'),
        address=venue_data.get('address'),
        city=venue_data.get('city'),
        state=venue_data.get('state'),
        zip_code=venue_data.get('zip_code'),
        country=venue_data.get('country', 'US'),
        latitude=venue_data.get('latitude'),
        longitude=venue_data.get('longitude'),
        phone=venue_data.get('phone'),
        email=venue_data.get('email'),
        website=venue_data.get('website'),
        description=venue_data.get('description'),
        year_opened=venue_data.get('year_opened'),
        verified=venue_data.get('verified', False),
        status=VenueStatus.ACTIVE,
        rating=venue_data.get('rating', 0.0),
        review_count=venue_data.get('review_count', 0),
        meta_title=venue_data.get('meta_title'),
        meta_description=venue_data.get('meta_description'),
        seo_keywords=venue_data.get('seo_keywords'),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(venue)
    db.flush()  # Get the venue ID
    
    # Add default photo
    photo = VenuePhoto(
        venue_id=venue.id,
        url=f"https://picsum.photos/seed/{venue.slug}/800/600",
        caption=f"{venue.name} - Main view",
        is_primary=True,
        approved=True
    )
    db.add(photo)
    
    # Add default amenities based on venue type
    amenities = []
    if venue.venue_type == 'skatepark':
        amenities = [
            VenueAmenity(venue_id=venue.id, amenity_type='facilities', amenity_name='Restrooms', available=True),
            VenueAmenity(venue_id=venue.id, amenity_type='facilities', amenity_name='Parking', available=True),
            VenueAmenity(venue_id=venue.id, amenity_type='features', amenity_name='Lighting', available=True),
        ]
    elif venue.venue_type in ['ice_rink', 'roller_rink']:
        amenities = [
            VenueAmenity(venue_id=venue.id, amenity_type='services', amenity_name='Skate Rentals', available=True),
            VenueAmenity(venue_id=venue.id, amenity_type='services', amenity_name='Lessons', available=True),
            VenueAmenity(venue_id=venue.id, amenity_type='facilities', amenity_name='Snack Bar', available=True),
        ]
    elif venue.venue_type == 'trail':
        amenities = [
            VenueAmenity(venue_id=venue.id, amenity_type='features', amenity_name='Paved Surface', available=True),
            VenueAmenity(venue_id=venue.id, amenity_type='features', amenity_name='Scenic Views', available=True),
        ]
    
    for amenity in amenities:
        db.add(amenity)
    
    # Add default hours (if not trail)
    if venue.venue_type != 'trail':
        hours = VenueHours(
            venue_id=venue.id,
            monday="9:00 AM - 9:00 PM",
            tuesday="9:00 AM - 9:00 PM",
            wednesday="9:00 AM - 9:00 PM",
            thursday="9:00 AM - 9:00 PM",
            friday="9:00 AM - 10:00 PM",
            saturday="10:00 AM - 10:00 PM",
            sunday="10:00 AM - 9:00 PM"
        )
        db.add(hours)
    
    # Add default pricing
    if venue.venue_type == 'skatepark':
        pricing = VenuePricing(
            venue_id=venue.id,
            admission="Free",
            notes="Free admission, bring your own equipment"
        )
    elif venue.venue_type in ['ice_rink', 'roller_rink']:
        pricing = VenuePricing(
            venue_id=venue.id,
            admission="$10-$15",
            rental="$5",
            notes="Prices vary by session"
        )
    else:
        pricing = VenuePricing(
            venue_id=venue.id,
            admission="Free",
            notes="Public trail, free access"
        )
    
    db.add(pricing)
    
    logger.info(f"✅ Imported: {venue.name} ({venue.city}, {venue.state})")
    return venue


def run_scrapers():
    """Run all scrapers and import data"""
    
    # Initialize database
    init_db()
    db = SessionLocal()
    
    try:
        logger.info("=" * 60)
        logger.info("STARTING VENUE SCRAPING AND IMPORT")
        logger.info("=" * 60)
        
        total_imported = 0
        
        # 1. Scrape skateparks
        logger.info("\n📍 Scraping Skateparks from Concrete Disciples...")
        skatepark_scraper = ConcreteDisciplesMockScraper()
        skateparks = skatepark_scraper.scrape()
        for venue_data in skateparks:
            if import_venue_to_db(venue_data, db):
                total_imported += 1
        db.commit()
        
        # 2. Scrape ice rinks
        logger.info("\n⛸️  Scraping Ice Rinks from RinkAtlas...")
        ice_scraper = RinkAtlasMockScraper()
        ice_rinks = ice_scraper.scrape()
        for venue_data in ice_rinks:
            if import_venue_to_db(venue_data, db):
                total_imported += 1
        db.commit()
        
        # 3. Scrape roller rinks
        logger.info("\n🛼 Scraping Roller Rinks from RinkTime...")
        roller_scraper = RinkTimeMockScraper()
        roller_rinks = roller_scraper.scrape()
        for venue_data in roller_rinks:
            if import_venue_to_db(venue_data, db):
                total_imported += 1
        db.commit()
        
        # 4. Scrape inline skating trails
        logger.info("\n🛹 Scraping Inline Skating Trails from TrailLink...")
        trail_scraper = TrailLinkMockScraper()
        trails = trail_scraper.scrape()
        for venue_data in trails:
            if import_venue_to_db(venue_data, db):
                total_imported += 1
        db.commit()
        
        logger.info("\n" + "=" * 60)
        logger.info(f"✅ IMPORT COMPLETE!")
        logger.info(f"Total venues imported: {total_imported}")
        logger.info("=" * 60)
        
        # Show stats
        logger.info("\n📊 Database Statistics:")
        skatepark_count = db.query(Venue).filter(Venue.sport_type == SportType.SKATEBOARDING).count()
        ice_count = db.query(Venue).filter(Venue.sport_type == SportType.ICE_SKATING).count()
        roller_count = db.query(Venue).filter(Venue.sport_type == SportType.ROLLER_SKATING).count()
        inline_count = db.query(Venue).filter(Venue.sport_type == SportType.INLINE_SKATING).count()
        
        logger.info(f"  Skateparks: {skatepark_count}")
        logger.info(f"  Ice Rinks: {ice_count}")
        logger.info(f"  Roller Rinks: {roller_count}")
        logger.info(f"  Inline Trails: {inline_count}")
        logger.info(f"  TOTAL: {skatepark_count + ice_count + roller_count + inline_count}")
        
    except Exception as e:
        logger.error(f"❌ Error during import: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run_scrapers()
