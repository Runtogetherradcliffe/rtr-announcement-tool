
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
    meeting_point = row.get("Meeting point", "[missing meeting point]")
    route = row.get("8k Route", "[missing route]")
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

    footer = """📲 Please book on ASAP here:
https://groups.runtogether.co.uk/RunTogetherRadcliffe/Runs

❌ Can’t make it? Cancel at least 1 hour before:
https://groups.runtogether.co.uk/My/BookedRuns"""

    email_msg = f"""👋 {intro}

📍 **Meeting point:** {meeting_point}
🛣️ **Route:** {route}
🕖 **Start time:** 7:00pm

{safety_msg}
{social_msg}

{footer}

{signoff}"""

    whatsapp_msg = f"""*RunTogether Radcliffe – This Thursday*

📍 {meeting_point}
🛣️ {route}
🕖 7:00pm

{safety_msg}
{social_msg}

{footer}

{signoff}"""

    facebook_msg = f"""📣 {intro}

📍 Meeting point: {meeting_point}
🛣️ Route: {route}
🕖 Start: 7:00pm

{safety_msg}
{social_msg}

{footer}

{signoff}"""
else:
    email_msg = whatsapp_msg = facebook_msg = "⚠️ No route found for next Thursday. Please check the schedule."

st.subheader("📧 Weekly Email")
st.text_area("Email Text", value=email_msg, height=300)

st.subheader("💬 WhatsApp Message")
st.text_area("WhatsApp Text", value=whatsapp_msg, height=250)

st.subheader("📱 Facebook / Instagram Post")
st.text_area("Facebook / Instagram Text", value=facebook_msg, height=250)
