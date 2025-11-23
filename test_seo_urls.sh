#!/bin/bash

# Test script to verify all SEO URLs are working
# Run with: bash test_seo_urls.sh

BASE_URL="http://localhost:8000"

echo "================================================================================"
echo "SEO URL Testing - Skaters.com"
echo "================================================================================"
echo ""
echo "Base URL: $BASE_URL"
echo ""
echo "⚠️  Make sure the server is running: uvicorn app.main:app --reload"
echo ""

# Function to test a URL
test_url() {
    local url=$1
    local response=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL$url" 2>/dev/null)
    
    if [ "$response" = "200" ]; then
        echo "✅ OK           $url"
        return 0
    elif [ "$response" = "404" ]; then
        echo "❌ NOT FOUND   $url"
        return 1
    elif [ "$response" = "500" ]; then
        echo "❌ ERROR 500   $url"
        return 1
    elif [ -z "$response" ]; then
        echo "❌ NO RESPONSE $url (Is server running?)"
        return 1
    else
        echo "⚠️  $response       $url"
        return 1
    fi
}

# Test counters
total=0
success=0
failed=0

echo "================================================================================"
echo "Homepage & Core Pages"
echo "================================================================================"
test_url "/" && ((success++)) || ((failed++))
((total++))

echo ""
echo "================================================================================"
echo "Hub Pages"
echo "================================================================================"
test_url "/ice-rinks" && ((success++)) || ((failed++))
((total++))

echo ""
echo "================================================================================"
echo "Near Me Pages"
echo "================================================================================"
urls=(
    "/near-me"
    "/skate-parks/near-me"
    "/ice-rinks/near-me"
    "/roller-rinks/near-me"
    "/indoor-skate-parks/near-me"
    "/outdoor-skate-parks/near-me"
    "/outdoor-ice-rinks/near-me"
    "/indoor-ice-rinks/near-me"
)
for url in "${urls[@]}"; do
    test_url "$url" && ((success++)) || ((failed++))
    ((total++))
done

echo ""
echo "================================================================================"
echo "Location Pages"
echo "================================================================================"
urls=(
    "/locations/states"
    "/locations/ca"
    "/locations/ny"
    "/locations/tx"
    "/locations/ca/los-angeles"
    "/locations/ny/new-york"
    "/locations/tx/houston"
)
for url in "${urls[@]}"; do
    test_url "$url" && ((success++)) || ((failed++))
    ((total++))
done

echo ""
echo "================================================================================"
echo "Sport-Specific City Pages"
echo "================================================================================"
urls=(
    "/skate-parks/ca/los-angeles"
    "/skate-parks/ny/new-york"
    "/ice-rinks/ny/new-york"
    "/ice-rinks/il/chicago"
    "/roller-rinks/nv/las-vegas"
    "/roller-rinks/ny/new-york"
)
for url in "${urls[@]}"; do
    test_url "$url" && ((success++)) || ((failed++))
    ((total++))
done

echo ""
echo "================================================================================"
echo "SEO Pages"
echo "================================================================================"
urls=(
    "/robots.txt"
    "/sitemap.xml"
)
for url in "${urls[@]}"; do
    test_url "$url" && ((success++)) || ((failed++))
    ((total++))
done

echo ""
echo "================================================================================"
echo "SUMMARY"
echo "================================================================================"
echo ""
echo "Total URLs Tested: $total"
echo "✅ Success (200):   $success ($(echo "scale=1; $success*100/$total" | bc)%)"
echo "❌ Failed:          $failed ($(echo "scale=1; $failed*100/$total" | bc)%)"
echo ""

if [ $failed -eq 0 ]; then
    echo "🎉 All URLs working perfectly!"
    exit 0
else
    echo "⚠️  Some URLs failed. Check the output above."
    exit 1
fi
