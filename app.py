
import streamlit as st
import pandas as pd

st.set_page_config(page_title="RunTogether Radcliffe – Weekly Run Generator", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_excel("RTR route schedule.xlsx")
    df.columns = df.columns.str.strip()
    df = df.loc[:, ~df.columns.duplicated()]  # Safer duplicate removal
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date']).dt.date
    return df

df = load_data()

# App title
st.markdown("## 🗓️ Preview of schedule data:")
st.dataframe(df[['Week', 'Date', 'Special events', 'Notes', 'Meeting point',
                 'Meeting point google link', '8k Route', '8k Strava link',
                 '5k Route', '5k Strava link']])
