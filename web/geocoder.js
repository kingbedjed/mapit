/**
 * Geocoding utility using Nominatim (OpenStreetMap)
 * Automatically converts city names to lat/lon coordinates
 */

export class Geocoder {
    constructor() {
        this.baseUrl = 'https://nominatim.openstreetmap.org/search';
        this.contactEmail = 'tjjdoman@gmail.com';  // Nominatim identification
        this.cache = this.loadCache();
        this.requestQueue = [];
        this.isProcessing = false;
        this.minDelay = 1000; // 1 second between requests (Nominatim requirement)
    }

    /**
     * Load cached geocoding results from localStorage
     */
    loadCache() {
        try {
            const cached = localStorage.getItem('geocode_cache');
            return cached ? JSON.parse(cached) : {};
        } catch (e) {
            console.warn('Could not load geocode cache:', e);
            return {};
        }
    }

    /**
     * Save geocoding results to localStorage cache
     */
    saveCache() {
        try {
            localStorage.setItem('geocode_cache', JSON.stringify(this.cache));
        } catch (e) {
            console.warn('Could not save geocode cache:', e);
        }
    }

    /**
     * Generate cache key for a city/country pair
     */
    getCacheKey(city, country) {
        return `${city.toLowerCase()},${country.toLowerCase()}`;
    }

    /**
     * Geocode a single city
     */
    async geocode(city, country) {
        const cacheKey = this.getCacheKey(city, country);

        // Check cache first
        if (this.cache[cacheKey]) {
            console.log(`✓ Using cached coordinates for ${city}, ${country}`);
            return this.cache[cacheKey];
        }

        // Build query. Nominatim's usage policy asks browser apps to identify
        // themselves; browsers forbid setting User-Agent, so we pass the
        // sanctioned `email` param instead (and let the Referer header identify
        // the origin). Keep volume low + cached per the policy.
        const query = `${city}, ${country}`;
        const url = `${this.baseUrl}?q=${encodeURIComponent(query)}`
            + `&format=json&limit=1&email=${encodeURIComponent(this.contactEmail)}`;

        try {
            console.log(`→ Geocoding ${query}...`);
            const response = await fetch(url);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const data = await response.json();

            if (data && data.length > 0) {
                const result = {
                    latitude: parseFloat(data[0].lat),
                    longitude: parseFloat(data[0].lon)
                };

                // Cache the result
                this.cache[cacheKey] = result;
                this.saveCache();

                console.log(`  ✓ Found: ${result.latitude.toFixed(2)}, ${result.longitude.toFixed(2)}`);
                return result;
            } else {
                console.warn(`  ✗ No results for ${query}`);
                return null;
            }
        } catch (error) {
            console.error(`  ✗ Error geocoding ${query}:`, error);
            return null;
        }
    }

    /**
     * Geocode multiple cities with rate limiting
     */
    async geocodeBatch(cities, onProgress = null) {
        const results = [];
        const total = cities.length;

        for (let i = 0; i < cities.length; i++) {
            const city = cities[i];

            // Skip if already has coordinates
            if (city.latitude !== undefined && city.longitude !== undefined) {
                results.push(city);
                if (onProgress) onProgress(i + 1, total, city.city, true);
                continue;
            }

            // Geocode
            const coords = await this.geocode(city.city, city.country);

            if (coords) {
                results.push({
                    ...city,
                    latitude: coords.latitude,
                    longitude: coords.longitude
                });
            } else {
                // Use default coordinates (0, 0) if geocoding fails
                console.warn(`Warning: Could not geocode ${city.city}, using default coordinates`);
                results.push({
                    ...city,
                    latitude: 0,
                    longitude: 0
                });
            }

            if (onProgress) onProgress(i + 1, total, city.city, !!coords);

            // Rate limiting: wait before next request
            if (i < cities.length - 1) {
                await this.sleep(this.minDelay);
            }
        }

        return results;
    }

    /**
     * Sleep utility for rate limiting
     */
    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    /**
     * Clear the geocoding cache
     */
    clearCache() {
        this.cache = {};
        localStorage.removeItem('geocode_cache');
        console.log('Geocoding cache cleared');
    }

    /**
     * Get cache statistics
     */
    getCacheStats() {
        const count = Object.keys(this.cache).length;
        return {
            count,
            cities: Object.keys(this.cache)
        };
    }
}
