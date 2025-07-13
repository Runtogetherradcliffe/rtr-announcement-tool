
import streamlit as st
import pandas as pd
import os

from route_summary_geocoding import summarize_routes
from strava_utils import get_strava_access_token, fetch_strava_activities

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

access_token = get_strava_access_token()

# --- Diagnostics ---
with st.expander("🔍 Token Diagnostics"):
    token_info = get_strava_access_token(return_full_response=True)
    st.json(token_info)

    st.write("Token Scope:", token_info.get("scope"))
    st.write("Expires at:", token_info.get("expires_at"))

activities = fetch_strava_activities(access_token=access_token)
st.write(f"✅ Found {len(activities)} activities.")

route_summaries = summarize_routes(activities)
st.write("✅ Route summaries generated:")
for summary in route_summaries:
    st.markdown(summary)
