import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from datetime import datetime
import yfinance as yf

st.set_page_config(page_title="Congress Trades Tracker", page_icon="🏛️", layout="wide")

st.title("🏛️ Congressional Stock Trades Tracker")
st.markdown("Live data from public disclosures • Free & open tool")

# ------------------- Sidebar -------------------
st.sidebar.header("Configuration")

api_key = st.sidebar.text_input(
    "RapidAPI Key (Politician Trade Tracker)", 
    type="password",
    help="Get free key at: https://rapidapi.com/s5yux/api/politician-trade-tracker1"
)

@st.cache_data(ttl=1800)  # Cache 30 minutes
def fetch_congress_trades(api_key, limit=50):
    if not api_key:
        return pd.DataFrame()
    
    url = "https://politician-trade-tracker1.p.rapidapi.com/api/trades/latest"
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "politician-trade-tracker1.p.rapidapi.com"
    }
    params = {"limit": limit}
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        if isinstance(data, list):
            df = pd.DataFrame(data)
        else:
            df = pd.DataFrame(data.get('trades', []) if isinstance(data, dict) else [])
            
        if not df.empty and 'trade_date' in df.columns:
            df['Trade_Date'] = pd.to_datetime(df['trade_date'], errors='coerce')
        return df
    except Exception as e:
        st.error(f"API Error: {str(e)}")
        return pd.DataFrame()

df = fetch_congress_trades(api_key)

# ------------------- Filters & Display -------------------
if not df.empty:
    # Rename columns to be more user-friendly if needed
    df = df.rename(columns=lambda x: x.replace('_', ' ').title())
    
    politicians = ['All'] + sorted(df.get('Politician', pd.Series()).unique())
    selected_pol = st.sidebar.selectbox("Politician", politicians)
    
    tickers = ['All'] + sorted(df.get('Ticker', pd.Series()).dropna().unique())
    selected_ticker = st.sidebar.selectbox("Ticker", tickers)

    # Apply filters
    filtered_df = df.copy()
    if selected_pol != 'All':
        filtered_df = filtered_df[filtered_df.get('Politician', '') == selected_pol]
    if selected_ticker != 'All':
        filtered_df = filtered_df[filtered_df.get('Ticker', '') == selected_ticker]

    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Total Trades", len(filtered_df))
    with col2: st.metric("Politicians", filtered_df.get('Politician', pd.Series()).nunique())
    with col3: st.metric("Buys", len(filtered_df[filtered_df.get('Transaction', '').str.contains("Buy|Purchase", na=False)]))
    with col4: st.metric("Sells", len(filtered_df[filtered_df.get('Transaction', '').str.contains("Sell|Sale", na=False)]))

    st.subheader("Recent Trades")
    st.dataframe(filtered_df.sort_values('Trade_Date', ascending=False) if 'Trade_Date' in filtered_df.columns else filtered_df, 
                 use_container_width=True, hide_index=True)

    # Charts
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Trades by Politician")
        fig = px.bar(filtered_df['Politician'].value_counts().head(10))
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.subheader("Trades by Ticker")
        fig2 = px.pie(filtered_df['Ticker'].value_counts().head(8), names=filtered_df['Ticker'].value_counts().head(8).index)
        st.plotly_chart(fig2, use_container_width=True)

else:
    st.info("Enter your RapidAPI key in the sidebar to load live data.")

# Quick Stock Chart
st.subheader("Quick Stock Performance Check")
ticker = st.text_input("Ticker", value="NVDA")
if st.button("Show Chart"):
    try:
        data = yf.download(ticker, period="6mo")
        if not data.empty:
            st.line_chart(data['Close'])
        else:
            st.error("No data found for ticker")
    except:
        st.error("Could not load chart")

st.caption("Data via Politician Trade Tracker API • Built for Ralph")
