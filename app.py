
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
    meeting_point = row.get("Meeting point", "[Missing meeting point]")
    route = row.get("8k Route", "[Missing route]")
    notes = str(row.get("Notes", "")).lower()
    special_events = str(row.get("Special events", "")).lower()

    intros = [
        "Hope your week’s going well!",
        "Ready to clock some miles this Thursday?",
        "We’ve got a great route lined up – come join us!",
        "It’s almost Thursday, and that means it’s time to run! 🏃",
        "This week’s run is nearly here – let’s get moving!"
    ]

    signoffs = [
        "See you there, legends! 👟",
        "Headtorch + smile = ready. 😄",
        "Can’t wait to see you all!",
        "Let’s make it another good one! 💪",
        "Run together, smile together!"
    ]

    safety_msg = "🔦 Please wear hi-vis and bring a headtorch – we’ll be running after dark." if "dark" in notes else ""
    social_msg = "🍻 After the run, we’re heading to the market for food and drinks – come along for the social!" if "social" in special_events else ""

    footer = """📲 Please book on ASAP here:
https://groups.runtogether.co.uk/RunTogetherRadcliffe/Runs

❌ Can’t make it? Cancel at least 1 hour before:
https://groups.runtogether.co.uk/My/BookedRuns"""

    intro = random.choice(intros)
    signoff = random.choice(signoffs)

    email_msg = f"""👋 {intro}

📍 We’re meeting at **{meeting_point}**
🛣️ Route: **{route}**
🕖 Start time: **7:00pm**

{safety_msg}
{social_msg}

{footer}

{signoff}"""

    social_msg_out = f"""📣 {intro}

📍 {meeting_point}
🛣️ {route}
🕖 7pm start

{safety_msg}
{social_msg}

{footer}

{signoff}"""

    whatsapp_msg = f"""*RunTogether Radcliffe – This Thursday*

📍 {meeting_point}
🛣️ {route}
🕖 7pm

{safety_msg}
{social_msg}

{footer}

{signoff}"""
else:
    email_msg = "⚠️ No route found for next Thursday. Please check the schedule."
    social_msg_out = email_msg
    whatsapp_msg = email_msg

st.subheader("📧 Weekly Email Message")
st.text_area("Email Text", value=email_msg, height=300)

st.subheader("📱 Facebook / Instagram Message")
st.text_area("Social Media Text", value=social_msg_out, height=250)

st.subheader("💬 WhatsApp Message")
st.text_area("WhatsApp Text", value=whatsapp_msg, height=200)
