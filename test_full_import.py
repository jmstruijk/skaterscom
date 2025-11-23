"""
End-to-End Test: Scrape one venue, get rich details, and save to DB.
"""

import os
import sys
import json
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from dotenv import load_dotenv
from app.scrapers.google_maps_scraper import GoogleMapsVenueScraper
from app.scrapers.detailed_importer import import_detailed_venue
from app.database import SessionLocal, init_db
from slugify import slugify

def test_single_venue_import():
    load_dotenv()
    api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    if not api_key:
        print("\n❌ ERROR: GOOGLE_MAPS_API_KEY not found in .env file.")
        return

    print(f"\n✅ API Key found. Starting FULL IMPORT test...")

    scraper = GoogleMapsVenueScraper(api_key)
    
    # 1. Find the top skatepark in New York
    print("\n1. Finding top skatepark in New York, NY...")
    initial_results = scraper.search_skateparks('New York', 'NY')
    if not initial_results:
        print("\n❌ Could not find any venues to test.")
        return
    
    top_venue_data = initial_results[0]
    print(f"   Found: {top_venue_data['name']}")

    # 2. Get rich details for that venue
    print("\n2. Fetching rich details...")
    place_id = top_venue_data.get('google_place_id')
    details = scraper.get_place_details(place_id)

    # 3. Merge all data into a single object
    top_venue_data.update({
        'website': details.get('website'),
        'phone': details.get('formatted_phone_number'),
        'opening_hours': details.get('opening_hours', {}).get('weekday_text', []), 
        'photos': [
            f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=1600&photoreference={p.get('photo_reference')}&key={api_key}"
            for p in details.get('photos', [])
        ],
        'slug': slugify(f"{top_venue_data.get('name')} {top_venue_data.get('city')} {top_venue_data.get('state')}")
    })
    print("   Rich details fetched successfully.")

    # 4. Save to database
    print("\n3. Importing to database...")
    init_db()
    db = SessionLocal()
    try:
        imported_venue = import_detailed_venue(top_venue_data, db)
        if imported_venue:
            db.commit()
            print(f"   ✅ Successfully imported '{imported_venue.name}' with ID {imported_venue.id}")
        else:
            print("   ⚠️  Venue was likely a duplicate and was skipped.")
    except Exception as e:
        print(f"   ❌ Database import failed: {e}")
        db.rollback()
    finally:
        db.close()

    # 5. Final verification
    print("\n" + "="*60)
    print("✅ END-TO-END TEST COMPLETE")
    print("="*60)
    print("\nPlease check your application to see the new, detailed venue.")
    print(f"URL: http://localhost:8000/venues/{top_venue_data['slug']}")
    print("\nAll data, including photos and hours, should be visible.")

if __name__ == "__main__":
    test_single_venue_import()
