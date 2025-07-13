import streamlit as st
import pandas as pd
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from route_summary_geocoding import summarize_routes
from strava_utils import fetch_strava_activities

st.set_page_config(page_title="RunTogether Route Announcements", layout="wide")

@st.cache_data
def load_excel(file):
    return pd.read_excel(file, engine="openpyxl")

st.title("🏃‍♀️ RunTogether Route Announcement Tool")

uploaded = st.file_uploader("Upload the RTR route schedule Excel file", type="xlsx")
if uploaded:
    df = load_excel(uploaded)

    today = pd.to_datetime("today").normalize()
    df["2025 Date"] = pd.to_datetime(df["2025 Date"])
    upcoming = df[df["2025 Date"] >= today].sort_values("2025 Date").head(1)

    if not upcoming.empty:
        st.subheader(f"📅 Next run: {upcoming.iloc[0]['2025 Date'].date()}")
        with st.spinner("Fetching Strava activities..."):
            activities = fetch_strava_activities()
        with st.spinner("Generating route summary..."):
            summary = summarize_routes(upcoming, activities)
        for s in summary:
            st.markdown(s)
    else:
        st.warning("No upcoming dates found in the spreadsheet.")
else:
    st.info("Please upload the route schedule to begin.")
