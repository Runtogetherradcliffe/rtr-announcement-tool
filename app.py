
import streamlit as st
import pandas as pd
import random
from datetime import datetime

st.title("RunTogether Radcliffe – Weekly Run Announcement Generator")

# Load from pre-included schedule
df = pd.read_excel("RTR route schedule.xlsx", sheet_name="schedule")
df = df.drop(columns=["C25K week", "C25K link"], errors="ignore")
df["2025 Date"] = pd.to_datetime(df["2025 Date"], errors="coerce")

trail_phrases = [
    "We’re exploring the wonderful trails around Radcliffe this week — a great way to enjoy the local scenery on the move!",
    "Join us for a scenic route through some of Radcliffe’s finest trails — soft underfoot and full of charm.",
    "It’s trail time! Get ready for a fun, varied route with great views and good company.",
    "This week we hit the trails — the perfect way to mix up the pace and enjoy the outdoors.",
    "Trail lovers, this one’s for you — come enjoy some of our favourite off-road paths!"
]

road_phrases = [
    "We’re sticking to well-lit roads this week — don’t forget your hi-vis and head torch!",
    "A night-time road run awaits — be safe, be seen, and join us for a steady evening loop.",
    "We’ll be keeping it simple on the streets this week — bring your lights and let’s go!",
    "We’re heading out on a steady road route this week — great for pacing and winter fitness!",
    "Expect smooth tarmac and streetlights this week — just remember your hi-vis and lights!"
]

sign_offs = [
    "See you Thursday!",
    "Looking forward to running with you Thursday!",
    "Happy running – see you soon!",
    "Bring your head torch and a smile!",
    "Let’s make it a good one!"
]


today = datetime.today().date()
future_dates = sorted(df[df["2025 Date"].dt.date >= today]["2025 Date"].dt.date.unique())
selected_date = st.selectbox("Select the run date:", future_dates, index=0)


row = df[df["2025 Date"].dt.date == selected_date].iloc[0]
date_str = row["2025 Date"].strftime("%A %d %B %Y")
meeting_point = row["Meeting point"]
notes = row["Notes"] or ""
special_event = str(row["Special events"]).lower() if pd.notna(row["Special events"]) else ""
route_8k = f"{row['8k Route']} ({row['8k Strava link']})"
route_5k = f"{row['5k Route']} ({row['5k Strava link']})"

if "trail" in notes.lower():
    note_msg = random.choice(trail_phrases)
elif "dark" in notes.lower():
    note_msg = random.choice(road_phrases) + "\n\nIf you’re able to join us, please ensure you have your lights with you and wear hi-vis clothing."
else:
    note_msg = notes

social_msg = ""
if "social" in special_event:
    social_msg = "After the run, many of us are going for drinks and food at the market, so it should be a nice social occasion."

sign_off = random.choice(sign_offs)

email_msg = f"""Subject: This Week’s Run – {date_str}

Join us this Thursday for our weekly RunTogether Radcliffe group run!

📍 Meeting point: {meeting_point}
🕖 Time: 7:00pm start

You can choose between:
- 🛣️ 8k route: {route_8k}
- 🏃 5k route: {route_5k}

{note_msg}
{social_msg}

📲 Please book on ASAP here:
https://groups.runtogether.co.uk/RunTogetherRadcliffe/Runs

❌ Can’t make it? Cancel at least 1 hour before:
https://groups.runtogether.co.uk/My/BookedRuns

{sign_off}"""

fb_msg = f"""📣 RunTogether Radcliffe – Thursday {date_str}

📍 {meeting_point}
🕖 7pm start

8k: {row['8k Route']}
https://www.strava.com/routes/{row['8k Strava link'].split('/')[-1]}

5k: {row['5k Route']}
https://www.strava.com/routes/{row['5k Strava link'].split('/')[-1]}

{note_msg}
{social_msg}

📲 Book now: https://groups.runtogether.co.uk/RunTogetherRadcliffe/Runs"""

wa_msg = f"""🏃 Thursday {date_str} – RunTogether Radcliffe!

📍 {meeting_point} | 7pm

8k: {row['8k Route']}
5k: {row['5k Route']}

{note_msg}

📲 Book: https://groups.runtogether.co.uk/RunTogetherRadcliffe/Runs"""

st.subheader("📧 Email Message")
st.text_area("Email:", value=email_msg, height=300)

st.subheader("📱 Facebook Caption")
st.text_area("Facebook:", value=fb_msg, height=250)

st.subheader("💬 WhatsApp Message")
st.text_area("WhatsApp:", value=wa_msg, height=250)
