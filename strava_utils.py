
import requests
import time
import gpxpy

def refresh_strava_token(client_id, client_secret, refresh_token):
    response = requests.post(
        "https://www.strava.com/oauth/token",
        data={
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        },
    )
    if response.status_code == 200:
        return response.json().get("access_token")
    return None

def extract_route_id(url):
    return url.rstrip("/").split("/")[-1]

def fetch_route_description(route_url, access_token):
    route_id = extract_route_id(route_url)
    api_url = f"https://www.strava.com/api/v3/routes/{route_id}"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        distance_km = round(data.get("distance", 0) / 1000, 1)
        elevation_gain = int(data.get("elevation_gain", 0))

        if elevation_gain < 20:
            comment = "a flat and fast route 🟢"
        elif elevation_gain < 60:
            comment = "a gently rolling route 🌿"
        else:
            comment = "a few hills this week! ⛰️"

        return f"{distance_km} km with {elevation_gain}m of elevation – {comment}"
    else:
        return "(⚠️ Could not fetch route details)"

def fetch_gpx_file(route_url, access_token):
    route_id = extract_route_id(route_url)
    gpx_url = f"https://www.strava.com/api/v3/routes/{route_id}/export_gpx"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(gpx_url, headers=headers)

    if response.status_code == 200:
        return response.content
    return None

def extract_gps_points_from_gpx(gpx_bytes, max_points=5):
    try:
        gpx = gpxpy.parse(gpx_bytes.decode('utf-8'))
        points = []
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    points.append((point.latitude, point.longitude))
        return points[:max_points]
    except Exception:
        return []

def reverse_geocode(lat, lon):
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=16&addressdetails=1"
        headers = {"User-Agent": "RunTogetherApp/1.0"}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            address = data.get("address", {})
            return address.get("road") or address.get("suburb") or address.get("town") or "Unknown area"
        else:
            return "Geocoding failed"
    except Exception:
        return "Geocoding error"

def extract_landmarks_from_gpx(gpx_bytes, access_token, num_points=4):
    try:
        gpx = gpxpy.parse(gpx_bytes.decode('utf-8'))
        all_points = []
        for track in gpx.tracks:
            for segment in track.segments:
                all_points.extend(segment.points)

        if not all_points:
            return ""

        step = max(len(all_points) // num_points, 1)
        sampled_points = all_points[::step][:num_points]

        seen = set()
        landmarks = []
        for pt in sampled_points:
            name = reverse_geocode(pt.latitude, pt.longitude)
            if name and name not in seen:
                seen.add(name)
                landmarks.append(name)
                time.sleep(1.1)

        if landmarks:
            return "Expect views through: " + ", ".join(landmarks) + "."
        return ""
    except Exception:
        return ""
