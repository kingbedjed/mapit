# CSV Usage Guide

Load your city data from a simple CSV file - no coordinate lookup required!

## Quick Start

1. **Start server**: `cd web && python -m http.server 8000`
2. **Open browser**: http://localhost:8000/index.html
3. **Drag and drop** your CSV file or click "Use Sample Data"
4. Done! Cities are auto-geocoded and displayed on the 3D globe

## CSV Format

### Required Structure

```csv
city,country,[any other columns you want]
```

**Rules:**
- ✅ First column = City name
- ✅ Second column = Country name
- ✅ All other columns = Custom data (shown on hover)
- ✅ NO latitude/longitude needed!

### Example CSV

```csv
city,country,category,description,population,founded
New York,USA,Financial Hub,Major financial center,8.3M,1624
San Francisco,USA,Tech Center,Silicon Valley hub,875K,1776
London,UK,Financial Hub,European center,9.0M,47 AD
Tokyo,Japan,Tech Center,Innovation center,14.0M,1457
```

## Custom Columns

**All columns** after `city` and `country` are automatically:
- Displayed in hover tooltip
- Formatted with proper labels
- Shown in order they appear in CSV

### Examples of Custom Columns

```csv
city,country,industry,employees,revenue,year_established
```

```csv
city,country,lab_name,equipment_type,samples_processed,contact_email
```

```csv
city,country,partner_name,collaboration_type,projects,status
```

**Any columns work!** The system automatically displays them all.

## How It Works

### 1. Load CSV
```javascript
const CSV_URL = '../cities.csv';  // Path to your file
```

### 2. Auto-Parse Headers
System automatically detects:
- Column 1 = City
- Column 2 = Country
- Columns 3+ = Custom fields

### 3. Auto-Geocode
Cities are geocoded using OpenStreetMap (free):
```
New York, USA → 40.71°, -74.01°
London, UK → 51.51°, -0.13°
```

### 4. Display Everything
All custom columns shown in hover info:
```
City: New York
Country: USA
Category: Financial Hub
Description: Major financial center
Population: 8.3M
Founded: 1624
Coordinates: 40.71°, -74.01°
```

## Marker Colors

The system intelligently assigns colors based on data:

### Auto-Detection
If you have a `category` column, colors are assigned:
- Contains "financial" or "hub" → 🔴 Red
- Contains "tech" → 🔵 Cyan
- Contains "startup" → 🟡 Yellow

### No Category?
Colors cycle through a palette automatically.

### Custom Colors
Edit `getMarkerColor()` function in `index.html`:

```javascript
function getMarkerColor(cityData, index) {
    if (cityData.industry === 'Healthcare') return 0x4ECDC4;
    if (cityData.industry === 'Finance') return 0xFF6B6B;
    // ... your custom logic
}
```

## Marker Sizes

Based on `category` field:
- "financial" or "hub" → Largest (0.03)
- "tech" → Medium (0.025)
- Default → Small (0.02)

### Custom Sizes
Edit `getMarkerSize()` function:

```javascript
function getMarkerSize(cityData) {
    if (cityData.population && parseFloat(cityData.population) > 10) {
        return 0.04;  // Large cities
    }
    return 0.02;
}
```

## File Locations

### Default Setup
```
20251205_interactive_map/
└── web/
    ├── index.html       # Main app with drag-and-drop upload
    └── cities.csv       # Sample data file
```

### Using Your Own CSV
Two ways to load your data:

1. **Drag and Drop** (Easiest)
   - Open http://localhost:8000/index.html
   - Drag your CSV file onto the upload area
   - Or click "Choose CSV File" button

2. **Replace Sample File**
   - Replace `web/cities.csv` with your data
   - Click "Use Sample Data" button in the app

## Caching & Performance

### First Load
- Reads CSV file
- Geocodes each city (1 per second)
- Caches results in browser

