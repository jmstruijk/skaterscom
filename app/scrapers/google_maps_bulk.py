"""
Google Maps Bulk Scraper - Get thousands of real venues

This script will scrape the top 100 US cities for all venue types.
Estimated: 5,000+ venues for ~$50-100

SETUP:
1. Get API key: https://console.cloud.google.com/
2. Enable "Places API"
3. Add to .env: GOOGLE_MAPS_API_KEY=your_key_here
4. Run: python app/scrapers/google_maps_bulk.py
"""

import os
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.scrapers.google_maps_scraper import GoogleMapsVenueScraper
from app.database import SessionLocal, init_db
from app.scrapers.detailed_importer import import_detailed_venue
from slugify import slugify
import json
import time

# Top 100 US cities for comprehensive coverage
TOP_CITIES = [
    # Major metros
    ('New York', 'NY'), ('Los Angeles', 'CA'), ('Chicago', 'IL'), ('Houston', 'TX'),
    ('Phoenix', 'AZ'), ('Philadelphia', 'PA'), ('San Antonio', 'TX'), ('San Diego', 'CA'),
    ('Dallas', 'TX'), ('San Jose', 'CA'), ('Austin', 'TX'), ('Jacksonville', 'FL'),
    
    # Large cities
    ('Fort Worth', 'TX'), ('Columbus', 'OH'), ('Charlotte', 'NC'), ('San Francisco', 'CA'),
    ('Indianapolis', 'IN'), ('Seattle', 'WA'), ('Denver', 'CO'), ('Washington', 'DC'),
    ('Boston', 'MA'), ('El Paso', 'TX'), ('Nashville', 'TN'), ('Detroit', 'MI'),
    ('Oklahoma City', 'OK'), ('Portland', 'OR'), ('Las Vegas', 'NV'), ('Memphis', 'TN'),
    
    # Medium cities
    ('Louisville', 'KY'), ('Baltimore', 'MD'), ('Milwaukee', 'WI'), ('Albuquerque', 'NM'),
    ('Tucson', 'AZ'), ('Fresno', 'CA'), ('Mesa', 'AZ'), ('Sacramento', 'CA'),
    ('Atlanta', 'GA'), ('Kansas City', 'MO'), ('Colorado Springs', 'CO'), ('Raleigh', 'NC'),
    ('Miami', 'FL'), ('Long Beach', 'CA'), ('Virginia Beach', 'VA'), ('Omaha', 'NE'),
    ('Oakland', 'CA'), ('Minneapolis', 'MN'), ('Tulsa', 'OK'), ('Tampa', 'FL'),
    
    # Additional coverage
    ('Arlington', 'TX'), ('New Orleans', 'LA'), ('Wichita', 'KS'), ('Cleveland', 'OH'),
    ('Bakersfield', 'CA'), ('Aurora', 'CO'), ('Anaheim', 'CA'), ('Honolulu', 'HI'),
    ('Santa Ana', 'CA'), ('Riverside', 'CA'), ('Corpus Christi', 'TX'), ('Lexington', 'KY'),
    ('Henderson', 'NV'), ('Stockton', 'CA'), ('Saint Paul', 'MN'), ('Cincinnati', 'OH'),
    ('St. Louis', 'MO'), ('Pittsburgh', 'PA'), ('Greensboro', 'NC'), ('Anchorage', 'AK'),
    ('Plano', 'TX'), ('Lincoln', 'NE'), ('Orlando', 'FL'), ('Irvine', 'CA'),
    ('Newark', 'NJ'), ('Durham', 'NC'), ('Chula Vista', 'CA'), ('Toledo', 'OH'),
    ('Fort Wayne', 'IN'), ('St. Petersburg', 'FL'), ('Laredo', 'TX'), ('Jersey City', 'NJ'),
    ('Chandler', 'AZ'), ('Madison', 'WI'), ('Lubbock', 'TX'), ('Scottsdale', 'AZ'),
    ('Reno', 'NV'), ('Buffalo', 'NY'), ('Gilbert', 'AZ'), ('Glendale', 'AZ'),
    ('North Las Vegas', 'NV'), ('Winston-Salem', 'NC'), ('Chesapeake', 'VA'), ('Norfolk', 'VA'),
    ('Fremont', 'CA'), ('Garland', 'TX'), ('Irving', 'TX'), ('Hialeah', 'FL'),
    ('Richmond', 'VA'), ('Boise', 'ID'), ('Spokane', 'WA'), ('Baton Rouge', 'LA'),
]


