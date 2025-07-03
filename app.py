
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random

st.set_page_config(page_title="RTR Weekly Announcement Generator", layout="centered")
st.title("🏃‍♀️ RunTogether Radcliffe – Weekly Run Announcement Generator")

# Load schedule
@st.cache_data
def load_schedule():
    df = pd.read_excel("RTR route schedule.xlsx", sheet_name="schedule")
    df.columns = df.columns.str.strip()
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    return df

df = load_schedule()

# Determine next Thursday
today = datetime.today()
next_thursday = today + timedelta((3 - today.weekday()) % 7)
this_week = df[df["Date"] == next_thursday]

if not this_week.empty:
    row = this_week.iloc[0]
    location = row["Location"] if pd.notna(row["Location"]) else None
    is_trail = "trail" in str(row["Surface"]).lower()
    is_dark = next_thursday.month in [10, 11, 12, 1, 2, 3]
    is_social = pd.notna(row.get("Social"))

    if location:
        # Friendly phrasing variations
        trail_phrases = [
            f"We're heading out on the trails around {location} 🌿.",
            f"This week we’ll be exploring the beautiful paths near {location}.",
            f"Join us for a scenic trail run through {location}!"
        ]
        road_phrases = [
            f"We’re running from {location} this week — perfect for a solid road loop.",
            f"This Thursday’s route starts at {location} – join us for a great evening run!",
            f"Our run this week is from {location}. Come along and stretch those legs!"
        ]

        intro = random.choice(trail_phrases if is_trail else road_phrases)

        safety_msg = "Please wear hi-vis and bring a headtorch 🔦" if is_dark else ""
        social_msg = "After the run, many of us are going for drinks and food at the market — it’ll be a nice social evening! 🍻" if is_social else ""

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

{social_msg}

{footer}

{random.choice(signoffs)}"""

        whatsapp_msg = f"""*RunTogether Radcliffe – This Thursday*

{intro}

{safety_msg if safety_msg else ""}

{social_msg}

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
