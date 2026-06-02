import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import yfinance as yf

st.set_page_config(page_title="Congress Trades Tracker", page_icon="🏛️", layout="wide")

st.title("🏛️ Congressional Stock Trades Tracker")
st.markdown("Live data from public disclosures")

# Sidebar
st.sidebar.header("Configuration")
api_key = st.sidebar.text_input("RapidAPI Key", type="password", 
                                help="Paste your key from RapidAPI")

@st.cache_data(ttl=3600)
def fetch_politicians(api_key):
    if not api_key:
        return pd.DataFrame()
    
    url = "https://politician-trade-tracker1.p.rapidapi.com/get_politicians"
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "politician-trade-tracker1.p.rapidapi.com"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        # Convert to DataFrame
        if isinstance(data, dict):
            df = pd.DataFrame([{"Politician": k, **v} for k, v in data.items()])
        else:
            df = pd.DataFrame(data)
        return df
    except Exception as e:
        st.error(f"API Error: {str(e)}")
        return pd.DataFrame()

df = fetch_politicians(api_key)

if not df.empty:
    st.success(f"Loaded {len(df)} politicians!")
    st.dataframe(df.head(20), use_container_width=True)
    
    # Simple charts
    if 'Party' in df.columns:
        fig = px.pie(df, names='Party', title="Politicians by Party")
        st.plotly_chart(fig)
else:
    st.info("Enter your RapidAPI key above to load data.")

# Quick stock chart (works without API)
st.subheader("Quick Stock Check")
ticker = st.text_input("Enter Ticker", value="NVDA")
if st.button("Show Chart"):
    try:
        data = yf.download(ticker, period="6mo")
        st.line_chart(data['Close'])
    except:
        st.error("Could not load chart")
