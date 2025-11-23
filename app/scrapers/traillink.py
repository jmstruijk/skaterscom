"""
TrailLink scraper for inline skating paths
Source: https://www.traillink.com/
Coverage: 1,500+ US inline skating trails
"""

from .base import BaseScraper
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class TrailLinkMockScraper(BaseScraper):
    """Mock scraper for inline skating trails - generates sample data"""
    
    SAMPLE_TRAILS = [
        {
            'name': 'Hudson River Greenway',
            'city': 'New York',
            'state': 'NY',
            'address': 'West Side Highway, Manhattan',
            'zip_code': '10014',
            'latitude': 40.7282,
            'longitude': -74.0076,
            'website': 'https://www.hudsonrivergreenway.ny.gov',
            'description': '11-mile paved path along the Hudson River from Battery Park to the George Washington Bridge. Perfect for inline skating with stunning river and city views. Separated from traffic with smooth asphalt surface.',
        },
        {
            'name': 'Lakefront Trail',
            'city': 'Chicago',
            'state': 'IL',
            'address': 'Lake Shore Drive',
            'zip_code': '60611',
            'latitude': 41.8781,
            'longitude': -87.6298,
            'website': 'https://www.chicagoparkdistrict.com/parks-facilities/lakefront-trail',
            'description': '18-mile scenic paved trail along Lake Michigan. Excellent for inline skating with separate lanes for cyclists and pedestrians. Connects multiple beaches and parks with beautiful lake views.',
        },
        {
            'name': 'Santa Monica Beach Path',
            'city': 'Santa Monica',
            'state': 'CA',
            'address': 'Ocean Front Walk',
            'zip_code': '90401',
            'latitude': 34.0095,
            'longitude': -118.4966,
            'website': 'https://www.smgov.net/departments/ccs/content.aspx?id=14073',
            'description': '22-mile paved beachfront path from Santa Monica to Torrance Beach. Popular inline skating destination with ocean views, beach access, and smooth concrete surface. Connects Venice Beach and other iconic locations.',
        },
        {
            'name': 'Katy Trail',
            'city': 'Dallas',
            'state': 'TX',
            'address': 'Various access points in Dallas',
            'zip_code': '75201',
            'latitude': 32.8098,
            'longitude': -96.8016,
            'website': 'https://www.katytraildallas.org',
            'description': '3.5-mile urban trail through Dallas neighborhoods. Smooth concrete surface ideal for inline skating. Connects parks, restaurants, and shopping areas. Well-maintained and lit for evening use.',
        },
        {
            'name': 'Springwater Corridor',
            'city': 'Portland',
            'state': 'OR',
            'address': 'SE McLoughlin Blvd',
            'zip_code': '97202',
            'latitude': 45.4842,
            'longitude': -122.6403,
            'website': 'https://www.portlandoregon.gov/parks/finder/index.cfm?&propertyid=111',
            'description': '21-mile paved multi-use path from downtown Portland to Boring. Excellent for inline skating with mostly flat terrain and smooth asphalt. Passes through wetlands, parks, and urban areas.',
        },
    ]
    
    def scrape(self) -> List[Dict]:
        """Generate mock inline skating trail data"""
        logger.info("Generating mock inline skating trail data...")
        
        for trail_data in self.SAMPLE_TRAILS:
            trail_data['sport_type'] = 'inline_skating'
            trail_data['discipline'] = 'recreational'
            trail_data['venue_type'] = 'trail'
            trail_data['country'] = 'US'
            
            normalized = self.normalize_venue_data(trail_data)
            self.venues_scraped.append(normalized)
        
        logger.info(f"Generated {len(self.venues_scraped)} mock inline skating trails")
        return self.venues_scraped
