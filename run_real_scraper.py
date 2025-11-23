"""
Run the REAL scraper and show output
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from app.scrapers.concrete_disciples_real import ConcreteDisciplesRealScraper
import json

def main():
    print("=" * 80)
    print("RUNNING REAL CONCRETE DISCIPLES SCRAPER")
    print("=" * 80)
    print("\nThis will scrape actual data from concretedisciples.com")
    print("Please be patient, this respects rate limits (1 second between requests)\n")
    
    # Create scraper
    scraper = ConcreteDisciplesRealScraper(delay=1.5)  # 1.5 seconds between requests
    
    # Scrape (limit to 3 states, 10 parks each for testing)
    print("Scraping 3 states, max 10 parks per state...\n")
    venues = scraper.scrape(max_states=3, max_parks_per_state=10)
    
    print("\n" + "=" * 80)
    print(f"SCRAPING COMPLETE - Found {len(venues)} skateparks")
    print("=" * 80)
    
    # Show sample results
    print("\n📊 SAMPLE RESULTS (first 5):\n")
    for i, venue in enumerate(venues[:5], 1):
        print(f"{i}. {venue['name']}")
        print(f"   Location: {venue['city']}, {venue['state']}")
        print(f"   Coordinates: {venue['latitude']}, {venue['longitude']}")
        print(f"   Description: {venue['description'][:100]}...")
        print()
    
    # Save to JSON
    output_file = 'scraped_skateparks.json'
    with open(output_file, 'w') as f:
        json.dump(venues, f, indent=2)
    
    print(f"💾 Saved all {len(venues)} venues to: {output_file}")
    
    # Show statistics
    print("\n📈 STATISTICS:")
    states = {}
    for venue in venues:
        state = venue['state']
        states[state] = states.get(state, 0) + 1
    
    for state, count in sorted(states.items()):
        print(f"   {state}: {count} parks")
    
    print(f"\n   TOTAL: {len(venues)} skateparks scraped")
    
    return venues

if __name__ == "__main__":
    venues = main()
    
    print("\n" + "=" * 80)
    print("✅ SUCCESS! Real data scraped from Concrete Disciples")
    print("=" * 80)
    print("\nNext steps:")
    print("1. Review scraped_skateparks.json")
    print("2. Import into database with: python app/scrapers/import_venues.py")
    print("3. Increase max_states to scrape more data")
    print("4. Add more scrapers for ice rinks, roller rinks, trails")
    print()
