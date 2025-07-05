
import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="RunTogether Radcliffe – Weekly Run Generator", layout="wide")

# Load the data
@st.cache_data
def load_data():
    df = pd.read_excel("RTR route schedule.xlsx")
    df.columns = df.columns.str.strip()
    df = df.loc[:, ~pd.Series(df.columns).duplicated()]
    df["Date"] = pd.to_datetime(df["Date"]).dt.date
    return df

df = load_data()

# Show cleaned preview (no sidebar, no column selector)
st.markdown("### 🗓️ Preview of schedule data:")
st.dataframe(df)

# Example dropdown (functionality preserved)
st.markdown("### Select run date:")
run_date = st.selectbox("Run date", options=df["Date"].dropna().unique())

# Placeholder message section
st.markdown("### 📬 Weekly Messages")
st.info("Messages will be generated here.")
