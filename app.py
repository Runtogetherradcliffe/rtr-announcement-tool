
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random

st.set_page_config(page_title="RTR Weekly Announcement Generator", layout="centered")
st.title("🏃‍♀️ RunTogether Radcliffe – Weekly Run Announcement Generator")

@st.cache_data
def load_schedule():
    df = pd.read_excel("RTR route schedule.xlsx", sheet_name=0)
    df.columns = df.columns.str.strip()
    df["Date"] = pd.to_datetime(df["2025 Date"], errors="coerce").dt.date
    return df

df = load_schedule()
today = datetime.today().date()
next_thursday = today + timedelta((3 - today.weekday()) % 7)
this_week = df[df["Date"] == next_thursday]

if not this_week.empty:
    row = this_week.iloc[0]
    meeting_point = row.get("Meeting point", "[missing meeting point]")
    route_8k = row.get("8k Route")
    route_5k = row.get("5k Route")
    link_8k = row.get("8k Strava link")
    link_5k = row.get("5k Strava link")
    notes = str(row.get("Notes", "")).lower()
    special = str(row.get("Special events", "")).lower()

    intros = [
        "Hope your week’s going well!",
        "Excited for another Thursday run?",
        "Lace up — here’s what we’ve got planned!",
        "Looking forward to another great evening together!",
        "Let’s make this week’s run another good one!"
    ]

    signoffs = [
        "See you Thursday! 👟",
        "Can’t wait to run with you all!",
        "Bring the energy and let’s go!",
        "Let’s make it count!",
        "Keep running strong!"
    ]

    intro = random.choice(intros)
    signoff = random.choice(signoffs)

    safety_msg = "🔦 Please bring a headtorch and wear hi-vis — we’ll be running after dark." if "dark" in notes else ""
    social_msg = "🍻 After the run, we’re heading to the market for drinks and food. Join us!" if "social" in special else ""

    route_lines = []
    if pd.notna(route_8k):
        route_lines.append(f"🛣️ 8k Route: {route_8k}")
        if pd.notna(link_8k):
            route_lines.append(f"🔗 {link_8k}")
    if pd.notna(route_5k):
        route_lines.append(f"🏃 5k Route: {route_5k}")
        if pd.notna(link_5k):
            route_lines.append(f"🔗 {link_5k}")
    routes_text = "\n".join(route_lines) if route_lines else "[No route info available]"

    footer = """📲 Please book on ASAP here:
https://groups.runtogether.co.uk/RunTogetherRadcliffe/Runs

❌ Can’t make it? Cancel at least 1 hour before:
https://groups.runtogether.co.uk/My/BookedRuns"""

    full_message = f"""👋 {intro}

📍 We’re meeting at {meeting_point}  
{routes_text}  
🕖 Start time: 7:00pm

{safety_msg}
{social_msg}

{footer}

{signoff}"""
else:
    full_message = "⚠️ No route found for next Thursday. Please check the schedule."

st.subheader("📧 Weekly Email / Social Message")
st.text_area("Generated Message", value=full_message, height=400)
