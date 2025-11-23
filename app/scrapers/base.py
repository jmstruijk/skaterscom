"""
Base scraper class with common functionality
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import time
import logging
from abc import ABC, abstractmethod
from slugify import slugify

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """Base class for all venue scrapers"""
    
    def __init__(self, delay: float = 1.0):
        """
        Initialize scraper
        
        Args:
            delay: Delay between requests in seconds (be respectful!)
        """
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        })
        self.venues_scraped = []
    
    def fetch_page(self, url: str, retries: int = 3) -> Optional[BeautifulSoup]:
        """
        Fetch and parse a web page
        
        Args:
            url: URL to fetch
            retries: Number of retry attempts
            
        Returns:
            BeautifulSoup object or None if failed
        """
        for attempt in range(retries):
            try:
                logger.info(f"Fetching: {url} (attempt {attempt + 1}/{retries})")
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                time.sleep(self.delay)  # Be respectful
                return BeautifulSoup(response.content, 'html.parser')
            except requests.RequestException as e:
                logger.error(f"Error fetching {url}: {e}")
                if attempt < retries - 1:
                    time.sleep(self.delay * 2)  # Wait longer before retry
                else:
                    return None
    
    def clean_text(self, text: Optional[str]) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        return " ".join(text.strip().split())
    
    def extract_phone(self, text: str) -> Optional[str]:
        """Extract phone number from text"""
        import re
        # Match common US phone formats
        phone_pattern = r'(\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        match = re.search(phone_pattern, text)
        return match.group(0) if match else None
    
    def extract_email(self, text: str) -> Optional[str]:
        """Extract email from text"""
        import re
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        match = re.search(email_pattern, text)
        return match.group(0) if match else None
    
    def generate_slug(self, name: str, city: str = "", state: str = "") -> str:
        """Generate unique slug for venue"""
        parts = [name]
        if city:
            parts.append(city)
        if state:
            parts.append(state)
        return slugify("-".join(parts))
    
    def normalize_venue_data(self, raw_data: Dict) -> Dict:
        """
        Normalize raw scraped data to standard format
        
        Args:
            raw_data: Raw venue data from scraper
            
        Returns:
            Normalized venue dictionary
        """
        return {
            'name': self.clean_text(raw_data.get('name', '')),
            'slug': self.generate_slug(
                raw_data.get('name', ''),
                raw_data.get('city', ''),
                raw_data.get('state', '')
            ),
            'sport_type': raw_data.get('sport_type', 'skateboarding'),
            'discipline': raw_data.get('discipline'),
            'venue_type': raw_data.get('venue_type', 'skatepark'),
            'address': self.clean_text(raw_data.get('address', '')),
            'city': self.clean_text(raw_data.get('city', '')),
            'state': raw_data.get('state', '').upper() if raw_data.get('state') else '',
            'zip_code': raw_data.get('zip_code', ''),
            'country': raw_data.get('country', 'US'),
            'latitude': raw_data.get('latitude'),
            'longitude': raw_data.get('longitude'),
            'phone': self.extract_phone(raw_data.get('phone', '')) if raw_data.get('phone') else None,
            'email': self.extract_email(raw_data.get('email', '')) if raw_data.get('email') else None,
            'website': raw_data.get('website'),
            'description': self.clean_text(raw_data.get('description', '')),
            'year_opened': raw_data.get('year_opened'),
            'verified': False,  # Scraped data needs verification
            'status': 'active',
            'rating': 0.0,
            'review_count': 0,
            'meta_title': f"{raw_data.get('name', '')} | {raw_data.get('city', '')}, {raw_data.get('state', '')} | Skaters.com",
            'meta_description': self.clean_text(raw_data.get('description', ''))[:160],
            'seo_keywords': f"{raw_data.get('sport_type', '')}, {raw_data.get('venue_type', '')}, {raw_data.get('city', '')}, {raw_data.get('state', '')}"
        }
    
    @abstractmethod
    def scrape(self) -> List[Dict]:
        """
        Main scraping method - must be implemented by subclasses
        
        Returns:
            List of normalized venue dictionaries
        """
        pass
    
    def get_results(self) -> List[Dict]:
        """Get scraped and normalized results"""
        return self.venues_scraped
    
    def save_to_json(self, filename: str):
        """Save results to JSON file"""
        import json
        with open(filename, 'w') as f:
            json.dump(self.venues_scraped, f, indent=2)
        logger.info(f"Saved {len(self.venues_scraped)} venues to {filename}")
