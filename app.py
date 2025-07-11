import streamlit as st
import pandas as pd
import os
import sys

print("🔍 Current working directory:", os.getcwd())
print("📦 Python sys.path:", sys.path)

try:
    from route_summary_geocoding import generate_route_summary
    print("✅ Successfully imported generate_route_summary")
except ImportError as e:
    print("❌ Failed to import generate_route_summary:", e)
    raise

from strava_utils import get_strava_access_token

@st.cache_data
def load_data():
    df = pd.read_excel("RTR route schedule.xlsx")
    df = df[df["5k Strava link"].notnull() | df["8k Strava link"].notnull()]
    return df

st.title("🏃 Weekly Run Announcement Generator")

df = load_data()
access_token = get_strava_access_token()

output_lines = []

for _, row in df.iterrows():
    messages = []
    if pd.notna(row.get("8k Strava link")):
        name = row.get("8k Route", "8k route")
        url = row["8k Strava link"]
        note = row.get("Notes", "")
        summary = generate_route_summary(url, access_token)
        line = f"• 8k – {name}: {url}"
        if note:
            line += f" ({note})"
        messages.append(f"{line}
  {summary}")

    if pd.notna(row.get("5k Strava link")):
        name = row.get("5k Route", "5k route")
        url = row["5k Strava link"]
        note = row.get("Notes", "")
        summary = generate_route_summary(url, access_token)
        line = f"• 5k – {name}: {url}"
        if note:
            line += f" ({note})"
        messages.append(f"{line}
  {summary}")

    if messages:
        output_lines.append("🛣️ This week we’ve got two route options to choose from:
" + "
".join(messages))

st.text_area("📣 Weekly Announcement", value="\n\n".join(output_lines), height=500)