### Subsequent Loads
- Reads CSV file
- Uses cached coordinates (instant!)
- Only geocodes new cities

### Clear Cache
Open browser console:
```javascript
localStorage.removeItem('geocode_cache');
```

## Troubleshooting

### Cities Not Appearing

**Problem**: Cities show at (0, 0)

**Solutions:**
1. Check city/country spelling
2. Be more specific: "Paris, France" not "Paris, Texas"
3. Check browser console for errors

### CSV Not Loading

**Problem**: "Failed to load CSV"

**Solutions:**
1. Use HTTP server (not `file://`)
   ```bash
   python -m http.server 8000
   ```
2. Check CSV path in `index_csv.html`
3. Verify CSV is valid (no empty rows)

### Columns Not Showing

**Problem**: Custom columns don't appear in hover

**Solutions:**
1. Check CSV has header row
2. Verify no empty values (use "N/A" instead)
3. Check browser console for parsing errors

### Slow Loading

**Problem**: Takes long to load

**Explanation**: Nominatim rate-limits to 1 request/second
- 10 cities = 10 seconds first load
- Subsequent loads = instant (cached)

**Solutions:**
1. Use pre-geocoded `cities_geocoded.csv`
2. Upgrade to Mapbox/Google (see GEOCODING.md)
3. Be patient on first load

## Advanced Usage

### Mix Geocoded & Non-Geocoded

CSV can have optional lat/lon columns:

```csv
city,country,category,latitude,longitude
New York,USA,Hub,40.71,-74.01
Paris,France,Hub,,
```

System will:
- Use provided coordinates if available
- Auto-geocode if missing

### Dynamic Data Loading

Load from API instead of file:

```javascript
async function loadCSV() {
    const response = await fetch('https://api.example.com/cities');
    const data = await response.json();

    // Convert to CSV format
    const csvText = convertJSONToCSV(data);
    return parseCSV(csvText);
}
```

### Custom Hover Layout

Edit `showCityInfo()` function for custom formatting:

```javascript
function showCityInfo(city) {
    // Custom HTML
    detailsDiv.innerHTML = `
        <div class="custom-layout">
            <p><strong>${city.category}</strong></p>
            <p>${city.description}</p>
            <div class="stats">
                <span>Pop: ${city.population}</span>
                <span>Founded: ${city.founded}</span>
            </div>
        </div>
    `;
}
```

## CSV Examples

### Research Labs
```csv
city,country,lab_name,research_focus,equipment,pi_name
Boston,USA,Smith Lab,Cell Biology,Vireo,Dr. Jane Smith
Cambridge,UK,Jones Lab,Neuroscience,Kestrel,Dr. Bob Jones
```

### Customer Locations
```csv
city,country,company,industry,install_date,units
Seattle,USA,TechCorp,Software,2024-01-15,3
Tokyo,Japan,BioInc,Biotech,2024-03-20,5
```

### Event Locations
```csv
city,country,event_name,date,attendees,type
San Francisco,USA,AI Conference,2024-06-15,500,Conference
Berlin,Germany,Startup Summit,2024-08-20,300,Summit
```

## Best Practices

### 1. Consistent Formatting
```csv
# Good
New York,USA,Tech Hub,...
London,UK,Financial,...

# Bad (inconsistent)
New York,United States,Tech Hub,...
London,Great Britain,Financial,...
```

### 2. Use Standard Country Names
```csv
# Good
USA, UK, France, Japan

# Avoid
United States of America, England, French Republic
```

### 3. Keep Descriptions Concise
```csv
# Good
description,Major financial center

# Too long (will overflow hover)
description,This is a major financial center with extensive history spanning...
```

### 4. Use Meaningful Column Names
```csv
# Good
city,country,category,employees,revenue

# Not helpful
city,country,col3,col4,col5
```

---

**Summary:** Just drag and drop your CSV file (no coordinates needed) at http://localhost:8000/index.html and watch your cities appear on the 3D globe automatically!
