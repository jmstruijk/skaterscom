"""
Concrete Disciples scraper for skateparks
Source: https://www.concretedisciples.com/
Coverage: 2,300+ US skateparks
"""

from .base import BaseScraper
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class ConcreteDisciplesScraper(BaseScraper):
    """Scraper for Concrete Disciples skatepark directory"""
    
    BASE_URL = "https://www.concretedisciples.com"
    
    # Sample state URLs - in production, iterate through all states
    STATE_URLS = {
        'CA': '/california-skateparks',
        'NY': '/new-york-skateparks',
        'TX': '/texas-skateparks',
        'FL': '/florida-skateparks',
        'OR': '/oregon-skateparks',
    }
    
    def scrape(self, states: List[str] = None) -> List[Dict]:
        """
        Scrape skateparks from Concrete Disciples
        
        Args:
            states: List of state codes to scrape (None = all)
            
        Returns:
            List of venue dictionaries
        """
        if states is None:
            states = list(self.STATE_URLS.keys())
        
        logger.info(f"Starting Concrete Disciples scrape for states: {states}")
        
        for state in states:
            if state not in self.STATE_URLS:
                logger.warning(f"No URL mapping for state: {state}")
                continue
            
            state_url = f"{self.BASE_URL}{self.STATE_URLS[state]}"
            self._scrape_state(state_url, state)
        
        logger.info(f"Scraped {len(self.venues_scraped)} skateparks from Concrete Disciples")
        return self.venues_scraped
    
    def _scrape_state(self, url: str, state: str):
        """Scrape all parks from a state page"""
        soup = self.fetch_page(url)
        if not soup:
            logger.error(f"Failed to fetch state page: {url}")
            return
        
        # NOTE: This is a template - actual selectors need to be updated
        # based on the real website structure
        
        # Find all skatepark listings
        park_listings = soup.find_all('div', class_='skatepark-listing')
        
        if not park_listings:
            # Try alternative selectors
            park_listings = soup.find_all('article', class_='park')
            
        logger.info(f"Found {len(park_listings)} parks in {state}")
        
        for listing in park_listings:
            try:
                venue_data = self._parse_park_listing(listing, state)
                if venue_data:
                    normalized = self.normalize_venue_data(venue_data)
                    self.venues_scraped.append(normalized)
            except Exception as e:
                logger.error(f"Error parsing park listing: {e}")
                continue
    
    def _parse_park_listing(self, listing, state: str) -> Dict:
        """Parse individual park listing"""
        # NOTE: Update selectors based on actual website structure
        
        name_elem = listing.find('h2') or listing.find('h3') or listing.find('a', class_='park-name')
        name = self.clean_text(name_elem.text) if name_elem else "Unknown Park"
        
        # Extract city
        city_elem = listing.find(class_='city') or listing.find(class_='location')
        city = self.clean_text(city_elem.text) if city_elem else ""
        
        # Extract address
        address_elem = listing.find(class_='address')
        address = self.clean_text(address_elem.text) if address_elem else ""
        
        # Extract description
        desc_elem = listing.find(class_='description') or listing.find('p')
        description = self.clean_text(desc_elem.text) if desc_elem else f"Skatepark located in {city}, {state}"
        
        # Extract coordinates if available
        lat_elem = listing.get('data-lat') or listing.find(attrs={'data-latitude': True})
        lon_elem = listing.get('data-lng') or listing.find(attrs={'data-longitude': True})
        
        latitude = float(lat_elem) if lat_elem and str(lat_elem).replace('.', '').replace('-', '').isdigit() else None
        longitude = float(lon_elem) if lon_elem and str(lon_elem).replace('.', '').replace('-', '').isdigit() else None
        
        return {
            'name': name,
            'sport_type': 'skateboarding',
            'discipline': 'street',
            'venue_type': 'skatepark',
            'address': address,
            'city': city,
            'state': state,
            'country': 'US',
            'latitude': latitude,
            'longitude': longitude,
            'description': description,
        }


# Demo/Mock scraper that generates sample data without hitting real websites
class ConcreteDisciplesMockScraper(BaseScraper):
    """Mock scraper for testing - generates sample skatepark data"""
    
    SAMPLE_PARKS = [
        {
            'name': 'Burnside Skatepark',
            'city': 'Portland',
            'state': 'OR',
            'address': 'SE 2nd Ave & Burnside St',
            'zip_code': '97214',
            'latitude': 45.5231,
            'longitude': -122.6655,
            'description': 'Legendary DIY skatepark built under the Burnside Bridge. Features concrete bowls, transitions, and unique obstacles. A must-visit for any serious skater.',
            'year_opened': 1990,
        },
        {
            'name': 'Lincoln City Skatepark',
            'city': 'Lincoln City',
            'state': 'OR',
            'address': '2150 NE Oar Ave',
            'zip_code': '97367',
            'latitude': 44.9987,
            'longitude': -124.0182,
            'description': '20,000 square foot outdoor concrete skatepark with street course, flow bowl, and beginner area. Free admission and well-maintained.',
            'year_opened': 2008,
        },
        {
            'name': 'Pier Park Skatepark',
            'city': 'Portland',
            'state': 'OR',
            'address': '9341 N Bruce Ave',
            'zip_code': '97203',
            'latitude': 45.5897,
            'longitude': -122.7614,
            'description': 'Large outdoor skatepark with multiple bowls, street plaza, and vert ramp. One of Portland\'s premier skateparks.',
            'year_opened': 2007,
        },
        {
            'name': 'Tualatin Skatepark',
            'city': 'Tualatin',
            'state': 'OR',
            'address': '8515 SW Tualatin Rd',
            'zip_code': '97062',
            'latitude': 45.3784,
            'longitude': -122.7645,
            'description': 'Modern concrete skatepark with flowing transitions, street obstacles, and a large bowl. Great for all skill levels.',
            'year_opened': 2015,
        },
        {
            'name': 'Newberg Skatepark',
            'city': 'Newberg',
            'state': 'OR',
            'address': '401 E Hancock St',
            'zip_code': '97132',
            'latitude': 45.3001,
            'longitude': -122.9731,
            'description': 'Community skatepark featuring street course and bowl sections. Popular local spot with good lighting for evening sessions.',
            'year_opened': 2010,
        },
    ]
    
    def scrape(self) -> List[Dict]:
        """Generate mock skatepark data"""
        logger.info("Generating mock skatepark data...")
        
        for park_data in self.SAMPLE_PARKS:
            park_data['sport_type'] = 'skateboarding'
            park_data['discipline'] = 'street'
            park_data['venue_type'] = 'skatepark'
            park_data['country'] = 'US'
            
            normalized = self.normalize_venue_data(park_data)
            self.venues_scraped.append(normalized)
        
        logger.info(f"Generated {len(self.venues_scraped)} mock skateparks")
        return self.venues_scraped
