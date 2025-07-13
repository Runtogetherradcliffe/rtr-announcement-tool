
import streamlit as st
import pandas as pd
from strava_utils import fetch_strava_activities
from route_summary_geocoding import summarize_routes

st.set_page_config(page_title="RTR Route Announcement Tool")

st.title("Run Together Radcliffe - Route Announcement Tool")

uploaded_file = st.file_uploader("Upload RTR Route Schedule (Excel)", type=["xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        st.success("File uploaded successfully.")

        st.subheader("Schedule Preview")
        st.dataframe(df)

        st.subheader("Fetching Strava Activities...")
        strava_activities = fetch_strava_activities()
        st.success(f"Fetched {len(strava_activities)} activities.")

        st.subheader("Summarizing Routes")
        summary_df = summarize_routes(df, strava_activities)
        st.dataframe(summary_df)

    except Exception as e:
        st.error(f"Error processing file: {e}")
else:
    st.info("Please upload an Excel schedule file.")
