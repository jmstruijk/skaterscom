"""
Test script to verify all SEO URLs are working
Run with: python test_seo_urls.py
"""

import httpx
import asyncio
from typing import List, Tuple

BASE_URL = "http://localhost:8000"

# All SEO URLs to test
SEO_URLS = {
    "Homepage & Core": [
        "/",
    ],
    "Hub Pages": [
        "/ice-rinks",
    ],
    "Near Me Pages": [
        "/near-me",
        "/skate-parks/near-me",
        "/ice-rinks/near-me",
        "/roller-rinks/near-me",
        "/indoor-skate-parks/near-me",
        "/outdoor-skate-parks/near-me",
        "/outdoor-ice-rinks/near-me",
        "/indoor-ice-rinks/near-me",
    ],
    "Location Pages": [
        "/locations/states",
        "/locations/ca",
        "/locations/ny",
        "/locations/tx",
        "/locations/ca/los-angeles",
        "/locations/ny/new-york",
        "/locations/tx/houston",
    ],
    "Sport-Specific City Pages": [
        "/skate-parks/ca/los-angeles",
        "/skate-parks/ny/new-york",
        "/ice-rinks/ny/new-york",
        "/ice-rinks/il/chicago",
        "/roller-rinks/nv/las-vegas",
        "/roller-rinks/ny/new-york",
    ],
    "SEO Pages": [
        "/robots.txt",
        "/sitemap.xml",
    ],
}

async def test_url(client: httpx.AsyncClient, url: str) -> Tuple[str, int, str]:
    """Test a single URL and return status"""
    try:
        response = await client.get(url, follow_redirects=True)
        status = response.status_code
        
        if status == 200:
            result = "✅ OK"
        elif status == 404:
            result = "❌ NOT FOUND"
        elif status == 500:
            result = "❌ SERVER ERROR"
        else:
            result = f"⚠️  {status}"
            
        return (url, status, result)
    except Exception as e:
        return (url, 0, f"❌ ERROR: {str(e)}")

async def test_all_urls():
    """Test all SEO URLs"""
    print("=" * 80)
    print("SEO URL Testing - Skaters.com")
    print("=" * 80)
    print(f"\nBase URL: {BASE_URL}")
    print(f"Testing {sum(len(urls) for urls in SEO_URLS.values())} URLs...\n")
    
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10.0) as client:
        all_results = []
        
        for category, urls in SEO_URLS.items():
            print(f"\n{'='*80}")
            print(f"{category} ({len(urls)} URLs)")
            print(f"{'='*80}")
            
            # Test all URLs in this category
            tasks = [test_url(client, url) for url in urls]
            results = await asyncio.gather(*tasks)
            
            # Print results
            for url, status, result in results:
                print(f"{result:20} {url}")
                all_results.append((category, url, status, result))
        
        # Summary
        print(f"\n{'='*80}")
        print("SUMMARY")
        print(f"{'='*80}")
        
        total = len(all_results)
        success = sum(1 for _, _, status, _ in all_results if status == 200)
        not_found = sum(1 for _, _, status, _ in all_results if status == 404)
        errors = sum(1 for _, _, status, _ in all_results if status not in [200, 404])
        
        print(f"\nTotal URLs Tested: {total}")
        print(f"✅ Success (200):   {success} ({success/total*100:.1f}%)")
        print(f"❌ Not Found (404): {not_found} ({not_found/total*100:.1f}%)")
        print(f"⚠️  Errors:          {errors} ({errors/total*100:.1f}%)")
        
        # List failures
        failures = [(cat, url, status) for cat, url, status, result in all_results if status != 200]
        if failures:
            print(f"\n{'='*80}")
            print("FAILED URLs")
            print(f"{'='*80}")
            for cat, url, status in failures:
                print(f"[{cat}] {url} - Status: {status}")
        else:
            print("\n🎉 All URLs working perfectly!")

if __name__ == "__main__":
    print("\n⚠️  Make sure the server is running on http://localhost:8000")
    print("Run: uvicorn app.main:app --reload\n")
    
    try:
        asyncio.run(test_all_urls())
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test failed: {e}")
