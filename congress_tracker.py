import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from datetime import datetime, timedelta
import yfinance as yf

st.set_page_config(page_title="Congress Trades Tracker", page_icon="🏛️", layout="wide")

st.title("🏛️ Congressional Stock Trades Tracker")
st.markdown("Live data from public disclosures • Free & open tool")

# ------------------- Sidebar -------------------
st.sidebar.header("Configuration")

# API Key input (user adds their free key)
api_key = st.sidebar.text_input("RapidAPI Key (Politician Trade Tracker)", type="password", 
                                help="Get free key at: https://rapidapi.com/s5yux/api/politician-trade-tracker1")

@st.cache_data(ttl=1800)  # Cache for 30 minutes
def fetch_congress_trades(api_key, limit=100):
    if not api_key:
        st.warning("Enter your free API key in sidebar for live data.")
        return pd.DataFrame()  # Return empty
    
    url = "https://politician-trade-tracker1.p.rapidapi.com/get_recent_trades"  # Adjust endpoint if needed
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "politician-trade-tracker1.p.rapidapi.com"
    }
    params = {"limit": limit}
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        df = pd.DataFrame(data)
        if not df.empty:
            df['Trade_Date'] = pd.to_datetime(df['Trade_Date'], errors='coerce')
        return df
    except Exception as e:
        st.error(f"API Error: {str(e)}")
        return pd.DataFrame()

df = fetch_congress_trades(api_key)

# Filters
if not df.empty:
    politicians = ['All'] + sorted(df['Politician'].unique())
    selected_pol = st.sidebar.selectbox("Politician", politicians)
    
    tickers = ['All'] + sorted(df['Ticker'].unique())
    selected_ticker = st.sidebar.selectbox("Ticker", tickers)
    
    parties = ['All'] + sorted(df['Party'].dropna().unique())
    selected_party = st.sidebar.selectbox("Party", parties)
else:
    selected_pol = selected_ticker = selected_party = 'All'

# Apply filters
filtered_df = df.copy()
if not filtered_df.empty:
    if selected_pol != 'All':
        filtered_df = filtered_df[filtered_df['Politician'] == selected_pol]
    if selected_ticker != 'All':
        filtered_df = filtered_df[filtered_df['Ticker'] == selected_ticker]
    if selected_party != 'All':
        filtered_df = filtered_df[filtered_df['Party'] == selected_party]

# ------------------- Dashboard -------------------
if not filtered_df.empty:
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Total Trades", len(filtered_df))
    with col2: st.metric("Politicians", filtered_df['Politician'].nunique())
    with col3: st.metric("Buys", len(filtered_df[filtered_df['Transaction'].str.contains("Purchase", na=False)]))
    with col4: st.metric("Sells", len(filtered_df[filtered_df['Transaction'].str.contains("Sale", na=False)]))

    st.subheader("Recent Trades")
    st.dataframe(filtered_df.sort_values('Trade_Date', ascending=False), use_container_width=True, hide_index=True)
    
    # Export
    csv = filtered_df.to_csv(index=False)
    st.download_button("📥 Download CSV", csv, "congress_trades.csv", "text/csv")

    # Charts
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Trades by Politician")
        fig = px.bar(filtered_df['Politician'].value_counts().head(10), 
                     title="Top Active Traders")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.subheader("Trades by Ticker")
        fig2 = px.pie(filtered_df['Ticker'].value_counts().head(8), 
                      names=filtered_df['Ticker'].value_counts().head(8).index)
        st.plotly_chart(fig2, use_container_width=True)
else:
    st.info("No data loaded yet. Add your free API key above.")

# Stock Performance Tool
st.subheader("Quick Stock Performance Check")
ticker = st.text_input("Ticker", value="NVDA")
if st.button("Show Chart"):
    try:
        data = yf.download(ticker, period="6mo")
        st.line_chart(data['Close'])
    except:
        st.error("Could not load chart")

st.caption("Data via Politician Trade Tracker API • Built for Ralph")