
import streamlit as st
import pandas as pd
from datetime import datetime

from strava_utils import refresh_strava_token, download_gpx_from_strava_route, extract_landmarks_from_gpx

@st.cache_data
def load_data():
    df = pd.read_excel("RTR route schedule.xlsx")
    df.columns = df.columns.str.strip()
    df = df.loc[:, ~pd.Series(df.columns).duplicated()]
    df["Date"] = pd.to_datetime(df["Date"]).dt.date
    return df

try:
    client_id = st.secrets["STRAVA_CLIENT_ID"]
    client_secret = st.secrets["STRAVA_CLIENT_SECRET"]
    refresh_token = st.secrets["STRAVA_REFRESH_TOKEN"]
    token_data = refresh_strava_token(client_id, client_secret, refresh_token)
    access_token = token_data.get("access_token")
    st.write("✅ Access token acquired.")
except Exception as e:
    st.warning("⚠️ Could not refresh Strava access token. GPX fetch will be skipped.")
    access_token = None

# Placeholder logic for future content
st.title("RTR Announcement Tool")
