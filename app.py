
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random

st.set_page_config(page_title="RTR Weekly Announcement Generator", layout="centered")
st.title("🏃‍♀️ RunTogether Radcliffe – Weekly Run Announcement Generator")

@st.cache_data
def load_data():
    df = pd.read_excel("RTR route schedule.xlsx")
    df.columns = df.columns.str.strip()
    df["Date"] = pd.to_datetime(df["2025 Date"], errors="coerce").dt.date
    return df

df = load_data()
today = datetime.today().date()
next_thursday = today + timedelta((3 - today.weekday()) % 7)
available_dates = df["Date"].dropna().sort_values().unique().tolist()
default_index = available_dates.index(next_thursday) if next_thursday in available_dates else 0
selected_date = st.selectbox("Select run date:", available_dates, index=default_index)

row = df[df["Date"] == selected_date].iloc[0]

meeting_point = row.get("Meeting point", "")
gmaps_link = row.get("Meeting point google link", "")
route_8k_name = row.get("8k Route", "")
route_5k_name = row.get("5k Route", "")
link_8k = row.get("8k Strava link", "")
link_5k = row.get("5k Strava link", "")
notes = str(row.get("Notes", "")).lower()
special = str(row.get("Special events", "")).lower()
events_text = notes + " " + special

intro = random.choice([
    "👋 Hope you're having a great week! Here's what we’ve got planned for Thursday…",
    "🌟 Get ready for another great Thursday evening with the RTR crew!",
    "🙌 Here’s what’s coming up this week at RunTogether Radcliffe!"
])

tour_msg = ""
gmaps_line = ""
if "radcliffe market" not in meeting_point.lower():
    tour_msg = "🚌 We’re on tour this week – meeting somewhere different!"
    if gmaps_link:
        gmaps_line = f"🗺️ Google Maps: {gmaps_link}"

location_line = f"📍 Meeting at: {meeting_point}" if meeting_point else ""
time_line = "🕖 We set off at 7:00pm"

# Route descriptions
route_lines = ["🛣️ This week we’ve got two route options to choose from:"]
if route_8k_name and link_8k:
    route_lines.append(f"• 8k route – *{route_8k_name}*: {link_8k}")
if route_5k_name and link_5k:
    route_lines.append(f"• 5k route – *{route_5k_name}*: {link_5k} (or do it as a Jeff – run/walk style!)")
route_section = "\n".join(route_lines)

# Special notes and keywords
extra_lines = []
if "wear" in events_text and "green" in events_text:
    extra_lines.append("🟢 It's **Wear it Green Day** for Mental Health Awareness Week! Join us by wearing something green.")
if "pride" in events_text:
    extra_lines.append("🌈 It’s our **Pride Run**! We’re encouraging everyone to wear something colourful and celebrate together.")
if "dark" in events_text:
    extra_lines.append("🔦 Don’t forget your hi-vis and headtorch – we’ll be running after dark.")
if "social" in events_text:
    extra_lines.append("🍻 Afterwards, we’re heading to **Radcliffe Market** for a post-run social – come along!")
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

# Format each channel
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

# Display
st.subheader("📧 Email Message")
st.text_area("Email", value=email_msg, height=500)

st.subheader("📱 Facebook / Instagram Post")
st.text_area("Facebook / Instagram", value=facebook_msg, height=500)

st.subheader("💬 WhatsApp Message")
st.text_area("WhatsApp", value=whatsapp_msg, height=500)
