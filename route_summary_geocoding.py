
import time
import requests
import gpxpy
import polyline
import json
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from geopy.distance import geodesic
import pandas as pd
from datetime import datetime, timedelta

GEOCODE_FIELDS_PRIORITY = ["park", "leisure", "natural", "landuse", "road"]
SAMPLE_DISTANCE_METERS = 800
CACHE_FILE = "landmarks_cache.json"

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

def extract_poi_from_location(location):
    if not location or "address" not in location.raw:
        return None

    address = location.raw.get("address", {})
    namedetails = location.raw.get("namedetails", {})
    poi_name = None

    # 1. Prioritise leisure/park/green space
    if location.raw.get("class") in ["leisure", "landuse", "natural"] and "name" in location.raw:
        poi_name = location.raw["name"]

    # 2. Namedetails fallback
    elif "name" in namedetails:
        poi_name = namedetails["name"]

    # 3. Prioritised fields in address
    else:
        for key in GEOCODE_FIELDS_PRIORITY:
            if key in address:
                poi_name = address[key]
                break

    return poi_name

def reverse_geocode_points(coords):
    geolocator = Nominatim(user_agent="run_group_app")
    geocode = RateLimiter(geolocator.reverse, min_delay_seconds=1)
    pois = []
    seen = set()
    for lat, lon in coords:
        try:
            location = geocode((lat, lon), exactly_one=True, timeout=10)
            name = extract_poi_from_location(location)
            if name and name not in seen:
                pois.append(name)
                seen.add(name)
        except Exception as e:
            print(f"⚠️ Geocode error at ({lat}, {lon}): {e}")
            continue
    return pois

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

def extract_route_links_from_schedule(schedule_path, days_ahead=30):
    df = pd.read_excel(schedule_path)
    today = datetime.today()
    end_date = today + timedelta(days=days_ahead)

    route_links = set()
    for _, row in df.iterrows():
        try:
            route_date = pd.to_datetime(row.get("Date"))
            if today <= route_date <= end_date:
                link_5k = str(row.get("Link_5k", "")).strip()
                link_8k = str(row.get("Link_8k", "")).strip()
                if link_5k.startswith("http"):
                    route_links.add(link_5k)
                if link_8k.startswith("http"):
                    route_links.add(link_8k)
        except Exception as e:
            print(f"⚠️ Error reading row: {e}")
            continue
    return list(route_links)

def preload_route_summaries(schedule_path, access_token, days_ahead=30):
    upcoming_links = extract_route_links_from_schedule(schedule_path, days_ahead)
    print(f"🗂️ Preloading {len(upcoming_links)} routes from the next {days_ahead} days.")
    for link in upcoming_links:
        coords, route_id = fetch_route_coords_from_strava(link, access_token)
        if coords and route_id and route_id not in cache:
            sampled = sample_coords(coords)
            pois = reverse_geocode_points(sampled)
            cache[route_id] = pois
            save_cache()
            print(f"✅ Cached POIs for route {route_id}")
        else:
            print(f"ℹ️ Route {route_id} already cached or unavailable.")


import requests

def query_overpass_parks(lat, lon, radius=100):
    query = f"""
    [out:json][timeout:10];
    (
      way["leisure"="park"](around:{radius},{lat},{lon});
      relation["leisure"="park"](around:{radius},{lat},{lon});
    );
    out tags center;
    """
    try:
        response = requests.post("https://overpass-api.de/api/interpreter", data={"data": query})
        response.raise_for_status()
        data = response.json()
        names = set()
        for element in data.get("elements", []):
            tags = element.get("tags", {})
            name = tags.get("name")
            if name:
                names.add(name)
        return list(names)
    except Exception as e:
        print(f"❌ Overpass API error at ({lat}, {lon}): {e}")
        return []

def reverse_geocode_points(coords):
    geolocator = Nominatim(user_agent="run_group_app")
    geocode = RateLimiter(geolocator.reverse, min_delay_seconds=1)
    pois = []
    seen = set()
    for lat, lon in coords:
        # Check for park using Overpass first
        parks = query_overpass_parks(lat, lon)
        for park in parks:
            if park not in seen:
                pois.append(park)
                seen.add(park)

        try:
            location = geocode((lat, lon), exactly_one=True, timeout=10)
            name = extract_poi_from_location(location)
            if name and name not in seen:
                pois.append(name)
                seen.add(name)
        except Exception as e:
            print(f"⚠️ Geocode error at ({lat}, {lon}): {e}")
            continue
    return pois


