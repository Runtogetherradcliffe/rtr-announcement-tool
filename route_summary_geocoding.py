
import requests
import gpxpy
import time
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from io import StringIO

def fetch_gpx_from_strava(route_url: str) -> str:
    """
    Attempts to fetch GPX file from a public Strava route page.
    """
    try:
        route_id = route_url.strip("/").split("/")[-1]
        gpx_export_url = f"https://www.strava.com/routes/{route_id}/gpx"
        response = requests.get(gpx_export_url)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"❌ Failed to fetch GPX: {e}")
        return None

def parse_gpx_points(gpx_data: str, spacing_m: int = 300) -> list:
    """
    Parses GPX data and returns lat/lon points spaced approximately every `spacing_m` meters.
    """
    try:
        gpx = gpxpy.parse(gpx_data)
        points = []
        total_distance = 0
        last_point = None

        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    if last_point is None:
                        points.append((point.latitude, point.longitude))
                        last_point = point
                    else:
                        dist = point.distance_2d(last_point)
                        total_distance += dist
                        if total_distance >= spacing_m:
                            points.append((point.latitude, point.longitude))
                            total_distance = 0
                            last_point = point
        return points
    except Exception as e:
        print(f"❌ Failed to parse GPX: {e}")
        return []

def reverse_geocode_points(points: list, max_pois: int = 5) -> list:
    """
    Reverse geocodes lat/lon points to place/road names using OpenStreetMap.
    """
    geolocator = Nominatim(user_agent="rtr-geocoder")
    geocode = RateLimiter(geolocator.reverse, min_delay_seconds=1)

    seen = set()
    pois = []

    for lat, lon in points:
        try:
            location = geocode((lat, lon), exactly_one=True, language='en')
            if not location:
                continue

            data = location.raw.get('address', {})
            for key in ['road', 'neighbourhood', 'suburb', 'park']:
                value = data.get(key)
                if value and value not in seen:
                    pois.append(value)
                    seen.add(value)
                    break

            if len(pois) >= max_pois:
                break
        except Exception as e:
            print(f"⚠️ Geocode error: {e}")
            continue

    return pois

def generate_route_summary(strava_url: str) -> str:
    """
    Full pipeline: fetch route from Strava, parse and geocode to generate summary.
    """
    gpx_data = fetch_gpx_from_strava(strava_url)
    if not gpx_data:
        return "📍 Could not load route data."

    points = parse_gpx_points(gpx_data)
    if not points:
        return "📍 Route data could not be parsed."

    pois = reverse_geocode_points(points)
    if not pois:
        return "📍 Could not identify major points of interest."

    summary = "🏞️ This route passes " + ", ".join(pois[:-1]) + f", and {pois[-1]}." if len(pois) > 1 else f"🏞️ This route passes {pois[0]}."
    return summary
