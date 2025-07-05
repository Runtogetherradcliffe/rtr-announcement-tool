
import requests

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

        # Generate a natural description based on elevation
        if elevation_gain < 20:
            comment = "a flat and fast route 🟢"
        elif elevation_gain < 60:
            comment = "a gently rolling route 🌿"
        else:
            comment = "a hillier challenge ⛰️"

        return f"{distance_km} km with {elevation_gain}m of elevation – {comment}"
    else:
        return f"(⚠️ Could not fetch route details)"
