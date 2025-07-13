
import streamlit as st
import pandas as pd
import os
import sys

from route_summary_geocoding import summarize_routes
from strava_utils import fetch_strava_activities

st.set_page_config(page_title="RunTogether Route Announcements", layout="wide")

@st.cache_data
def load_schedule():
    path = os.path.join(os.path.dirname(__file__), "RTR route schedule.xlsx")
    df = pd.read_excel(path, engine="openpyxl")
    return df

st.title("🏃‍♀️ RunTogether Route Announcements")

try:
    df_schedule = load_schedule()
    st.success("✅ Loaded schedule from local file.")
except Exception as e:
    st.error(f"❌ Failed to load route schedule: {e}")
    st.stop()

strava_token = st.secrets["STRAVA_ACCESS_TOKEN"]

activities = fetch_strava_activities(access_token=strava_token)
st.write(f"✅ Found {len(activities)} activities.")

route_summaries = summarize_routes(df_schedule, strava_token)
st.write("✅ Route summaries generated:")
for summary in route_summaries:
    st.markdown(summary)
