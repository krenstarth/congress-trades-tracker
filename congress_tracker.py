import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import yfinance as yf

st.set_page_config(page_title="Congress Trades Tracker", page_icon="🏛️", layout="wide")

st.title("🏛️ Congressional Stock Trades Tracker")
st.markdown("Live data from public disclosures • Free & open tool")

# Sidebar
st.sidebar.header("Configuration")
api_key = st.sidebar.text_input("RapidAPI Key", type="password", 
                                help="Paste your key from RapidAPI")

@st.cache_data(ttl=1800)
def fetch_latest_trades(api_key, limit=100):
    if not api_key:
        return pd.DataFrame()
    
    url = "https://politician-trade-tracker1.p.rapidapi.com/api/trades/latest"
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "politician-trade-tracker1.p.rapidapi.com"
    }
    params = {"limit": limit}
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=20)
        response.raise_for_status()
        data = response.json()
        
        if isinstance(data, list):
            df = pd.DataFrame(data)
        else:
            df = pd.DataFrame(data.get('trades', []) if isinstance(data, dict) else [])
        
        return df
    except Exception as e:
        st.error(f"API Error: {str(e)}")
        return pd.DataFrame()

df = fetch_latest_trades(api_key)

# Display
if not df.empty:
    st.success(f"✅ Loaded {len(df)} recent trades!")
    
    # Clean column names
    df.columns = [col.replace('_', ' ').title() for col in df.columns]
    
    st.subheader("Recent Trades")
    st.dataframe(df.head(50), use_container_width=True, hide_index=True)
    
    # Charts
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Top Politicians")
        fig = px.bar(df['Politician'].value_counts().head(10))
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.subheader("Top Tickers")
        fig2 = px.pie(df['Ticker'].value_counts().head(8), 
                      names=df['Ticker'].value_counts().head(8).index)
        st.plotly_chart(fig2, use_container_width=True)
else:
    st.info("Enter your RapidAPI key in the sidebar to load live data.")

# Stock Chart
st.subheader("Quick Stock Performance Check")
ticker = st.text_input("Ticker", value="NVDA")
if st.button("Show Chart"):
    try:
        data = yf.download(ticker, period="6mo")
        st.line_chart(data['Close'])
    except:
        st.error("Could not load chart")
