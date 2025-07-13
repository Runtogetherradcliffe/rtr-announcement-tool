import streamlit as st
import pandas as pd
import sys

from route_summary_geocoding import summarize_routes
from strava_utils import fetch_strava_activities  # Assuming this is the right function name

st.set_page_config(page_title="RunTogether Route Announcements", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_excel("RTR route schedule.xlsx")
    df["2025 Date"] = pd.to_datetime(df["2025 Date"]).dt.date
    return df

def get_upcoming_runs(df, num_weeks=1):
    from datetime import date, timedelta
    today = date.today()
    max_date = today + timedelta(weeks=num_weeks)
    return df[(df["2025 Date"] >= today) & (df["2025 Date"] <= max_date)]

def main():
    st.title("🏃 RunTogether Announcement Generator")

    try:
        df = load_data()
    except Exception as e:
        st.error(f"Failed to load Excel: {e}")
        return

    try:
        access_token = "FAKE_TOKEN"  # Placeholder
        activities = fetch_strava_activities()
    except Exception as e:
        st.warning(f"Could not fetch Strava activities: {e}")
        activities = []

    try:
        upcoming = get_upcoming_runs(df)
    except Exception as e:
        st.error(f"Failed to filter upcoming runs: {e}")
        return

    if upcoming.empty:
        st.info("No upcoming runs found in the schedule.")
        return

    st.subheader("📅 Upcoming Run Info")
    st.dataframe(upcoming)

    st.subheader("📝 Route Summary")
    try:
        summary = summarize_routes(upcoming, activities)
        st.dataframe(summary)
    except Exception as e:
        st.error(f"Failed to generate route summary: {e}")
        return

    st.subheader("📢 Announcement Text")
    messages = []
    for _, row in upcoming.iterrows():
        line = f"{row['2025 Date']} - Meet at {row['Meeting point']} for {row['8k Route']} and {row['5k Route']}."
        messages.append(f"{line}")
    announcement_text = "\n".join(messages)
    st.code(announcement_text, language="markdown")

if __name__ == "__main__":
    main()
