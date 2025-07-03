
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
    df["Date"] = pd.to_datetime(df["2025 Date"], errors="coerce")
    return df

df = load_schedule()
today = datetime.today()
next_thursday = today + timedelta((3 - today.weekday()) % 7)
this_week = df[df["Date"] == next_thursday]

if not this_week.empty:
    row = this_week.iloc[0]
    meeting_point = row["Meeting point"]
    route = row["8k Route"]
    is_dark = next_thursday.month in [10, 11, 12, 1, 2, 3]
    is_social = "social" in str(row.get("Special events", "")).lower()

    intros = [
        "Hope your week’s going well!",
        "Ready for another great Thursday together?",
        "Looking forward to catching up on the run!",
        "Let’s make this Thursday another fun one!",
        "Time to lace up – here’s what’s planned:"
    ]

    signoffs = [
        "See you Thursday! 👟",
        "Bring your smiles and let's run! 🏃‍♀️",
        "Hope to see lots of you there!",
        "Let’s make it a good one!",
        "Running into the weekend starts here! 💪"
    ]

    intro = random.choice(intros)
    route_msg = f"Our route this week is **{route}**, meeting at **{meeting_point}**."
    safety_msg = "Please remember to wear hi-vis and bring a light 🔦" if is_dark else ""
    social_msg = "We’ll be heading to the market for food and drinks after — come along! 🍻" if is_social else ""

    footer = """📲 Please book on ASAP here:
https://groups.runtogether.co.uk/RunTogetherRadcliffe/Runs

❌ Can’t make it? Cancel at least 1 hour before:
https://groups.runtogether.co.uk/My/BookedRuns"""

    email_msg = f"""👋 {intro}

📍 {route_msg}

{("🔦 " + safety_msg) if safety_msg else ""}
{social_msg}

🕖 **7:00pm start**

{footer}

{random.choice(signoffs)}"""
else:
    email_msg = "⚠️ No route found for next Thursday. Please check the schedule."

st.subheader("📧 Weekly Email Message")
st.text_area("Email Text", value=email_msg, height=350)
