
import time
import requests
import gpxpy
import polyline
import json
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from geopy.distance import geodesic

# Constants
GEOCODE_FIELDS_PRIORITY = ["road", "park", "neighbourhood", "suburb"]
SAMPLE_DISTANCE_METERS = 800
CACHE_FILE = "landmarks_cache.json"

# Load or initialize cache
try:
    with open(CACHE_FILE, "r") as f:
        cache = json.load(f)
except FileNotFoundError:
    cache = {}

def save_cache():
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)

def fetch_route_coords_from_strava(route_url, access_token):
    try:
        route_id = route_url.strip("/").split("/")[-1]
        print(f"🔍 Fetching route ID: {route_id}")
        api_url = f"https://www.strava.com/api/v3/routes/{route_id}"
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(api_url, headers=headers)
        print(f"🔁 Strava API status: {response.status_code}")
        if response.status_code != 200:
            print(f"❌ Error response: {response.text}")
        response.raise_for_status()
        data = response.json()
        polyline_str = data.get("map", {}).get("polyline")
        if not polyline_str:
            print("⚠️ No polyline found in route data.")
            return [], route_id
        coords = polyline.decode(polyline_str)
        print(f"✅ Retrieved {len(coords)} coordinates.")
        return coords, route_id
    except Exception as e:
        print(f"❌ Failed to fetch route: {e}")
        return [], None

def sample_coords(coords, sample_distance_m=SAMPLE_DISTANCE_METERS):
    if not coords:
        return []
    sampled = [coords[0]]
    last = coords[0]
    accum_dist = 0
    for point in coords[1:]:
        dist = geodesic(last, point).meters
        accum_dist += dist
        if accum_dist >= sample_distance_m:
            sampled.append(point)
            last = point
            accum_dist = 0
    return sampled

def reverse_geocode_points(coords):
    geolocator = Nominatim(user_agent="run_group_app")
    geocode = RateLimiter(geolocator.reverse, min_delay_seconds=1)
    pois = set()
    for lat, lon in coords:
        try:
            location = geocode((lat, lon), exactly_one=True, timeout=10)
            if location and "address" in location.raw:
                for key in GEOCODE_FIELDS_PRIORITY:
                    val = location.raw["address"].get(key)
                    if val:
                        pois.add(val)
                        break
        except Exception as e:
            print(f"⚠️ Geocode error at ({lat}, {lon}): {e}")
            continue
    return list(pois)

def generate_route_summary(route_url, access_token):
    coords, route_id = fetch_route_coords_from_strava(route_url, access_token)
    if not coords or not route_id:
        return "📍 Could not load route data."
    if route_id in cache:
        print(f"📦 Loaded POIs from cache for route {route_id}")
        pois = cache[route_id]
    else:
        sampled = sample_coords(coords)
        pois = reverse_geocode_points(sampled)
        cache[route_id] = pois
        save_cache()
    if pois:
        return "🏞️ This route passes " + ", ".join(pois[:5]) + "."
    else:
        return "🏞️ This route explores some scenic areas."
