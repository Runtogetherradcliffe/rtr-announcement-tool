import requests
import polyline
import math

# Constants
GEOCODE_FIELDS_PRIORITY = ["road", "park", "neighbourhood", "suburb"]
SAMPLE_DISTANCE_METERS = 300
LOCATIONIQ_API_KEY = "pk.c820b7e76f37159a448acc812ceefee1"
MAX_PARK_DISTANCE_METERS = 50

# Cache structure (in memory or replace with persistent storage)
cache = {}

def query_parks_in_bbox(coords):
    if not coords:
        return []

    lats = [lat for lat, _ in coords]
    lons = [lon for _, lon in coords]
    min_lat, max_lat = min(lats), max(lats)
    min_lon, max_lon = min(lons), max(lons)

    query = f"""
    [out:json][timeout:25];
    (
      way["leisure"="park"]({min_lat},{min_lon},{max_lat},{max_lon});
      relation["leisure"="park"]({min_lat},{min_lon},{max_lat},{max_lon});
    );
    out tags center;
    """

    try:
        response = requests.post("https://overpass-api.de/api/interpreter", data={"data": query})
        response.raise_for_status()
        data = response.json()
        parks = []
        for element in data.get("elements", []):
            tags = element.get("tags", {})
            name = tags.get("name")
            center = element.get("center")
            if name and center:
                parks.append((name, (center["lat"], center["lon"])))
        return parks
    except Exception as e:
        print(f"❌ Overpass API (bbox) error: {e}")
        return []

def locationiq_reverse_geocode(lat, lon):
    try:
        url = f"https://us1.locationiq.com/v1/reverse?key={LOCATIONIQ_API_KEY}&lat={lat}&lon={lon}&format=json"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        address = data.get("address", {})
        display_name = data.get("display_name", "")
        for field in GEOCODE_FIELDS_PRIORITY:
            if field in address:
                return address[field]
        if "," in display_name:
            return display_name.split(",")[0]
        return None
    except Exception as e:
        print(f"⚠️ LocationIQ geocode error at ({lat}, {lon}): {e}")
        return None

def haversine(coord1, coord2):
    R = 6371000  # radius of Earth in meters
    lat1, lon1 = map(math.radians, coord1)
    lat2, lon2 = map(math.radians, coord2)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def sample_coords(coords, sample_distance_m=SAMPLE_DISTANCE_METERS):
    sampled = []
    if not coords:
        return sampled
    last = coords[0]
    sampled.append(last)
    accum_dist = 0
    for point in coords[1:]:
        dist = haversine(last, point)
        accum_dist += dist
        if accum_dist >= sample_distance_m:
            sampled.append(point)
            last = point
            accum_dist = 0
    return sampled

def reverse_geocode_points(coords):
    sampled = sample_coords(coords)
    nearby_parks = query_parks_in_bbox(sampled)

    # Only keep parks that are within MAX_PARK_DISTANCE_METERS from any sampled point
    filtered_parks = []
    for name, park_coord in nearby_parks:
        if any(haversine(park_coord, pt) <= MAX_PARK_DISTANCE_METERS for pt in sampled):
            filtered_parks.append(name)

    seen = set(filtered_parks)
    pois = list(filtered_parks)

    # Limit LocationIQ lookups to 3 to avoid API overload
    locationiq_lookups = 0
    for lat, lon in sampled:
        if locationiq_lookups >= 3:
            break
        name = locationiq_reverse_geocode(lat, lon)
        if name and name not in seen:
            pois.append(name)
            seen.add(name)
            locationiq_lookups += 1

    return pois

def get_elevation_comment(elev_m):
    if elev_m <= 20:
        return "flat as a pancake 🥞"
    elif elev_m <= 50:
        return "gently undulating 🌿"
    elif elev_m <= 100:
        return "a few hills this week! 🔺"
    else:
        return "hilly route – legs ready? ⛰️"

def save_cache():
    pass  # Placeholder for future caching to disk

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
            return [], route_id, 0, 0
        coords = polyline.decode(polyline_str)
         elev_gain = round(data.get("elevation_gain", 0))
         distance_km = round(data.get("distance", 0) / 1000, 1)
         print(f"✅ Retrieved {len(coords)} coords, {distance_km} km, {elev_gain}m elevation.")
         return coords, route_id, elev_gain, distance_km
     except Exception as e:
         print(f"❌ Failed to fetch route: {e}")
         return [], None, 0, 0
 
 def generate_route_summary(route_url, access_token):
     coords, route_id, elev_m, dist_km = fetch_route_coords_from_strava(route_url, access_token)
     if not coords or not route_id:
         return "📍 Could not load route data."
 
     try:
         elevation_msg = get_elevation_comment(elev_m)
         dist_summary = f"{dist_km} km with {elev_m}m of elevation – {elevation_msg}"
 
         if route_id in cache:
             pois = cache[route_id]
         else:
             pois = reverse_geocode_points(coords)
             cache[route_id] = pois
             save_cache()
 
         if pois:
-            return f"{dist_summary}
-🏞️ This route passes " + ", ".join(pois[:5]) + "."
+            return (
+                f"{dist_summary}\n"
+                "🏞️ This route passes " + ", ".join(pois[:5]) + "."
+            )
         else:
-            return f"{dist_summary}
-🏞️ This route explores some scenic areas."
+            return (
+                f"{dist_summary}\n"
+                "🏞️ This route explores some scenic areas."
+            )
     except Exception as e:
         print(f"Error generating route summary: {e}")
         return "🏞️ Route summary unavailable."