def scrape_all_venues(api_key: str, max_cities: int = 100):
    """
    Scrape all venue types from top US cities
    
    Args:
        api_key: Google Maps API key
        max_cities: Number of cities to scrape (default: 100)
    """
    
    print("=" * 80)
    print("GOOGLE MAPS BULK VENUE SCRAPER")
    print("=" * 80)
    print(f"\nScraping {max_cities} cities for all venue types...")
    print(f"Estimated venues: {max_cities * 50}+")
    print(f"Estimated cost: ${max_cities * 0.50:.2f} - ${max_cities * 1.00:.2f}")
    print("\nThis will take approximately 30-60 minutes.")
    print("=" * 80)
    
    scraper = GoogleMapsVenueScraper(api_key)
    all_venues = []
    completed_cities = set()

    # --- Make the scraper resumable ---
    progress_file = 'google_maps_venues.json'
    if os.path.exists(progress_file):
        print(f"\nFound existing progress file: {progress_file}")
        with open(progress_file, 'r') as f:
            all_venues = json.load(f)
        for venue in all_venues:
            completed_cities.add((venue.get('city'), venue.get('state')))
        print(f"Identified {len(completed_cities)} previously scraped cities. They will be skipped.")
    # ---------------------------------
    
    cities_to_scrape = TOP_CITIES[:max_cities]
    
    for i, (city, state) in enumerate(cities_to_scrape, 1):
        if (city, state) in completed_cities:
            print(f"\n[{i}/{len(cities_to_scrape)}] Skipping {city}, {state} (already scraped)..." )
            continue

        print(f"\n[{i}/{len(cities_to_scrape)}] Scraping {city}, {state}...")

        city_venues = []
        try:
            # Skateparks
            print(f"  🛹 Skateparks...", end=" ")
            skateparks = scraper.search_skateparks(city, state)
            print(f"{len(skateparks)} found")
            for venue in skateparks:
                details = scraper.get_place_details(venue.get('google_place_id'))
                venue.update({
                    'website': details.get('website'),
                    'phone': details.get('formatted_phone_number'),
                    'opening_hours': details.get('opening_hours', {}).get('weekday_text', []),
                    'photos': [
                        f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=1600&photoreference={p.get('photo_reference')}&key={api_key}"
                        for p in details.get('photos', [])
                    ],
                    'slug': slugify(f"{venue.get('name')} {venue.get('city')} {venue.get('state')}")
                })
                city_venues.append(venue)
                time.sleep(0.05)
            time.sleep(1)

            # Ice rinks
            print(f"  ⛸️  Ice rinks...", end=" ")
            ice_rinks = scraper.search_ice_rinks(city, state)
            print(f"{len(ice_rinks)} found")
            for venue in ice_rinks:
                details = scraper.get_place_details(venue.get('google_place_id'))
                venue.update({
                    'website': details.get('website'),
                    'phone': details.get('formatted_phone_number'),
                    'opening_hours': details.get('opening_hours', {}).get('weekday_text', []),
                    'photos': [
                        f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=1600&photoreference={p.get('photo_reference')}&key={api_key}"
                        for p in details.get('photos', [])
                    ],
                    'slug': slugify(f"{venue.get('name')} {venue.get('city')} {venue.get('state')}")
                })
                city_venues.append(venue)
                time.sleep(0.05)
            time.sleep(1)

            # Roller rinks
            print(f"  🛼 Roller rinks...", end=" ")
            roller_rinks = scraper.search_roller_rinks(city, state)
            print(f"{len(roller_rinks)} found")
            for venue in roller_rinks:
                details = scraper.get_place_details(venue.get('google_place_id'))
                venue.update({
                    'website': details.get('website'),
                    'phone': details.get('formatted_phone_number'),
                    'opening_hours': details.get('opening_hours', {}).get('weekday_text', []),
                    'photos': [
                        f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=1600&photoreference={p.get('photo_reference')}&key={api_key}"
                        for p in details.get('photos', [])
                    ],
                    'slug': slugify(f"{venue.get('name')} {venue.get('city')} {venue.get('state')}")
                })
                city_venues.append(venue)
                time.sleep(0.05)
            time.sleep(1)

            print(f"  ✅ Found {len(city_venues)} total new venues for {city}.")

            # --- Save data for the current city ---
            if city_venues:
                print(f"  💾 Importing {len(city_venues)} new venues to database...")
                import_to_database(city_venues)
                all_venues.extend(city_venues)
                save_progress(all_venues, progress_file) # Overwrite with the full list each time
            # -------------------------------------

        except Exception as e:
            print(f"  ❌ Error scraping {city}: {e}")
            continue
    
    return all_venues


