"""
Web scraping infrastructure for venue data collection
"""

from .base import BaseScraper
from .concrete_disciples import ConcreteDisciplesMockScraper
from .rinkatlas import RinkAtlasMockScraper
from .rinktime import RinkTimeMockScraper
from .traillink import TrailLinkMockScraper

__all__ = [
    'BaseScraper',
    'ConcreteDisciplesMockScraper',
    'RinkAtlasMockScraper',
    'RinkTimeMockScraper',
    'TrailLinkMockScraper'
]
