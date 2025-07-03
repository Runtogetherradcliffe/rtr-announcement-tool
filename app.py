
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

    intro = random.choice([
        "👋 Ready for another great Thursday with the RTR crew?",
        "🌟 It’s nearly time to lace up! Here's what we’ve got planned:",
        "🙌 Good vibes, good routes – here’s what’s coming up this week:",
        "👟 Thursday is calling – check out this week’s plan!"
    ])

    tour_msg = ""
    gmaps_line = ""
    if "radcliffe market" not in meeting_point.lower():
        tour_msg = "🚌 We’re on tour this week – meeting somewhere different!"
        if pd.notna(gmaps_link) and gmaps_link.strip():
            gmaps_line = f"🗺️ Google Maps: {gmaps_link}"

    location_line = f"📍 Meeting at: {meeting_point}" if meeting_point else ""
    time_line = "🕖 We set off at 7:00pm sharp – don’t be late!"

    route_lines = ["This week we’ve got two route options to choose from:"]
    if link_8k:
        route_lines.append(f"• 8k route: {link_8k}")
    if link_5k:
        route_lines.append(f"• 5k route: {link_5k} (or do it as a Jeff – run/walk style!)")
    route_section = "\n".join(route_lines)

    extra_lines = []
    if "dark" in notes:
        extra_lines.append("🔦 Don’t forget your hi-vis and headtorch – we’ll be running after dark.")
    if "social" in special:
        extra_lines.append("🍻 After the run, we’re heading out for drinks and food – come along!")
    extra_msg = "\n".join(extra_lines)

    footer = """📲 Book now:
https://groups.runtogether.co.uk/RunTogetherRadcliffe/Runs
❌ Can’t make it? Cancel at least 1 hour before:
https://groups.runtogether.co.uk/My/BookedRuns"""

    signoff = random.choice([
        "Looking forward to seeing you there! 🎉",
        "Grab your shoes, bring your smiles – see you Thursday! 👟",
        "Bring the energy – we’ve got a great one lined up! 💥"
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

def copy_button(label, content):
    st.text_area(f"{label} Message", value=content, height=300)
    st.download_button(f"📋 Copy {label} text", content, file_name=f"{label.lower()}_message.txt")

copy_button("Email", email_msg)
copy_button("Facebook", facebook_msg)
copy_button("WhatsApp", whatsapp_msg)
