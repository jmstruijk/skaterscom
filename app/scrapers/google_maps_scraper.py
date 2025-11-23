"""
Google Maps Places API scraper - REAL DATA
This is the most reliable way to get real venue data

Setup:
1. Go to https://console.cloud.google.com/
2. Enable "Places API"
3. Create API key
4. Add to .env: GOOGLE_MAPS_API_KEY=your_key_here

Free tier: 28,000 requests/month
Cost: $5 per 1,000 requests after free tier
"""

import os
import requests
from typing import List, Dict
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GoogleMapsVenueScraper:
    """Scrape real venue data from Google Maps Places API"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('GOOGLE_MAPS_API_KEY')
        if not self.api_key:
            raise ValueError("Google Maps API key required. Set GOOGLE_MAPS_API_KEY in .env")
        
        self.base_url = "https://maps.googleapis.com/maps/api/place"
        self.venues = []
    
    def search_skateparks(self, city: str, state: str, radius: int = 50000) -> List[Dict]:
        """
        Search for skateparks in a city
        
        Args:
            city: City name
            state: State code (e.g., 'CA', 'NY')
            radius: Search radius in meters (default 50km)
        """
        query = f"skatepark in {city}, {state}"
        return self._search_places(query, 'skateboarding')
    
    def search_ice_rinks(self, city: str, state: str) -> List[Dict]:
        """Search for ice rinks"""
        query = f"ice skating rink in {city}, {state}"
        return self._search_places(query, 'ice_skating')
    
    def search_roller_rinks(self, city: str, state: str) -> List[Dict]:
        """Search for roller rinks"""
        query = f"roller skating rink in {city}, {state}"
        return self._search_places(query, 'roller_skating')
    
    def _search_places(self, query: str, sport_type: str) -> List[Dict]:
        """Search Google Places API"""
        
        url = f"{self.base_url}/textsearch/json"
        params = {
            'query': query,
            'key': self.api_key
        }
        
        logger.info(f"Searching: {query}")
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data['status'] != 'OK':
                logger.warning(f"API returned status: {data['status']}")
                return []
            
            results = data.get('results', [])
            logger.info(f"Found {len(results)} results")
            
            venues = []
            for place in results:
                venue = self._parse_place(place, sport_type)
                if venue:
                    venues.append(venue)
                    self.venues.append(venue)
            
            # Handle pagination
            next_page_token = data.get('next_page_token')
            if next_page_token:
                time.sleep(2)  # Required delay for next page
                venues.extend(self._get_next_page(next_page_token, sport_type))
            
            return venues
            
        except Exception as e:
            logger.error(f"Error searching places: {e}")
            return []
    
    def _get_next_page(self, page_token: str, sport_type: str) -> List[Dict]:
        """Get next page of results"""
        url = f"{self.base_url}/textsearch/json"
        params = {
            'pagetoken': page_token,
            'key': self.api_key
        }
        
        try:
            response = requests.get(url, params=params)
            data = response.json()
            
            results = data.get('results', [])
            venues = []
            for place in results:
                venue = self._parse_place(place, sport_type)
                if venue:
                    venues.append(venue)
                    self.venues.append(venue)
            
            return venues
        except Exception as e:
            logger.error(f"Error getting next page: {e}")
            return []
    
    def _parse_place(self, place: Dict, sport_type: str) -> Dict:
        """Parse Google Place into our venue format"""
        
        # Extract address components
        address_parts = place.get('formatted_address', '').split(', ')
        
        city = ''
        state = ''
        zip_code = ''
        
        if len(address_parts) >= 3:
            city = address_parts[-3]
            state_zip = address_parts[-2].split(' ')
            if len(state_zip) >= 1:
                state = state_zip[0]
            if len(state_zip) >= 2:
                zip_code = state_zip[1]
        
        # Get location
        location = place.get('geometry', {}).get('location', {})
        
        return {
            'name': place.get('name', 'Unknown'),
            'sport_type': sport_type,
            'venue_type': self._get_venue_type(sport_type),
            'address': place.get('formatted_address', ''),
            'city': city,
            'state': state,
            'zip_code': zip_code,
            'country': 'US',
            'latitude': location.get('lat'),
            'longitude': location.get('lng'),
            'rating': place.get('rating', 0.0),
            'review_count': place.get('user_ratings_total', 0),
            'google_place_id': place.get('place_id'),
            'description': f"{place.get('name')} - {place.get('formatted_address')}",
        }
    
    def _get_venue_type(self, sport_type: str) -> str:
        """Map sport type to venue type"""
        mapping = {
            'skateboarding': 'skatepark',
            'ice_skating': 'ice_rink',
            'roller_skating': 'roller_rink',
            'inline_skating': 'trail'
        }
        return mapping.get(sport_type, 'venue')
    
    def get_place_details(self, place_id: str) -> Dict:
        """Get detailed information about a place"""
        url = f"{self.base_url}/details/json"
        params = {
            'place_id': place_id,
            'fields': 'name,formatted_address,formatted_phone_number,website,opening_hours,photos,rating,user_ratings_total',
            'key': self.api_key
        }
        
        try:
            response = requests.get(url, params=params)
            data = response.json()
            
            if data['status'] == 'OK':
                return data.get('result', {})
            
        except Exception as e:
            logger.error(f"Error getting place details: {e}")
        
        return {}


# Example usage
if __name__ == "__main__":
    print("""
╔════════════════════════════════════════════════════════════════╗
║  GOOGLE MAPS VENUE SCRAPER - REAL DATA                        ║
╚════════════════════════════════════════════════════════════════╝

This scraper uses Google Maps Places API to get REAL venue data.

SETUP REQUIRED:
1. Go to: https://console.cloud.google.com/
2. Create a project
3. Enable "Places API"
4. Create API credentials (API Key)
5. Add to .env file: GOOGLE_MAPS_API_KEY=your_key_here

PRICING:
- Free tier: 28,000 requests/month
- After free tier: $5 per 1,000 requests
- Each city search = 1-3 requests (depending on results)

EXAMPLE:
    scraper = GoogleMapsVenueScraper()
    venues = scraper.search_skateparks('Los Angeles', 'CA')
    print(f"Found {len(venues)} skateparks")

This will give you REAL, verified data with:
- Accurate addresses
- Phone numbers
- Websites
- Real ratings and reviews
- Operating hours
- Photos
    """)
    
    # Check if API key is set
    api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    if not api_key:
        print("\n❌ ERROR: GOOGLE_MAPS_API_KEY not found in environment")
        print("\nTo set it up:")
        print("1. Get API key from Google Cloud Console")
        print("2. Add to .env file: GOOGLE_MAPS_API_KEY=your_key_here")
        print("3. Run this script again")
    else:
        print(f"\n✅ API Key found: {api_key[:10]}...")
        print("\nReady to scrape real data!")
