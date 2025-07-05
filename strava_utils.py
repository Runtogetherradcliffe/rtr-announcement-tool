
import requests
import gpxpy
from io import StringIO

def refresh_strava_token(client_id, client_secret, refresh_token):
    response = requests.post("https://www.strava.com/oauth/token", data={
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    })
    return response.json()["access_token"]

def download_gpx_from_strava_route(route_url, access_token):
    route_id = route_url.strip("/").split("/")[-1]
    headers = {"Authorization": f"Bearer {access_token}"}
    export_url = f"https://www.strava.com/api/v3/routes/{route_id}/export_gpx"
    response = requests.get(export_url, headers=headers)
    if response.ok:
        return response.text
    return None

def extract_landmarks_from_gpx(gpx_data, max_points=3):
    if not gpx_data:
        return []

    gpx = gpxpy.parse(StringIO(gpx_data))
    points = gpx.tracks[0].segments[0].points if gpx.tracks else []

    if not points:
        return []

    # sample evenly spaced points along the route
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
                place = data["display_name"].split(",")[0]
                if place not in landmarks:
                    landmarks.append(place)
        except Exception:
            continue

    return landmarks
