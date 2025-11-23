"""
REAL Concrete Disciples scraper - actually scrapes the website
"""

from .base import BaseScraper
from typing import List, Dict
import logging
import re

logger = logging.getLogger(__name__)


class ConcreteDisciplesRealScraper(BaseScraper):
    """Real scraper for Concrete Disciples skatepark directory"""
    
    BASE_URL = "https://www.concretedisciples.com"
    
    # All US states
    STATES = [
        'alabama', 'alaska', 'arizona', 'arkansas', 'northern-california', 'southern-california',
        'colorado-skateparks', 'connecticut', 'delaware', 'florida-skateparks', 'georgia',
        'hawaii', 'idaho', 'illinois', 'indiana', 'iowa', 'kansas', 'kentucky',
        'louisiana', 'maine', 'maryland', 'massachusetts', 'michigan', 'minnesota',
        'mississippi', 'missouri', 'montana', 'nebraska', 'nevada', 'new-hampshire',
        'new-jersey', 'new-mexico', 'new-york-skateparks', 'north-carolina', 'north-dakota',
        'ohio', 'oklahoma', 'oregon-skateparks', 'pennsylvania', 'rhode-island',
        'south-carolina', 'south-dakota', 'tennessee', 'texas-skateparks', 'utah',
        'vermont', 'virginia', 'washington', 'west-virginia', 'wisconsin', 'wyoming'
    ]
    
    def scrape(self, max_states: int = 5, max_parks_per_state: int = 20) -> List[Dict]:
        """
        Scrape skateparks from Concrete Disciples
        
        Args:
            max_states: Maximum number of states to scrape (for testing)
            max_parks_per_state: Maximum parks per state
            
        Returns:
            List of venue dictionaries
        """
        logger.info(f"Starting Concrete Disciples REAL scrape (max {max_states} states)")
        
        states_to_scrape = self.STATES[:max_states]
        
        for state in states_to_scrape:
            state_url = f"{self.BASE_URL}/global-skatepark-directory/usa-skateparks-guide/{state}/"
            logger.info(f"\n📍 Scraping state: {state}")
            logger.info(f"   URL: {state_url}")
            
            self._scrape_state_page(state_url, state, max_parks_per_state)
        
        logger.info(f"\n✅ Scraped {len(self.venues_scraped)} skateparks from Concrete Disciples")
        return self.venues_scraped
    
    def _scrape_state_page(self, url: str, state: str, max_parks: int):
        """Scrape all parks from a state page"""
        soup = self.fetch_page(url)
        if not soup:
            logger.error(f"Failed to fetch state page: {url}")
            return
        
        # Find all skatepark links on the page
        park_links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            # Look for individual park pages
            if '/global-skatepark-directory/' in href and href.count('/') > 5:
                if href not in park_links:
                    park_links.append(href)
        
        logger.info(f"   Found {len(park_links)} park links")
        
        # Scrape each park (limit for testing)
        for i, park_url in enumerate(park_links[:max_parks]):
            if i >= max_parks:
                break
            
            try:
                park_data = self._scrape_park_page(park_url, state)
                if park_data:
                    normalized = self.normalize_venue_data(park_data)
                    self.venues_scraped.append(normalized)
                    logger.info(f"   ✅ [{i+1}/{min(len(park_links), max_parks)}] {park_data['name']}")
            except Exception as e:
                logger.error(f"   ❌ Error scraping {park_url}: {e}")
                continue
    
    def _scrape_park_page(self, url: str, state: str) -> Dict:
        """Scrape individual park page"""
        soup = self.fetch_page(url)
        if not soup:
            return None
        
        # Extract park name from title or h1
        name = "Unknown Park"
        title_tag = soup.find('h1', class_='entry-title')
        if title_tag:
            name = self.clean_text(title_tag.text)
        elif soup.title:
            name = self.clean_text(soup.title.string.split('|')[0])
        
        # Extract description
        description = ""
        content_div = soup.find('div', class_='entry-content')
        if content_div:
            paragraphs = content_div.find_all('p')
            if paragraphs:
                description = self.clean_text(paragraphs[0].text)
        
        # Try to extract address from content
        address = ""
        city = ""
        
        # Look for address patterns in text
        full_text = soup.get_text()
        
        # Try to find city from URL or content
        url_parts = url.split('/')
        if len(url_parts) > 2:
            city_slug = url_parts[-2]
            city = city_slug.replace('-', ' ').title()
        
        # Extract coordinates if available
        latitude = None
        longitude = None
        
        # Look for Google Maps links or coordinates
        for link in soup.find_all('a', href=True):
            href = link['href']
            if 'google.com/maps' in href or 'maps.google' in href:
                # Try to extract coordinates from Google Maps URL
                coord_match = re.search(r'@(-?\d+\.\d+),(-?\d+\.\d+)', href)
                if coord_match:
                    latitude = float(coord_match.group(1))
                    longitude = float(coord_match.group(2))
                    break
        
        # Get state code from state name
        state_code = self._get_state_code(state)
        
        return {
            'name': name,
            'sport_type': 'skateboarding',
            'discipline': 'street',
            'venue_type': 'skatepark',
            'address': address,
            'city': city,
            'state': state_code,
            'country': 'US',
            'latitude': latitude,
            'longitude': longitude,
            'description': description if description else f"Skatepark in {city}, {state_code}",
            'website': url,  # Use the Concrete Disciples page as website
        }
    
    def _get_state_code(self, state_slug: str) -> str:
        """Convert state slug to state code"""
        state_map = {
            'alabama': 'AL', 'alaska': 'AK', 'arizona': 'AZ', 'arkansas': 'AR',
            'northern-california': 'CA', 'southern-california': 'CA',
            'colorado-skateparks': 'CO', 'connecticut': 'CT', 'delaware': 'DE',
            'florida-skateparks': 'FL', 'georgia': 'GA', 'hawaii': 'HI',
            'idaho': 'ID', 'illinois': 'IL', 'indiana': 'IN', 'iowa': 'IA',
            'kansas': 'KS', 'kentucky': 'KY', 'louisiana': 'LA', 'maine': 'ME',
            'maryland': 'MD', 'massachusetts': 'MA', 'michigan': 'MI',
            'minnesota': 'MN', 'mississippi': 'MS', 'missouri': 'MO',
            'montana': 'MT', 'nebraska': 'NE', 'nevada': 'NV',
            'new-hampshire': 'NH', 'new-jersey': 'NJ', 'new-mexico': 'NM',
            'new-york-skateparks': 'NY', 'north-carolina': 'NC',
            'north-dakota': 'ND', 'ohio': 'OH', 'oklahoma': 'OK',
            'oregon-skateparks': 'OR', 'pennsylvania': 'PA',
            'rhode-island': 'RI', 'south-carolina': 'SC', 'south-dakota': 'SD',
            'tennessee': 'TN', 'texas-skateparks': 'TX', 'utah': 'UT',
            'vermont': 'VT', 'virginia': 'VA', 'washington': 'WA',
            'west-virginia': 'WV', 'wisconsin': 'WI', 'wyoming': 'WY'
        }
        return state_map.get(state_slug, 'XX')
