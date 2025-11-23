"""
Enhanced importer to save RICH venue data to the database.
"""

import sys
import logging
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from app.database import SessionLocal
from app.models.venue import Venue, VenuePhoto, VenueAmenity, VenueHours, VenuePricing, SportType, VenueStatus
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def import_detailed_venue(venue_data: dict, db: SessionLocal):
    """Import a single venue with rich details into the database."""

    # Check if venue already exists by Google Place ID
    if 'google_place_id' in venue_data and venue_data['google_place_id']:
        existing = db.query(Venue).filter(Venue.google_place_id == venue_data['google_place_id']).first()
        if existing:
            logger.info(f"Skipping duplicate venue (Google Place ID): {venue_data['name']}")
            return None

    # Convert sport_type string to enum
    try:
        sport_type_enum = SportType(venue_data['sport_type'])
    except ValueError:
        logger.error(f"Invalid sport type: {venue_data['sport_type']}")
        return None

    # Create the main Venue object
    venue = Venue(
        name=venue_data.get('name', 'Unknown Venue'),
        slug=venue_data.get('slug'), # Assuming slug is pre-generated
        sport_type=sport_type_enum,
        address=venue_data.get('address'),
        city=venue_data.get('city'),
        state=venue_data.get('state'),
        zip_code=venue_data.get('zip_code'),
        country='US',
        latitude=venue_data.get('latitude'),
        longitude=venue_data.get('longitude'),
        phone=venue_data.get('phone'),
        website=venue_data.get('website'),
        description=venue_data.get('description'),
        rating=venue_data.get('rating', 0.0),
        review_count=venue_data.get('review_count', 0),
        google_place_id=venue_data.get('google_place_id'),
        verified=True, # Data from Google is considered verified
        status=VenueStatus.ACTIVE,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(venue)
    db.flush() # This is crucial to get the new venue.id

    # --- Save the RICH DATA --- #

    # 1. Save all Photos
    if 'photos' in venue_data and venue_data['photos']:
        for i, photo_url in enumerate(venue_data['photos']):
            photo = VenuePhoto(
                venue_id=venue.id,
                url=photo_url,
                caption=f"{venue.name} photo {i+1}",
                is_primary=(i == 0), # First photo is primary
                approved=True
            )
            db.add(photo)

    # 2. Save all Opening Hours
    if 'opening_hours' in venue_data and venue_data['opening_hours']:
        hours_data = {day.split(': ')[0].lower(): day.split(': ')[1] for day in venue_data['opening_hours']}
        hours = VenueHours(
            venue_id=venue.id,
            monday=hours_data.get('monday'),
            tuesday=hours_data.get('tuesday'),
            wednesday=hours_data.get('wednesday'),
            thursday=hours_data.get('thursday'),
            friday=hours_data.get('friday'),
            saturday=hours_data.get('saturday'),
            sunday=hours_data.get('sunday')
        )
        db.add(hours)

    # 3. Save default amenities and pricing (can be enhanced later)
    pricing = VenuePricing(venue_id=venue.id, admission="Varies", rental="Varies")
    db.add(pricing)

    logger.info(f"✅ Imported: {venue.name} ({venue.city}, {venue.state}) with full details.")
    return venue
