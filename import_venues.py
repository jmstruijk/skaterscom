import json
import sqlite3
from datetime import datetime
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

# Database connection
conn = sqlite3.connect('/Users/johan/Projects/skaters-python/skaters.db')
cursor = conn.cursor()

# Load the JSON data
with open('/Users/johan/Projects/skaters-python/google_maps_venues.json', 'r') as f:
    venues = json.load(f)

# Function to convert sport_type to the correct format
def convert_sport_type(sport_type):
    # Convert snake_case to UPPER_SNAKE_CASE
    if not sport_type:
        return 'UNKNOWN'
    return sport_type.upper()

# Function to process photo URL
def process_photo_url(photo):
    if not photo:
        return None
        
    if isinstance(photo, dict):
        # If it's a dictionary, extract the photo_reference
        photo_ref = photo.get('photo_reference')
        if not photo_ref:
            return None
            
        # Construct the photo URL
        base_url = "https://maps.googleapis.com/maps/api/place/photo"
        params = {
            'maxwidth': '800',
            'photoreference': photo_ref,
            'key': 'YOUR_GOOGLE_API_KEY'  # Replace with your API key
        }
        return f"{base_url}?{urlencode(params)}"
        
    elif isinstance(photo, str):
        # If it's already a URL, ensure it has maxwidth parameter
        parsed = urlparse(photo)
        query = parse_qs(parsed.query)
        if 'maxwidth' not in query:
            query['maxwidth'] = ['800']
            parsed = parsed._replace(query=urlencode(query, doseq=True))
            return urlunparse(parsed)
        return photo
    
    return None

# Prepare the SQL for inserting venues
insert_venue_sql = """
INSERT OR IGNORE INTO venues (
    name, slug, sport_type, city, state, country, 
    latitude, longitude, address, phone, website, 
    rating, review_count, google_place_id, 
    description, created_at, updated_at, status
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
"""

# Prepare the SQL for inserting photos (without width and height)
insert_photo_sql = """
INSERT OR IGNORE INTO venue_photos (
    venue_id, url, caption, is_primary, 
    created_at, updated_at
) VALUES (?, ?, ?, ?, ?, ?)
"""

# Get existing venue IDs to avoid duplicates
cursor.execute("SELECT google_place_id FROM venues WHERE google_place_id IS NOT NULL")
existing_place_ids = {row[0] for row in cursor.fetchall()}

# Process each venue
for venue_data in venues:
    # Skip if already exists
    if not venue_data.get('place_id') or venue_data.get('place_id') in existing_place_ids:
        print(f"Skipping duplicate venue: {venue_data.get('name')}")
        continue
    
    try:
        # Convert sport_type to match database enum
        sport_type = convert_sport_type(venue_data.get('sport_type', 'UNKNOWN'))
        
        # Prepare venue data
        venue_values = (
            venue_data.get('name', ''),
            venue_data.get('slug', ''),
            sport_type,
            venue_data.get('city', ''),
            venue_data.get('state', ''),
            venue_data.get('country', 'US'),
            venue_data.get('latitude'),
            venue_data.get('longitude'),
            venue_data.get('formatted_address', venue_data.get('address', '')),
            venue_data.get('formatted_phone_number', venue_data.get('phone', '')),
            venue_data.get('website', ''),
            float(venue_data.get('rating', 0.0)),
            int(venue_data.get('user_ratings_total', venue_data.get('review_count', 0))),
            venue_data.get('place_id', ''),
            venue_data.get('description', ''),
            datetime.now().isoformat(),
            datetime.now().isoformat(),
            'active'
        )
        
        # Insert the venue
        cursor.execute(insert_venue_sql, venue_values)
        venue_id = cursor.lastrowid
        
        # Process photos if they exist
        photos = venue_data.get('photos', [])
        if isinstance(photos, list) and photos:
            for i, photo in enumerate(photos[:5]):  # Limit to 5 photos per venue
                photo_url = process_photo_url(photo)
                if photo_url:
                    photo_values = (
                        venue_id,
                        photo_url,
                        f"{venue_data.get('name', 'Venue')} - Photo {i+1}",
                        i == 0,  # First photo is primary
                        datetime.now().isoformat(),
                        datetime.now().isoformat()
                    )
                    cursor.execute(insert_photo_sql, photo_values)
        
        print(f"Added venue: {venue_data.get('name')}")
        conn.commit()
        
    except Exception as e:
        print(f"Error processing venue {venue_data.get('name')}: {str(e)}")
        conn.rollback()
        raise  # Re-raise the exception to see full traceback

# Close the connection
conn.close()
print("Import completed successfully!")