"""
Test real web scraping to verify scrapers work
"""

import requests
from bs4 import BeautifulSoup
import json

def test_concrete_disciples():
    """Test scraping Concrete Disciples for skateparks"""
    
    print("=" * 80)
    print("TESTING CONCRETE DISCIPLES SCRAPER")
    print("=" * 80)
    
    # Try to fetch the main page
    url = "https://www.concretedisciples.com"
    
    try:
        print(f"\n1. Fetching: {url}")
        response = requests.get(url, timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        print(f"   Status: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('Content-Type')}")
        print(f"   Content Length: {len(response.content)} bytes")
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        print(f"\n2. Page Title: {soup.title.string if soup.title else 'No title'}")
        
        # Look for common elements
        print("\n3. Looking for skatepark listings...")
        
        # Try different selectors
        selectors_to_try = [
            ('div.skatepark', 'div with class skatepark'),
            ('div.park', 'div with class park'),
            ('article', 'article tags'),
            ('div.listing', 'div with class listing'),
            ('a[href*="skatepark"]', 'links containing skatepark'),
        ]
        
        for selector, description in selectors_to_try:
            elements = soup.select(selector)
            if elements:
                print(f"   ✅ Found {len(elements)} elements matching: {description}")
                # Show first few
                for i, elem in enumerate(elements[:3]):
                    print(f"      [{i+1}] {elem.get_text()[:100]}...")
            else:
                print(f"   ❌ No elements found for: {description}")
        
        # Look for state links
        print("\n4. Looking for state navigation...")
        state_links = soup.find_all('a', href=True)
        state_related = [link for link in state_links if 'state' in link['href'].lower() or 
                        any(state in link['href'].lower() for state in ['california', 'texas', 'florida', 'new-york'])]
        
        if state_related:
            print(f"   Found {len(state_related)} state-related links:")
            for link in state_related[:5]:
                print(f"      - {link.get_text()[:50]}: {link['href']}")
        
        # Save sample HTML for inspection
        with open('concrete_disciples_sample.html', 'w') as f:
            f.write(soup.prettify())
        print("\n5. Saved sample HTML to: concrete_disciples_sample.html")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


def test_skatepark_directory():
    """Test alternative skatepark directory"""
    
    print("\n" + "=" * 80)
    print("TESTING SKATEPARK DIRECTORY (Alternative)")
    print("=" * 80)
    
    # Try SkateboardDirectory.com
    url = "https://www.skateboarddirectory.com"
    
    try:
        print(f"\n1. Fetching: {url}")
        response = requests.get(url, timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        print(f"   Status: {response.status_code}")
        
        soup = BeautifulSoup(response.content, 'html.parser')
        print(f"   Title: {soup.title.string if soup.title else 'No title'}")
        
        # Look for park listings
        parks = soup.find_all('div', class_='park')
        print(f"\n2. Found {len(parks)} park listings")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")


def test_public_skatepark_guide():
    """Test Public Skatepark Guide"""
    
    print("\n" + "=" * 80)
    print("TESTING PUBLIC SKATEPARK GUIDE")
    print("=" * 80)
    
    url = "https://publicskateboardguide.org"
    
    try:
        print(f"\n1. Fetching: {url}")
        response = requests.get(url, timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            print(f"   Title: {soup.title.string if soup.title else 'No title'}")
            
            # Save sample
            with open('skatepark_guide_sample.html', 'w') as f:
                f.write(soup.prettify())
            print("   Saved sample to: skatepark_guide_sample.html")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")


def test_ice_rink_sources():
    """Test ice rink data sources"""
    
    print("\n" + "=" * 80)
    print("TESTING ICE RINK SOURCES")
    print("=" * 80)
    
    sources = [
        "https://www.rinkatlas.com",
        "https://www.arenaguide.com",
    ]
    
    for url in sources:
        try:
            print(f"\n1. Testing: {url}")
            response = requests.get(url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            })
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                print(f"   Title: {soup.title.string if soup.title else 'No title'}")
                
                # Look for rink listings
                rinks = soup.find_all(['div', 'article'], class_=lambda x: x and 'rink' in x.lower() if x else False)
                print(f"   Found {len(rinks)} potential rink elements")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")


def show_summary():
    """Show summary and next steps"""
    
    print("\n" + "=" * 80)
    print("SCRAPING TEST SUMMARY")
    print("=" * 80)
    
    print("""
Next Steps:
1. Review the saved HTML files to understand the structure
2. Update scraper selectors based on actual HTML structure
3. Implement proper parsing logic for each source
4. Add error handling and retry logic
5. Test with multiple pages to ensure consistency

Alternative Approaches:
- Use official APIs if available (TrailLink, some city data portals)
- Download bulk datasets (ByteScraper, SmartScrapers - paid)
- Use Google Maps API for venue discovery
- Scrape city recreation department websites
- Use OpenStreetMap data for skateparks/trails

For Production:
- Respect robots.txt
- Add rate limiting (1-2 seconds between requests)
- Use rotating user agents
- Handle pagination
- Store raw HTML for debugging
- Implement data validation
- Add monitoring and alerts
    """)


if __name__ == "__main__":
    print("\n🔍 STARTING WEB SCRAPING TESTS\n")
    
    # Test each source
    test_concrete_disciples()
    test_skatepark_directory()
    test_public_skatepark_guide()
    test_ice_rink_sources()
    
    # Show summary
    show_summary()
    
    print("\n✅ TESTS COMPLETE\n")
