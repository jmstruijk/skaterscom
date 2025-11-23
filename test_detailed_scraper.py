"""
Test Google Maps Scraper with Place Details API to get rich data.
"""

import os
import sys
import json
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from dotenv import load_dotenv
from app.scrapers.google_maps_scraper import GoogleMapsVenueScraper

def test_detailed_scrape():
    load_dotenv()
    api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    if not api_key:
        print("\n❌ ERROR: GOOGLE_MAPS_API_KEY not found in .env file.")
        return

    print(f"\n✅ API Key found. Starting DETAILED scrape for New York, NY...")

    scraper = GoogleMapsVenueScraper(api_key)
    detailed_venues = []

    # Step 1: Find venues (just skateparks for this test)
    print("\n1. Finding skateparks in New York, NY...")
    initial_results = scraper.search_skateparks('New York', 'NY')
    print(f"   Found {len(initial_results)} potential venues.")

    # Step 2: Get rich details for the top 5 results
    print("\n2. Fetching rich details for the top 5 venues...")
    for i, venue in enumerate(initial_results[:5], 1):
        place_id = venue.get('google_place_id')
        if not place_id:
            continue
        
        print(f"   [{i}/5] Getting details for: {venue['name']}...")
        details = scraper.get_place_details(place_id)

        # Merge initial data with rich details
        venue.update({
            'website': details.get('website'),
            'phone': details.get('formatted_phone_number'),
            'opening_hours': details.get('opening_hours', {}).get('weekday_text', []), 
            'photos': [
                f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=1600&photoreference={p.get('photo_reference')}&key={api_key}"
                for p in details.get('photos', [])
            ]
        })
        detailed_venues.append(venue)

    print(f"\n" + "="*80)
    print(f"✅ DETAILED SCRAPE COMPLETE: Processed {len(detailed_venues)} venues.")
    print("="*80)

    # Save results to a new file
    output_file = 'google_maps_DETAILED_results.json'
    with open(output_file, 'w') as f:
        json.dump(detailed_venues, f, indent=2)
    
    print(f"\n💾 All detailed results saved to: {output_file}")
    print("\nPlease review this file to see the high-quality data.")

    # Show a sample of the new rich data
    if detailed_venues:
        print("\n📊 SAMPLE VENUE WITH RICH DETAILS:")
        print(json.dumps(detailed_venues[0], indent=2))

if __name__ == "__main__":
    test_detailed_scrape()
