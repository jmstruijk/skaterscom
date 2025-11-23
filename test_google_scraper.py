"""
Test Google Maps Scraper on a single city to verify data.
"""

import os
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from app.scrapers.google_maps_scraper import GoogleMapsVenueScraper
import json

from dotenv import load_dotenv

def test_single_city():
    load_dotenv()
    api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    if not api_key:
        print("\n❌ ERROR: GOOGLE_MAPS_API_KEY not found in .env file.")
        return

    print(f"\n✅ API Key found. Starting test scrape for New York, NY...")

    scraper = GoogleMapsVenueScraper(api_key)
    venues = []

    # Scrape each venue type for one city
    print("  🛹 Searching for Skateparks...")
    venues.extend(scraper.search_skateparks('New York', 'NY'))
    print("  ⛸️  Searching for Ice Rinks...")
    venues.extend(scraper.search_ice_rinks('New York', 'NY'))
    print("  🛼 Searching for Roller Rinks...")
    venues.extend(scraper.search_roller_rinks('New York', 'NY'))

    print(f"\n" + "="*60)
    print(f"✅ TEST COMPLETE: Found {len(venues)} total venues in New York, NY.")
    print("="*60)

    # Save results to a test file
    output_file = 'google_maps_test_results.json'
    with open(output_file, 'w') as f:
        json.dump(venues, f, indent=2)
    
    print(f"\n💾 All results saved to: {output_file}")
    print("\nPlease review this file to see the high-quality data from Google.")

    # Show a sample
    if venues:
        print("\n📊 SAMPLE VENUE:")
        print(json.dumps(venues[0], indent=2))

if __name__ == "__main__":
    test_single_city()
