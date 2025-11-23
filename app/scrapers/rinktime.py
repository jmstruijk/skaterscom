"""
RinkTime scraper for roller rinks
Source: https://www.rinktime.com/
Coverage: 500+ US roller rinks
"""

from .base import BaseScraper
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class RinkTimeMockScraper(BaseScraper):
    """Mock scraper for roller rinks - generates sample data"""
    
    SAMPLE_RINKS = [
        {
            'name': 'World on Wheels',
            'city': 'Los Angeles',
            'state': 'CA',
            'address': '4645 Venice Blvd',
            'zip_code': '90019',
            'latitude': 34.0420,
            'longitude': -118.3287,
            'phone': '(323) 933-5170',
            'website': 'https://www.worldonwheelsla.com',
            'description': 'Historic roller rink in LA since 1979. Features 20,000 sq ft maple floor, DJ music, arcade games, and snack bar. Adult night, family skate, and private parties available.',
            'year_opened': 1979,
        },
        {
            'name': 'Skate World Center',
            'city': 'Orlando',
            'state': 'FL',
            'address': '7208 Old Cheney Hwy',
            'zip_code': '32807',
            'latitude': 28.5383,
            'longitude': -81.2849,
            'phone': '(407) 273-1300',
            'website': 'https://www.skateworldcenter.com',
            'description': 'Family-friendly roller skating rink with themed skate nights, birthday parties, and group events. Features modern sound system, lighting effects, and full snack bar.',
            'year_opened': 1985,
        },
        {
            'name': 'Skateland',
            'city': 'Austin',
            'state': 'TX',
            'address': '9514 N Lamar Blvd',
            'zip_code': '78753',
            'latitude': 30.3688,
            'longitude': -97.7002,
            'phone': '(512) 837-1300',
            'website': 'https://www.skatelandaustin.com',
            'description': 'Austin\'s premier roller skating destination with over 30,000 sq ft. Offers public sessions, private parties, skating lessons, and special events. Modern facility with arcade and cafe.',
            'year_opened': 1984,
        },
        {
            'name': 'Oaks Park Roller Rink',
            'city': 'Portland',
            'state': 'OR',
            'address': '7805 SE Oaks Park Way',
            'zip_code': '97202',
            'latitude': 45.4739,
            'longitude': -122.6598,
            'phone': '(503) 233-5777',
            'website': 'https://oakspark.com/skating',
            'description': 'Historic roller rink operating since 1905. Features beautiful hardwood floor, organ music on weekends, and classic skating atmosphere. Part of Oaks Amusement Park.',
            'year_opened': 1905,
        },
        {
            'name': 'United Skates of America',
            'city': 'Miami',
            'state': 'FL',
            'address': '10550 SW 72nd St',
            'zip_code': '33173',
            'latitude': 25.7020,
            'longitude': -80.3665,
            'phone': '(305) 271-6206',
            'website': 'https://www.unitedskates.com',
            'description': 'South Florida\'s largest roller skating rink with 32,000 sq ft floor. Features DJ music, laser lights, arcade, pro shop, and full-service snack bar. Hosts parties and events.',
            'year_opened': 1990,
        },
    ]
    
    def scrape(self) -> List[Dict]:
        """Generate mock roller rink data"""
        logger.info("Generating mock roller rink data...")
        
        for rink_data in self.SAMPLE_RINKS:
            rink_data['sport_type'] = 'roller_skating'
            rink_data['discipline'] = 'recreational'
            rink_data['venue_type'] = 'roller_rink'
            rink_data['country'] = 'US'
            
            normalized = self.normalize_venue_data(rink_data)
            self.venues_scraped.append(normalized)
        
        logger.info(f"Generated {len(self.venues_scraped)} mock roller rinks")
        return self.venues_scraped
