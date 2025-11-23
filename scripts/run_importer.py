"""
Run only the database import process from an existing JSON file.
"""

import os
import sys
import json
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from dotenv import load_dotenv
from app.scrapers.google_maps_bulk import import_to_database

def main():
    load_dotenv()
    json_file = 'google_maps_venues.json'

    if not os.path.exists(json_file):
        print(f"\n❌ ERROR: JSON file not found: {json_file}")
        print("Please run the scraper first to generate this file.")
        return

    with open(json_file, 'r') as f:
        venues = json.load(f)
    
    print(f"\nFound {len(venues)} venues in {json_file}.")
    
    if venues:
        print("Starting database import...")
        import_to_database(venues)
    else:
        print("No venues to import.")

if __name__ == "__main__":
    main()
