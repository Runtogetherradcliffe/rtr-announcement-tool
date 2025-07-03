
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random

st.set_page_config(page_title="RTR Weekly Announcement Generator", layout="centered")
st.title("🏃‍♀️ RunTogether Radcliffe – Weekly Run Announcement Generator")

# Load schedule
@st.cache_data
def load_schedule():
    df = pd.read_excel("RTR route schedule.xlsx", sheet_name=0)
    df.columns = df.columns.str.strip()
    df["Date"] = pd.to_datetime(df["2025 Date"], errors="coerce")
    return df

df = load_schedule()

# Determine next Thursday
today = datetime.today()
next_thursday = today + timedelta((3 - today.weekday()) % 7)
this_week = df[df["Date"] == next_thursday]

if not this_week.empty:
    row = this_week.iloc[0]
    location = row["Meeting point"] if pd.notna(row["Meeting point"]) else None
    is_dark = next_thursday.month in [10, 11, 12, 1, 2, 3]

    if location:
        phrases = [
            f"We're heading out from {location} this Thursday evening!",
            f"This week we’ll be meeting at {location} for our run.",
            f"Our run starts from {location} this week — hope you can join us!",
        ]
        intro = random.choice(phrases)

        safety_msg = "Please wear hi-vis and bring a headtorch 🔦" if is_dark else ""
        footer = """📲 Please book on ASAP here:
https://groups.runtogether.co.uk/RunTogetherRadcliffe/Runs

❌ Can’t make it? Cancel at least 1 hour before:
https://groups.runtogether.co.uk/My/BookedRuns"""

        signoffs = [
            "See you Thursday! 👟",
            "Looking forward to it! 💪",
            "Hope to see lots of you there!",
            "Bring the energy and see you soon!",
            "Let’s make it another great one! 🔥"
        ]

        social_post = f"""📣 {intro}

{("🔦 " + safety_msg) if safety_msg else ""}

{footer}

{random.choice(signoffs)}"""

        whatsapp_msg = f"""*RunTogether Radcliffe – This Thursday*

{intro}

{safety_msg if safety_msg else ""}

📍 *{location}*
🕖 7pm start

{footer}
{random.choice(signoffs)}"""
    else:
        social_post = "⚠️ Please update the spreadsheet to provide this week's route."
        whatsapp_msg = "⚠️ Please update the spreadsheet to provide this week's route."
else:
    social_post = "⚠️ No route found for the next Thursday. Please check the schedule."
    whatsapp_msg = "⚠️ No route found for the next Thursday. Please check the schedule."

st.subheader("📱 Facebook / Instagram Message")
st.text_area("Social Media Text", value=social_post, height=250)

st.subheader("💬 WhatsApp Message")
st.text_area("WhatsApp Text", value=whatsapp_msg, height=200)
