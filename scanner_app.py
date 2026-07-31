# ============================================
# US Stock Multi-Filter Scanner - Streamlit Web App
# Run with: streamlit run scanner_app.py
# ============================================

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
import io
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(
    page_title="Stock Scanner Pro",
    page_icon="📊",
    layout="wide"
)

st.title("📊 US Stock Scanner Pro")

# Sidebar filters
st.sidebar.header("⚙️ Filters")

# Time period
lookback_years = st.sidebar.number_input("Years to scan", min_value=1, max_value=20, value=10)
lookback_months = st.sidebar.number_input("Additional months", min_value=0, max_value=11, value=0)

# Price filter
price_enabled = st.sidebar.checkbox("Enable Price Filter", value=True)
if price_enabled:
    min_price = st.sidebar.number_input("Min Price ($)", min_value=1.0, value=5.0)
    max_price = st.sidebar.number_input("Max Price ($)", min_value=1.0, value=500.0)

# Volume filter
volume_enabled = st.sidebar.checkbox("Enable Volume Filter", value=True)
if volume_enabled:
    min_volume = st.sidebar.number_input("Min Daily $ Volume", min_value=100000, value=1000000)
    volume_days = st.sidebar.number_input("Volume Lookback Days", min_value=5, max_value=90, value=30)

# Gap filter
gap_enabled = st.sidebar.checkbox("Enable Gap Filter", value=True)
if gap_enabled:
    min_gap = st.sidebar.number_input("Min Gap %", min_value=1.0, value=10.0)
    gap_volume_mult = st.sidebar.number_input("Volume Multiplier", min_value=1.0, value=1.5)

# Momentum filter
momentum_enabled = st.sidebar.checkbox("Enable Momentum Filter", value=True)
if momentum_enabled:
    min_move = st.sidebar.number_input("Min Move %", min_value=5.0, value=50.0)
    move_days = st.sidebar.number_input("Move Days", min_value=5, max_value=90, value=22)

# Scan button
scan_button = st.sidebar.button("🔍 START SCAN", use_container_width=True)

# Main content
if scan_button:
    with st.spinner("Loading NASDAQ tickers..."):
        try:
            url = "https://www.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt"
            response = requests.get(url)
            data = io.StringIO(response.text)
            df_nasdaq = pd.read_csv(data, sep='|')
            tickers = df_nasdaq[df_nasdaq['Test Issue'] == 'N']['Symbol'].tolist()
            tickers = [str(t) for t in tickers if pd.notna(t)]
            tickers = [t for t in tickers if len(t) <= 4]
            st.info(f"Found {len(tickers)} NASDAQ stocks to scan")
        except Exception as e:
            st.error(f"Error loading tickers: {e}")
            tickers = []
    
    if tickers:
        progress_bar = st.progress(0)
        status_text = st.empty()
        results = []
        
        # Calculate lookback days
        lookback_days = (lookback_years * 365) + (lookback_months * 30)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=lookback_days)
        
        for i, ticker in enumerate(tickers[:50]):  # Limited to 50 for testing
            try:
                status_text.text(f"Scanning {i+1}/{len(tickers[:50])}: {ticker}")
                progress_bar.progress((i+1)/len(tickers[:50]))
                
                stock = yf.Ticker(ticker)
                df = stock.history(start=start_date, end=end_date)
                
                if len(df) < 252:
                    continue
                
                current_price = df['Close'].iloc[-1]
                
                # Price filter
                if price_enabled and (current_price < min_price or current_price > max_price):
                    continue
                
                # Volume filter
                if volume_enabled:
                    df['Dollar_Volume'] = df['Close'] * df['Volume']
                    avg_vol = df['Dollar_Volume'].tail(volume_days).mean()
                    if avg_vol < min_volume:
                        continue
                
                # Calculate indicators
                df['Previous_Close'] = df['Close'].shift(1)
                df['Gap_Pct'] = ((df['Open'] - df['Previous_Close']) / df['Previous_Close']) * 100
                df['Volume_SMA'] = df['Volume'].rolling(window=21).mean()
                df['Volume_Ratio'] = df['Volume'] / df['Volume_SMA']
                df['Price_Move'] = ((df['Close'] - df['Close'].shift(move_days)) / df['Close'].shift(move_days)) * 100
                
                # Gap filter
                gap_match = False
                if gap_enabled:
                    gap_condition = (df['Gap_Pct'] >= min_gap) & (df['Volume_Ratio'] >= gap_volume_mult)
                    gap_matches = df[gap_condition]
                    if len(gap_matches) > 0:
                        gap_match = True
                
                # Momentum filter
                momentum_match = False
                if momentum_enabled:
                    move_condition = (df['Price_Move'] >= min_move)
                    move_matches = df[move_condition]
                    if len(move_matches) > 0:
                        momentum_match = True
                
                # Check if stock matches any filter
                if gap_match or momentum_match:
                    result = {
                        'Ticker': ticker,
                        'Current_Price': round(current_price, 2),
                        'Gap_Match': 'Yes' if gap_match else 'No',
                        'Momentum_Match': 'Yes' if momentum_match else 'No',
                    }
                    results.append(result)
                    
            except Exception as e:
                continue
        
        progress_bar.progress(1.0)
        status_text.text("Scan complete!")
        
        if results:
            df_results = pd.DataFrame(results)
            st.success(f"✅ Found {len(results)} stocks matching your filters!")
            st.dataframe(df_results, use_container_width=True)
            
            csv = df_results.to_csv(index=False)
            st.download_button(
                label="📥 Download Results",
                data=csv,
                file_name="scanner_results.csv",
                mime="text/csv"
            )
        else:
            st.warning("No stocks found matching your criteria. Try adjusting filters.")
