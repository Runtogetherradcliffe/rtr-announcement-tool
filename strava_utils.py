import requests
import gpxpy
import os
import json
from io import StringIO

LANDMARKS_CACHE_PATH = "landmarks_cache.json"

def load_landmarks_cache():
    if not os.path.exists(LANDMARKS_CACHE_PATH):
        with open(LANDMARKS_CACHE_PATH, "w") as f:
            json.dump({}, f)
    with open(LANDMARKS_CACHE_PATH, "r") as f:
        return json.load(f)

def save_landmarks_cache(cache):
    with open(LANDMARKS_CACHE_PATH, "w") as f:
        json.dump(cache, f)

def refresh_strava_token(client_id, client_secret, refresh_token):
    response = requests.post(
        "https://www.strava.com/api/v3/oauth/token",
        data={
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        },
    )
    if response.ok:
        return response.json()["access_token"]
    return None

def download_gpx_from_strava_route(route_url, access_token):
    route_id = route_url.strip("/").split("/")[-1]
    headers = {"Authorization": f"Bearer {access_token}"}
    export_url = f"https://www.strava.com/api/v3/routes/{route_id}/export_gpx"
    response = requests.get(export_url, headers=headers)
    if response.ok:
        return response.text
    return None

def fetch_route_description(route_url, access_token):
    route_id = route_url.strip("/").split("/")[-1]
    headers = {"Authorization": f"Bearer {access_token}"}
    route_api = f"https://www.strava.com/api/v3/routes/{route_id}"
    response = requests.get(route_api, headers=headers)
    if response.ok:
        data = response.json()
        distance_km = round(data.get("distance", 0) / 1000, 1)
        elevation = round(data.get("elevation_gain", 0))
        if elevation < 20:
            difficulty = "flat as a pancake! 🟢"
        elif elevation < 50:
            difficulty = "a gently rolling route 🌿"
        else:
            difficulty = "a few hills this week! 🔺"

        description = f"{distance_km} km with {elevation}m of elevation – {difficulty}"

        cache = load_landmarks_cache()
        if route_id in cache:
            landmarks = cache[route_id]
        else:
            gpx = download_gpx_from_strava_route(route_url, access_token)
            landmarks = extract_landmarks_from_gpx(gpx)
            cache[route_id] = landmarks
            save_landmarks_cache(cache)

        if landmarks:
            description += f"\n🏞️ This route passes {', '.join(landmarks)}"

        return description
    return ""

def extract_landmarks_from_gpx(gpx_data, max_points=3):
    if not gpx_data:
        return []

    gpx = gpxpy.parse(StringIO(gpx_data))
    points = gpx.tracks[0].segments[0].points if gpx.tracks else []

    if not points:
        return []

    step = max(1, len(points) // max_points)
    sampled_points = points[::step][:max_points]

    landmarks = []
    for pt in sampled_points:
        try:
            nominatim_url = (
                f"https://nominatim.openstreetmap.org/reverse?format=json&lat={pt.latitude}&lon={pt.longitude}"
            )
            headers = {"User-Agent": "RunGroupApp/1.0"}
            res = requests.get(nominatim_url, headers=headers, timeout=5)
            data = res.json()
            if "display_name" in data:
                landmark = data["display_name"].split(",")[0]
                if landmark and landmark not in landmarks:
                    landmarks.append(landmark)
        except Exception:
            continue
    return landmarks