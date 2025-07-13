import requests
import streamlit as st

def get_strava_access_token():
    client_id = st.secrets["client_id"]
    client_secret = st.secrets["client_secret"]
    refresh_token = st.secrets["refresh_token"]

    response = requests.post(
        url="https://www.strava.com/api/v3/oauth/token",
        data={
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        }
    )

    response.raise_for_status()
    return response.json()["access_token"]

def fetch_strava_activities(access_token, per_page=10):
    url = f"https://www.strava.com/api/v3/athlete/activities?per_page={per_page}"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()
