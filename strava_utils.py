import os
import requests


def refresh_strava_token(client_id: str, client_secret: str, refresh_token: str) -> str:
    """Request a fresh Strava access token."""
    response = requests.post(
        "https://www.strava.com/oauth/token",
        data={
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        },
    )
    response.raise_for_status()
    return response.json()["access_token"]


# This function assumes you have your STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET,
# and REFRESH_TOKEN set in the environment

def get_strava_access_token():
    STRAVA_CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
    STRAVA_CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")
    REFRESH_TOKEN = os.getenv("STRAVA_REFRESH_TOKEN")

    if not STRAVA_CLIENT_ID or not STRAVA_CLIENT_SECRET or not REFRESH_TOKEN:
        raise ValueError("Strava credentials are missing from environment variables.")

    return refresh_strava_token(STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET, REFRESH_TOKEN)
