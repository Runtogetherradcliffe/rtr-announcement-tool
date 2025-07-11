import time
import requests
import gpxpy
import polyline
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

# Constants
GEOCODE_FIELDS_PRIORITY = ["road", "park", "neighbourhood", "suburb"]
SAMPLE_DISTANCE_METERS = 300


def fetch_route_coords_from_strava(route_url, access_token):
    """
    Fetches route coordinates from Strava API using access token.
    """
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
            return []

        coords = polyline.decode(polyline_str)
        print(f"✅ Retrieved {len(coords)} coordinates from Strava route.")
        return coords
    except Exception as e:
        print(f"❌ Failed to fetch route from Strava API: {e}")
        return []


def sample_coords(coords, sample_distance_m=SAMPLE_DISTANCE_METERS):
    """
    Sample route coordinates every ~sample_distance_m.
    """
    sampled = []
    if not coords:
        return sampled

    last = coords[0]
    sampled.append(last)
    accum_dist = 0

    from geopy.distance import geodesic

    for point in coords[1:]:
        dist = geodesic(last, point).meters
        accum_dist += dist
        if accum_dist >= sample_distance_m:
            sampled.append(point)
            last = point
            accum_dist = 0

    return sampled


def reverse_geocode_points(coords):
    """
    Use OpenStreetMap's Nominatim to reverse geocode each coordinate.
    """
    geolocator = Nominatim(user_agent="run_group_app")
    geocode = RateLimiter(geolocator.reverse, min_delay_seconds=1)

    pois = set()
    for lat, lon in coords:
        try:
            location = geocode((lat, lon), exactly_one=True, timeout=10)
            if location and location.raw and "address" in location.raw:
                address = location.raw["address"]
                for key in GEOCODE_FIELDS_PRIORITY:
                    if key in address:
                        pois.add(address[key])
                        break
        except Exception as e:
            print(f"Geocoding error at ({lat}, {lon}): {e}")
            continue
    return list(pois)


def generate_route_summary(route_url, access_token):
    coords = fetch_route_coords_from_strava(route_url, access_token)
    if not coords:
        return "📍 Could not load route data."

    try:
        sampled = sample_coords(coords)
        pois = reverse_geocode_points(sampled)
        if pois:
            summary = "🏞️ This route passes " + ", ".join(pois[:5]) + "."
        else:
            summary = "🏞️ This route explores some scenic areas."
        return summary
    except Exception as e:
        print(f"Error generating route summary: {e}")
        return "🏞️ Route summary unavailable."
