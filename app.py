
import streamlit as st
import pandas as pd
import urllib.parse
import json
from datetime import datetime, timedelta
from strava_utils import refresh_strava_token
from route_summary_geocoding import generate_route_summary

# Load Strava credentials
creds = {
    "client_id": st.secrets["client_id"],
    "client_secret": st.secrets["client_secret"],
    "refresh_token": st.secrets["refresh_token"]
}

access_token = refresh_strava_token(creds["client_id"], creds["client_secret"], creds["refresh_token"])

st.set_page_config(page_title="RunTogether Radcliffe Weekly Tool", layout="centered")
st.title("🏃‍♀️ RunTogether Radcliffe – Weekly Run Generator")

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

intro = "👋 Hope you're having a great week! Here's what we’ve got planned for Thursday…"
location = f"📍 Meeting at: {meeting_point}" if meeting_point else ""
tour_msg = ""
gmaps_line = ""
if "radcliffe market" not in meeting_point.lower():
    tour_msg = "🚌 We’re on tour this week – meeting somewhere different!"
    if gmaps_link:
        gmaps_line = f"🗺️ Google Maps: {gmaps_link}"
time = "🕖 We set off at 7:00pm"

# Route description via Strava
desc_8k = generate_route_summary(link_8k, access_token) if link_8k else ""
desc_5k = generate_route_summary(link_5k, access_token) if link_5k else ""

route_lines = ["🛣️ This week we’ve got two route options to choose from:"]
if route_8k_name and link_8k:
    route_lines.append(f"• 8k – {route_8k_name}: {link_8k}")
    if desc_8k:
        route_lines.append("  " + desc_8k.replace("\n", "\n  "))
if route_5k_name and link_5k:
    route_lines.append(f"• 5k – {route_5k_name}: {link_5k} (or Jeff it!)")
    if desc_5k:
        route_lines.append("  " + desc_5k.replace("\n", "\n  "))
route_section = "\n".join(route_lines)

extra_lines = []
if "wear" in events_text and "green" in events_text:
    extra_lines.append("🟢 It's Wear it Green Day for Mental Health Awareness Week! Join us by wearing something green.")
if "pride" in events_text:
    extra_lines.append("🌈 It’s our Pride Run! We’re encouraging everyone to wear something colourful and celebrate together.")
if "dark" in events_text:
    extra_lines.append("🔦 Don’t forget your hi-vis and headtorch – we’ll be running after dark.")
if "social" in events_text:
    extra_lines.append("🍻 Afterwards, we’re heading to Radcliffe Market for a post-run social – come along!")
extra_msg = "\n".join(extra_lines)

footer = """📲 Book now:
https://groups.runtogether.co.uk/RunTogetherRadcliffe/Runs
❌ Can’t make it? Cancel at least 1 hour before:
https://groups.runtogether.co.uk/My/BookedRuns"""

signoff = "👟 Grab your shoes, bring your smiles – see you Thursday!"

# Email message
email_msg = "\n".join([
    intro, tour_msg, location, gmaps_line, time, "", route_section, "", extra_msg, "", footer, "", signoff
])

# Facebook tone toggle
tone = st.radio("Choose Facebook tone", ["Professional", "Social"], key="facebook_tone_selector")
if tone == "Professional":
    facebook_msg = "\n".join([
        "📣 This Week’s Run: Thursday @ 7pm",
        "",
        f"📍 Location: {meeting_point}",
        gmaps_line,
        "🕖 We set off at 7:00pm sharp",
        "",
        "🛣️ Route Options:",
        f"• 8k – {route_8k_name}: {link_8k}",
        f"  {desc_8k}",
        f"• 5k – {route_5k_name}: {link_5k} (or Jeff it!)",
        f"  {desc_5k}",
        "",
        extra_msg,
        "",
        footer,
        "",
        "👍 Let us know you're coming!"
    ])
else:
    social_intro = "🗓️ THIS WEEK’S RUN!"
    routes = []
    if route_8k_name and link_8k:
        routes.append(f"➡️ 8k – {route_8k_name}: {link_8k}\n   {desc_8k}")
    if route_5k_name and link_5k:
        routes.append(f"➡️ 5k – {route_5k_name}: {link_5k} (or Jeff it!)\n   {desc_5k}")
    facebook_msg = "\n".join([
        social_intro,
        tour_msg,
        f"📍 WHERE: {meeting_point}",
        gmaps_line,
        "🕖 WHEN: We set off at 7:00pm",
        "",
        "🛣️ ROUTES:",
        *routes,
        "",
        extra_msg,
        "",
        footer,
        "",
        "🎉 Let us know if you're coming!"
    ])

# WhatsApp message
whatsapp_msg = "\n".join([
    "*RunTogether Radcliffe – This Thursday!*",
    tour_msg,
    location,
    gmaps_line,
    time,
    "",
    route_section,
    "",
    extra_msg,
    "",
    footer,
    "",
    signoff
])

# Display outputs
st.markdown("### 📧 Email Message")
st.code(email_msg, language="text")

st.markdown("### 📱 Facebook / Instagram Post")
st.code(facebook_msg, language="text")

st.markdown("### 💬 WhatsApp Message")
st.code(whatsapp_msg, language="text")

# WhatsApp share link
st.markdown("### 🔗 Share to WhatsApp")
encoded_message = urllib.parse.quote(whatsapp_msg)
share_url = f"https://wa.me/?text={encoded_message}"
st.markdown(f"[Click here to share this message on WhatsApp]({share_url})", unsafe_allow_html=True)