def save_progress(venues: list, filename: str):
    """Save venues to JSON file"""
    with open(filename, 'w') as f:
        json.dump(venues, f, indent=2)


def import_to_database(venues: list):
    """Import scraped venues to database"""
    print("\n" + "=" * 80)
    print("IMPORTING TO DATABASE")
    print("=" * 80)
    
    init_db()
    db = SessionLocal()
    
    imported = 0
    skipped = 0
    
    try:
        for venue in venues:
            if import_detailed_venue(venue, db):
                imported += 1
            else:
                skipped += 1
            
            if (imported + skipped) % 100 == 0:
                db.commit()
                print(f"Progress: {imported} imported, {skipped} skipped")
        
        db.commit()
        
        print(f"\n✅ Import complete!")
        print(f"   Imported: {imported}")
        print(f"   Skipped (duplicates): {skipped}")
        print(f"   Total: {imported + skipped}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()


def main():
    """Main execution"""
    
    # Check for API key
    api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    
    if not api_key:
        print("\n❌ ERROR: GOOGLE_MAPS_API_KEY not found!")
        print("\nSetup instructions:")
        print("1. Go to: https://console.cloud.google.com/")
        print("2. Create project → Enable 'Places API'")
        print("3. Create API Key")
        print("4. Add to .env file:")
        print("   GOOGLE_MAPS_API_KEY=your_key_here")
        print("\nThen run this script again.")
        return
    
    print(f"\n✅ API Key found: {api_key[:20]}...")
    
    # Ask for confirmation
    print("\n⚠️  This will use your Google Maps API quota")
    print("Estimated cost: $50-100 for 5,000+ venues")
    
    response = input("\nProceed? (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        print("Cancelled.")
        return
    
    # Choose number of cities
    print("\nHow many cities to scrape?")
    print("  10 cities  = ~500 venues  (~$5-10)")
    print("  50 cities  = ~2,500 venues (~$25-50)")
    print("  100 cities = ~5,000 venues (~$50-100)")
    
    try:
        num_cities = int(input("\nNumber of cities (1-100): "))
        num_cities = max(1, min(100, num_cities))
    except:
        num_cities = 10
        print(f"Using default: {num_cities} cities")
    
    # Scrape
    venues = scrape_all_venues(api_key, num_cities)
    
    # Save results
    output_file = 'google_maps_venues.json'
    save_progress(venues, output_file)
    
    print(f"\n💾 Saved {len(venues)} venues to: {output_file}")
    
    # The import now happens automatically after each city.
    # We just need to confirm the final numbers.
    if os.path.exists('skaters.db'):
        print("\nDatabase import was successful.")
    
    print("\n" + "=" * 80)
    print("✅ COMPLETE!")
    print("=" * 80)
    print(f"\nTotal venues scraped: {len(venues)}")
    print(f"Data saved to: {output_file}")
    print("\nYour directory now has REAL venue data!")


if __name__ == "__main__":
    main()
