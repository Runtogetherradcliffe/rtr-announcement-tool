import requests
import streamlit as st
import polyline

STRAVA_BASE = "https://www.strava.com/api/v3"

def get_strava_access_token():
    creds = st.secrets["strava"]
    resp = requests.post(
        "https://www.strava.com/oauth/token",
        data={
            "client_id": creds["client_id"],
            "client_secret": creds["client_secret"],
            "grant_type": "refresh_token",
            "refresh_token": creds["refresh_token"],
        }
    )
    resp.raise_for_status()
    return resp.json()["access_token"]

def get_route_id_from_url(url):
    try:
        return url.strip("/").split("/")[-1]
    except Exception:
        return None

def fetch_route_coordinates(route_url, access_token=None):
    route_id = get_route_id_from_url(route_url)
    if not route_id:
        return []

    if access_token is None:
        access_token = get_strava_access_token()

    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(f"{STRAVA_BASE}/routes/{route_id}", headers=headers)
    response.raise_for_status()
    data = response.json()

    # Decode polyline to (lat, lon) coordinates
    if "map" in data and "summary_polyline" in data["map"]:
        return polyline.decode(data["map"]["summary_polyline"])
    return []