def query_overpass_parks(lat, lon, radius=50):
    query = f"""
    [out:json][timeout:10];
    (
      way["leisure"="park"](around:{radius},{lat},{lon});
      relation["leisure"="park"](around:{radius},{lat},{lon});
    );
    out tags center;
    """
    try:
        response = requests.post("https://overpass-api.de/api/interpreter", data={"data": query})
        response.raise_for_status()
        data = response.json()
        names = set()
        for element in data.get("elements", []):
            tags = element.get("tags", {})
            name = tags.get("name")
            if name:
                names.add(name)
        return list(names)
    except Exception as e:
        print(f"❌ Overpass API error at ({lat}, {lon}): {e}")
        return []

def reverse_geocode_points(coords):
    geolocator = Nominatim(user_agent="run_group_app")
    geocode = RateLimiter(geolocator.reverse, min_delay_seconds=1)

    park_hits = {}
    seen = set()
    pois = []

    for lat, lon in coords:
        park_names = query_overpass_parks(lat, lon)
        for name in park_names:
            park_hits[name] = park_hits.get(name, 0) + 1

    # Filter to parks seen in at least 2 locations
    confirmed_parks = {name for name, count in park_hits.items() if count >= 2}
    pois.extend(confirmed_parks)
    seen.update(confirmed_parks)

    for lat, lon in coords:
        try:
            location = geocode((lat, lon), exactly_one=True, timeout=10)

            # Suppress road names if park already included
            if any(p in seen for p in query_overpass_parks(lat, lon)):
                continue

            name = extract_poi_from_location(location)
            if name and name not in seen:
                pois.append(name)
                seen.add(name)
        except Exception as e:
            print(f"⚠️ Geocode error at ({lat}, {lon}): {e}")
            continue
    return pois

from geopy.distance import geodesic

def calculate_distance_and_elevation(coords):
    total_distance_km = 0.0
    total_elevation_gain = 0.0
    previous = None
    previous_elev = None

    for point in coords:
        if len(point) == 3:  # with elevation
            lat, lon, elev = point
        else:
            lat, lon = point
            elev = 0

        if previous:
            total_distance_km += geodesic((previous[0], previous[1]), (lat, lon)).km
            if elev > previous_elev:
                total_elevation_gain += elev - previous_elev

        previous = (lat, lon)
        previous_elev = elev

    return round(total_distance_km, 1), round(total_elevation_gain)

# Modify generate_route_summary to include it
original_generate = generate_route_summary

def generate_route_summary(route_url, access_token):
    coords, route_id = fetch_route_coords_from_strava(route_url, access_token)
    if not coords or not route_id:
        return "📍 Could not load route data."

    try:
        # Distance and elevation
        dist_km, elev_m = calculate_distance_and_elevation([(lat, lon) for lat, lon in coords])
        dist_summary = f"{dist_km} km with {elev_m}m of elevation"

        if route_id in cache:
            pois = cache[route_id]
        else:
            sampled = sample_coords(coords)
            pois = reverse_geocode_points(sampled)
            cache[route_id] = pois
            save_cache()

        if pois:
            return f"{dist_summary} – a few hills this week! 🔺\n🏞️ This route passes " + ", ".join(pois[:5]) + "."
        else:
            return f"{dist_summary} – a few hills this week! 🔺\n🏞️ This route explores some scenic areas."
    except Exception as e:
        print(f"Error generating route summary: {e}")
        return "🏞️ Route summary unavailable."

def get_elevation_comment(elev_m):
    if elev_m <= 20:
        return "flat as a pancake 🥞"
    elif elev_m <= 50:
        return "gently undulating 🌿"
    elif elev_m <= 100:
        return "a few hills this week! 🔺"
    else:
        return "hilly route – legs ready? ⛰️"

def generate_route_summary(route_url, access_token):
    coords, route_id = fetch_route_coords_from_strava(route_url, access_token)
    if not coords or not route_id:
        return "📍 Could not load route data."

    try:
        # Distance and elevation
        dist_km, elev_m = calculate_distance_and_elevation([(lat, lon) for lat, lon in coords])
        elevation_msg = get_elevation_comment(elev_m)
        dist_summary = f"{dist_km} km with {elev_m}m of elevation – {elevation_msg}"

        if route_id in cache:
            pois = cache[route_id]
        else:
            sampled = sample_coords(coords)
            pois = reverse_geocode_points(sampled)
            cache[route_id] = pois
            save_cache()

        if pois:
            return f"{dist_summary}\n🏞️ This route passes " + ", ".join(pois[:5]) + "."
        else:
            return f"{dist_summary}\n🏞️ This route explores some scenic areas."
    except Exception as e:
        print(f"Error generating route summary: {e}")
        return "🏞️ Route summary unavailable."
