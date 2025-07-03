
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
    gmaps_link = row.get("Meeting point google link", "")
    route_8k = row.get("8k Route", "")
    route_5k = row.get("5k Route", "")
    link_8k = row.get("8k Strava link", "")
    link_5k = row.get("5k Strava link", "")
    notes = str(row.get("Notes", "")).lower()
    special = str(row.get("Special events", "")).lower()

    intro = "👋 Hope you're having a great week! Here's what we’ve got planned for Thursday..."

    tour_msg = ""
    gmaps_line = ""
    if "radcliffe market" not in meeting_point.lower():
        tour_msg = "🚌 We’re on tour this week – meeting somewhere different!"
        if pd.notna(gmaps_link) and gmaps_link.strip():
            gmaps_line = f"🗺️ Google Maps: {gmaps_link}"

    location_line = f"📍 Meeting at: {meeting_point}" if meeting_point else ""
    time_line = "🕖 Set off time: 7:00pm"

    route_lines = ["As usual we’ve got 2 route options this week."]
    if link_8k:
        route_lines.append(f"The 8k route is 🔗 {link_8k}")
    if link_5k:
        route_lines.append(f"The 5k Route is 🔗 {link_5k} and you have the option to do this as a run or ‘Jeff’ (which is run / walk intervals)")
    route_section = "\n".join(route_lines)

    extra_lines = []
    if "dark" in notes:
        extra_lines.append("🔦 Bring your hi-vis and headtorch – it’ll be dark!")
    if "social" in special:
        extra_lines.append("🍻 Social after the run – drinks and food at the market!")
    extra_msg = "\n".join(extra_lines)

    footer = """\n📲 Book on here:
https://groups.runtogether.co.uk/RunTogetherRadcliffe/Runs
❌ Need to cancel? Please do so at least 1 hour before:
https://groups.runtogether.co.uk/My/BookedRuns"""

    signoff = random.choice([
        "See you out there! 👟",
        "Let’s make it a good one! 💪",
        "Tag your run buddies and get booked in! 🏃"
    ])

    email_msg = f"""{intro}

{tour_msg}
{location_line}
{gmaps_line}
{time_line}

{route_section}

{extra_msg}

{footer}

{signoff}"""

    facebook_msg = f"""📣 {intro}

{tour_msg}
{location_line}
{gmaps_line}
{time_line}

{route_section}

{extra_msg}

{footer}

👍 {signoff}"""

    whatsapp_msg = f"""*RunTogether Radcliffe – This Thursday!*

{tour_msg}
{location_line}
{gmaps_line}
{time_line}

{route_section}

{extra_msg}

{footer}

{signoff}"""

else:
    email_msg = facebook_msg = whatsapp_msg = "⚠️ No route found for selected date. Please check the schedule."

st.subheader("📧 Email Message")
st.text_area("Email", value=email_msg, height=420)

st.subheader("📱 Facebook / Instagram Post")
st.text_area("Facebook / Instagram", value=facebook_msg, height=400)

st.subheader("💬 WhatsApp Message")
st.text_area("WhatsApp", value=whatsapp_msg, height=400)
