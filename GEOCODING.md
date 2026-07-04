# Auto-Geocoding Guide

This guide shows you how to add cities **without** manually looking up coordinates. The geocoding system automatically converts city/country names to latitude/longitude.

## Quick Start

The main `index.html` includes auto-geocoding:

```bash
cd web/
python -m http.server 8000
# Open http://localhost:8000/index.html
# Upload CSV with just city/country - coordinates added automatically!
```

## How It Works

### 1. Upload CSV Without Coordinates

Create a simple CSV with just city and country:

```csv
city,country,category,description
Paris,France,major_hub,City of lights
Dubai,UAE,tech_center,Innovation center
```

No latitude/longitude columns needed!

### 2. Auto-Geocoding

When you upload, the `Geocoder` class automatically:
- ✅ Fetches coordinates from OpenStreetMap (Nominatim)
- ✅ Caches results in browser localStorage
- ✅ Rate-limits requests (1 per second)
- ✅ Shows progress during loading

### 3. Display on Globe

Cities appear on the globe at their correct geographic positions automatically!

## Geocoding Services

### Option 1: Nominatim (Free, No API Key)

**Used by default** - OpenStreetMap's free geocoding service

**Pros:**
- ✅ Free, no API key required
- ✅ No usage limits for reasonable use
- ✅ Good global coverage

**Cons:**
- ⚠️ Must rate-limit to 1 request/second
- ⚠️ Slower for large batches

**Usage Policy:** https://operations.osmfoundation.org/policies/nominatim/

### Option 2: Mapbox Geocoding API

**API Key Required** (free tier: 100,000 requests/month)

```javascript
// In geocoder.js, change baseUrl to:
this.baseUrl = 'https://api.mapbox.com/geocoding/v5/mapbox.places';
this.accessToken = 'YOUR_MAPBOX_TOKEN';

// Update geocode() method:
const url = `${this.baseUrl}/${encodeURIComponent(query)}.json?access_token=${this.accessToken}`;
```

**Get API key:** https://account.mapbox.com/

**Pros:**
- ✅ Much faster (no rate limiting)
- ✅ More accurate results
- ✅ Better address parsing

### Option 3: Google Maps Geocoding

**API Key Required** (paid service, free $200 credit/month)

```javascript
this.baseUrl = 'https://maps.googleapis.com/maps/api/geocode/json';
this.apiKey = 'YOUR_GOOGLE_API_KEY';

const url = `${this.baseUrl}?address=${encodeURIComponent(query)}&key=${this.apiKey}`;
```

**Get API key:** https://console.cloud.google.com/

**Pros:**
- ✅ Highest accuracy
- ✅ Best global coverage
- ✅ No rate limits on paid tier

**Cons:**
- ❌ Requires payment info (even for free tier)

### Option 4: OpenCage Geocoder

**API Key Required** (free tier: 2,500 requests/day)

```javascript
this.baseUrl = 'https://api.opencagedata.com/geocode/v1/json';
this.apiKey = 'YOUR_OPENCAGE_KEY';

const url = `${this.baseUrl}?q=${encodeURIComponent(query)}&key=${this.apiKey}`;
```

**Get API key:** https://opencagedata.com/

**Pros:**
- ✅ Good free tier
- ✅ Fast
- ✅ Simple API

## Browser Caching

Results are automatically cached in browser localStorage:

**How it works:**
- First time you upload a city → geocoded and cached
- Upload same city again → instant (from cache)
- Works across browser sessions
- No expiration (persists until cleared)

**Check cache:**
Open browser console (F12) and type:
```javascript
localStorage.getItem('geocode_cache')
```

**Clear cache if needed:**
```javascript
localStorage.removeItem('geocode_cache')
```

**Benefits:**
- Only geocode each city once
- Instant loading on subsequent uploads
- Reduces API requests

## Mixing Formats

You can mix cities with and without coordinates in your CSV:

```csv
city,country,category,latitude,longitude
New York,USA,major_hub,40.7128,-74.0060
Paris,France,major_hub,,
London,UK,tech_center,,
```

The geocoder automatically skips cities that already have coordinates (New York) and only geocodes the ones that don't (Paris, London).

## Loading Progress

The app automatically shows progress during geocoding:

- **Loading panel** displays current city being geocoded
- **Progress counter** shows "X / Y cities"
- **Success/fail icons** (✓ or ✗) for each city
- **Status updates** in real-time

No configuration needed - it's built into the upload interface!

## Error Handling

If geocoding fails for a city:
- Console warning is logged
- City is skipped (won't appear on globe)
- Other cities continue processing

**Check browser console (F12)** to see which cities failed and why.

## Best Practices

### 1. Save Geocoded Results

After uploading your CSV once:
1. Open browser console (F12)
2. Check localStorage cache: `localStorage.getItem('geocode_cache')`
3. Copy cached coordinates
4. Add them to your CSV for faster future loads

Example - add latitude/longitude columns after first geocode:
```csv
city,country,category,latitude,longitude
Mumbai,India,major_hub,19.076,72.8777
Cairo,Egypt,tech_center,30.0444,31.2357
```

### 2. Respect Rate Limits

The app automatically handles Nominatim's 1 req/second limit:
- First upload: Slow (1 city per second)
- Subsequent uploads: Instant (cached)
- Different cities: Geocoded as needed

No action needed - it's built-in!

### 3. Handle Ambiguous Names

Be specific with country names in your CSV:

```csv
city,country
Paris,France
Paris,Texas USA

# Avoid ambiguous names:
Springfield,USA    # Which Springfield? (there are many!)
```

Use more specific locations when needed:
```csv
city,country
Springfield,Illinois USA
Springfield,Massachusetts USA
```

## Complete Example

### Step 1: Create Your CSV

Create `my_cities.csv`:

```csv
city,country,category,description
Mumbai,India,major_hub,Financial center
Cairo,Egypt,tech_center,Innovation hub
Lagos,Nigeria,startup_hub,Emerging market
```

### Step 2: Upload to Map

1. Open http://localhost:8000/index.html
2. Drag and drop `my_cities.csv` onto the upload area
3. Watch as cities are geocoded one by one (progress shown)
4. Cities appear on the globe with correct coordinates!

The geocoding happens automatically in the browser - no backend needed!

## Comparison Table

| Service | Free Tier | Rate Limit | API Key | Accuracy |
|---------|-----------|------------|---------|----------|
| **Nominatim** | Unlimited | 1/sec | No | Good |
| **Mapbox** | 100k/mo | None | Yes | Excellent |
| **Google** | $200 credit | None* | Yes | Best |
| **OpenCage** | 2.5k/day | 1/sec | Yes | Good |

\* Google has rate limits on free tier

## Troubleshooting

**Cities not appearing:**
- Check browser console for errors
- Verify city/country spelling
- Try more specific location (e.g., "Paris, France" not just "Paris")

**Slow loading:**
- Nominatim rate-limits to 1/second
- Consider using Mapbox or Google for faster results
- Or pre-geocode and save results

**Blocked by API:**
- Nominatim blocks if you exceed 1 request/second
- Clear cache and retry: `geocoder.clearCache()`
- Wait a few minutes before retrying

**Incorrect coordinates:**
- Be specific with country/region in CSV
- Manually override coordinates if needed:
  ```csv
  city,country,latitude,longitude
  Springfield,Illinois USA,39.78,-89.65
  ```

---

**Summary:** Auto-geocoding makes it easy to add cities without manually looking up coordinates. Use Nominatim for free/simple projects, or upgrade to Mapbox/Google for production applications.
