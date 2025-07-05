
import streamlit as st
import pandas as pd

st.set_page_config(page_title="RunTogether Radcliffe – Weekly Run Generator", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_excel("RTR route schedule.xlsx", engine="openpyxl")
    df.columns = df.columns.str.strip()
    df = df.loc[:, ~pd.Series(df.columns).duplicated()]
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.dropna(subset=["Date"])
    return df

df = load_data()

# Sidebar preview
with st.sidebar:
    st.subheader("📅 Preview of schedule data:")
    preview_columns = st.multiselect(
        "Select columns to preview",
        options=list(df.columns),
        default=["Week", "Date", "Special events", "Notes", "Meeting point", "Meeting point google link", "8k Route", "8k Strava link", "5k Route", "5k Strava link"],
    )
    st.dataframe(df[preview_columns].copy().assign(Date=df["Date"].dt.strftime("%Y-%m-%d")))

# Main app layout
st.title("🏃‍♀️ RunTogether Radcliffe – Weekly Run Generator")

# Only show the cleaned preview once
st.markdown("### 📅 Preview of schedule data:")
st.dataframe(df[preview_columns].copy().assign(Date=df["Date"].dt.strftime("%Y-%m-%d")))

# Run date selector
upcoming_dates = df["Date"].dt.strftime("%Y-%m-%d").unique()
selected_date = st.selectbox("Select run date:", options=upcoming_dates)

# Facebook tone toggle
tone = st.radio("Choose Facebook tone", ["Professional", "Social"], horizontal=True)

# Placeholder for messages (to be filled in by working code downstream)
try:
    st.subheader("📧 Email Message")
    st.text_area("Email message", "Message generation logic goes here...", height=300)

    st.subheader("📘 Facebook Message")
    st.text_area("Facebook message", "Message generation logic goes here...", height=300)

    st.subheader("💬 WhatsApp Message")
    st.text_area("WhatsApp message", "Message generation logic goes here...", height=300)

except Exception as e:
    st.error(f"❌ An error occurred: {e}")
