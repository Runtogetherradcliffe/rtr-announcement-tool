
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

available_dates = df["Date"].dropna().sort_values().unique().tolist()
default_index = available_dates.index(next_thursday) if next_thursday in available_dates else 0
selected_date = st.selectbox("Select run date:", available_dates, index=default_index)

this_week = df[df["Date"] == selected_date]

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
        "👋 Let’s get together for another great Thursday run!",
        "🏃‍♂️ Time for another outing with the RTR crew!",
        "🗓️ Thursday’s nearly here – and so is this week’s route!",
        "🌟 Another week, another chance to move, chat, and feel good!"
    ]

    signoffs = [
        "Bring good vibes — and we’ll see you out there! 👟",
        "Let’s make it a good one — you in? 💪",
        "Running + good company = best way to spend a Thursday!",
        "Bring a friend, bring your energy — let’s go! 🏃‍♀️"
    ]

    intro = random.choice(intros)
    signoff = random.choice(signoffs)

    tour_msg = ""
    if "radcliffe market" not in meeting_point.lower():
        tour_msg = "🚌 We’re on tour this week – meeting somewhere different!"

    safety_msg = "🔦 Don’t forget your hi-vis and headtorch — we want you glowing for all the right reasons!" if "dark" in notes else ""
    social_msg = "🍻 Fancy a pint? We’re heading to the market after for food and drinks!" if "social" in special else ""

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

    footer = """📲 Book on when you can:
https://groups.runtogether.co.uk/RunTogetherRadcliffe/Runs
❌ Can’t make it? Just cancel with 1 hour’s notice:
https://groups.runtogether.co.uk/My/BookedRuns"""

    email_msg = f"""{intro}

{tour_msg}
📍 Meeting at: {meeting_point}  
{routes_text}  
🕖 We’ll be setting off at 7:00pm sharp
{safety_msg}
{social_msg}
{footer}
{signoff}"""

    facebook_msg = f"""📣 {intro}

{tour_msg}
📍 {meeting_point}  
{routes_text}  
🕖 7pm start
{safety_msg}
{social_msg}
{footer}
{signoff}"""

    whatsapp_msg = f"""*RunTogether Radcliffe – This Thursday*

{tour_msg}
📍 {meeting_point}  
{routes_text}  
🕖 7pm
{safety_msg}
{social_msg}
{footer}
{signoff}"""
else:
    email_msg = facebook_msg = whatsapp_msg = "⚠️ No route found for selected date. Please check the schedule."

st.subheader("📧 Weekly Email Message")
st.text_area("Email Text", value=email_msg, height=350)

st.subheader("📱 Facebook / Instagram Post")
st.text_area("Facebook / Instagram Text", value=facebook_msg, height=300)

st.subheader("💬 WhatsApp Message")
st.text_area("WhatsApp Text", value=whatsapp_msg, height=300)
