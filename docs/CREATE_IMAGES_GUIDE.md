# Image Assets Creation Guide

## Quick Solution: Use Online Tools

### 1. Favicon (5 minutes)

**Use:** https://realfavicongenerator.net/

**Steps:**
1. Create a simple 512x512 image with:
   - Blue background (#2563EB)
   - White letter "S" in center
   - Or use a skate icon

2. Upload to RealFaviconGenerator
3. Download the generated package
4. Extract files to `/app/static/`:
   - favicon.ico
   - favicon-16x16.png
   - favicon-32x32.png
   - apple-touch-icon.png

**Already done:** Favicon links are in base.html

---

### 2. OG Image (10 minutes)

**Use:** https://www.canva.com/ (free)

**Template:** 1200x630px

**Design:**
```
+------------------------------------------+
|                                          |
|     SKATERS.COM                          |
|     Find Your Perfect Skating Venue      |
|                                          |
|     [Skate icon or emoji]                |
|                                          |
|     🛹 Skate Parks                       |
|     ⛸️  Ice Rinks                        |
|     🛼 Roller Rinks                      |
|                                          |
+------------------------------------------+
```

**Colors:**
- Background: Gradient blue to purple (#2563EB to #7C3AED)
- Text: White
- Font: Bold, modern

**Save as:** `/app/static/images/og-default.jpg`

**Already done:** OG meta tags are in base.html

---

## Alternative: Simple SVG (Already Created!)

A simple SVG favicon has been created at:
`/app/static/favicon.svg`

This works in modern browsers but you should still create the ICO and PNG versions for full compatibility.

---

## Status

✅ Favicon SVG created
✅ Favicon links added to base.html
✅ OG meta tags added to base.html
⏳ Need to create actual image files (15 min with online tools)

The site will work without these files, but browsers will show default icons and social shares won't have images.
