"""
RinkAtlas scraper for ice rinks
Source: https://rinkatlas.com/
Coverage: 1,500+ US ice rinks
"""

from .base import BaseScraper
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class RinkAtlasMockScraper(BaseScraper):
    """Mock scraper for ice rinks - generates sample data"""
    
    SAMPLE_RINKS = [
        {
            'name': 'Bryant Park Winter Village Ice Rink',
            'city': 'New York',
            'state': 'NY',
            'address': 'Bryant Park, 6th Ave & 42nd St',
            'zip_code': '10018',
            'latitude': 40.7536,
            'longitude': -73.9832,
            'phone': '(212) 661-6640',
            'website': 'https://bryantpark.org/amenities/the-rink',
            'description': 'Free admission outdoor ice rink in the heart of Manhattan. Open seasonally from October to March. Skate rentals available. Located in beautiful Bryant Park with holiday market.',
            'year_opened': 2002,
        },
        {
            'name': 'Chelsea Piers Sky Rink',
            'city': 'New York',
            'state': 'NY',
            'address': '61 Chelsea Piers',
            'zip_code': '10011',
            'latitude': 40.7469,
            'longitude': -74.0093,
            'phone': '(212) 336-6100',
            'website': 'https://www.chelseapiers.com/skyrink',
            'description': 'Year-round indoor ice rink with two NHL-sized rinks. Offers public skating, hockey leagues, figure skating lessons, and birthday parties. Professional facility with locker rooms and pro shop.',
            'year_opened': 1995,
        },
        {
            'name': 'Wollman Rink',
            'city': 'New York',
            'state': 'NY',
            'address': 'Central Park, 830 5th Ave',
            'zip_code': '10065',
            'latitude': 40.7688,
            'longitude': -73.9748,
            'phone': '(212) 439-6900',
            'website': 'https://wollmanskatingrink.com',
            'description': 'Iconic outdoor ice rink in Central Park with stunning Manhattan skyline views. Seasonal operation from October to April. Featured in many movies. Skate rentals and lessons available.',
            'year_opened': 1950,
        },
        {
            'name': 'Ice at the Parks',
            'city': 'Arlington',
            'state': 'TX',
            'address': '3925 W Arkansas Ln',
            'zip_code': '76016',
            'latitude': 32.7081,
            'longitude': -97.1384,
            'phone': '(817) 467-5600',
            'website': 'https://www.iceattheparks.com',
            'description': 'Premier ice skating facility in Arlington with two regulation-sized rinks. Offers public skating, hockey programs, figure skating, and special events. Modern facility with full amenities.',
            'year_opened': 2008,
        },
        {
            'name': 'Dr Pepper StarCenter Farmers Branch',
            'city': 'Farmers Branch',
            'state': 'TX',
            'address': '13800 Hutton Dr',
            'zip_code': '75234',
            'latitude': 32.9343,
            'longitude': -96.8903,
            'phone': '(972) 241-5005',
            'website': 'https://www.starcenters.com/farmers-branch',
            'description': 'Multi-rink ice facility offering public skating, hockey leagues, figure skating programs, and skating lessons. Part of the StarCenters network with professional coaching staff.',
            'year_opened': 1998,
        },
    ]
    
    def scrape(self) -> List[Dict]:
        """Generate mock ice rink data"""
        logger.info("Generating mock ice rink data...")
        
        for rink_data in self.SAMPLE_RINKS:
            rink_data['sport_type'] = 'ice_skating'
            rink_data['discipline'] = 'recreational'
            rink_data['venue_type'] = 'ice_rink'
            rink_data['country'] = 'US'
            
            normalized = self.normalize_venue_data(rink_data)
            self.venues_scraped.append(normalized)
        
        logger.info(f"Generated {len(self.venues_scraped)} mock ice rinks")
        return self.venues_scraped
