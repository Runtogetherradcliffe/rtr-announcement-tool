import streamlit as st
import pandas as pd
import datetime
import os
import sys

print("🔍 Current working directory:", os.getcwd())
print("📦 Python sys.path:", sys.path)

try:
    from route_summary_geocoding import generate_route_summary
    print("✅ Successfully imported generate_route_summary")
except ImportError as e:
    print("❌ Failed to import generate_route_summary:", e)
    raise

from strava_utils import get_strava_access_token

st.set_page_config(page_title="RunTogether Route Announcements", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_excel("RTR route schedule.xlsx")
    df["Date"] = pd.to_datetime(df["Date"]).dt.date
    return df

def get_upcoming_runs(df, num_weeks=1):
    today = datetime.date.today()
    upcoming = df[(df["Date"] >= today)].sort_values("Date").head(num_weeks)
    return upcoming

def build_announcement(df, access_token):
    messages = []
    for _, row in df.iterrows():
        date = row["Date"]
        title = row["Title"]
        link = row["Strava Route Link"]
        summary = generate_route_summary(link, access_token)
        date_str = f"{title}: {link}" if pd.notna(link) else f"{title}"
        messages.append(f"• {date_str}\n  {summary}")
    return messages

def main():
    st.title("🏃 RunTogether Announcement Generator")

    df = load_data()
    access_token = get_strava_access_token()

    st.sidebar.markdown("## Settings")
    num_weeks = st.sidebar.slider("How many weeks to show?", 1, 6, 2)

    upcoming = get_upcoming_runs(df, num_weeks=num_weeks)

    if upcoming.empty:
        st.warning("No upcoming runs found.")
        return

    st.markdown("### 📣 Weekly Route Announcements")
    announcements = build_announcement(upcoming, access_token)
    announcement_text = (
        "🛣️ This week we’ve got two route options to choose from:\n" + "\n".join(announcements)
        if len(announcements) > 1
        else announcements[0]
    )

    st.text_area("Generated Announcement", value=announcement_text, height=300)
    st.code(announcement_text, language="markdown")

if __name__ == "__main__":
    main()
