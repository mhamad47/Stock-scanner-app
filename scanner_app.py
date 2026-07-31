import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
import io
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="Stock Scanner", layout="wide")

st.title("📊 Stock Scanner")

# --- Sidebar Filters ---
st.sidebar.header("Filters")

lookback_years = st.sidebar.number_input("Years", min_value=1, value=10)
min_price = st.sidebar.number_input("Min Price", min_value=1.0, value=5.0)
min_volume = st.sidebar.number_input("Min Daily Volume ($)", min_value=100000, value=1000000, step=100000)
min_gap = st.sidebar.number_input("Min Gap %", min_value=1.0, value=10.0)
min_move = st.sidebar.number_input("Min Move %", min_value=5.0, value=50.0)

scan_button = st.sidebar.button("Start Scan")

# --- Scan Function ---
if scan_button:
    try:
        # Get tickers
        url = "https://www.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt"
        response = requests.get(url)
        data = io.StringIO(response.text)
        df_nasdaq = pd.read_csv(data, sep='|')
        tickers = df_nasdaq[df_nasdaq['Test Issue'] == 'N']['Symbol'].tolist()
        tickers = [str(t) for t in tickers if pd.notna(t)]
        tickers = [t for t in tickers if len(t) <= 4]
        
        st.info(f"Found {len(tickers)} NASDAQ stocks")
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        results = []
        lookback_days = lookback_years * 365
        
        for i, ticker in enumerate(tickers[:20]):  # Reduced to 20 for quick testing
            try:
                status_text.text(f"Scanning {i+1}/20: {ticker}")
                progress_bar.progress((i+1)/20)
                
                stock = yf.Ticker(ticker)
                df = stock.history(period="2y")
                
                if len(df) < 100:
                    continue
                
                current_price = df['Close'].iloc[-1]
                
                if current_price < min_price:
                    continue
                
                # Calculate indicators
                df['Previous_Close'] = df['Close'].shift(1)
                df['Gap_Pct'] = ((df['Open'] - df['Previous_Close']) / df['Previous_Close']) * 100
                df['Price_Move'] = ((df['Close'] - df['Close'].shift(22)) / df['Close'].shift(22)) * 100
                
                # Check for gaps
                gap_match = False
                gap_max = 0
                
                if min_gap > 0:
                    gap_matches = df[df['Gap_Pct'] >= min_gap]
                    if len(gap_matches) > 0:
                        gap_match = True
                        gap_max = gap_matches['Gap_Pct'].max()
                
                # Check for momentum
                move_match = False
                move_max = 0
                
                if min_move > 0:
                    move_matches = df[df['Price_Move'] >= min_move]
                    if len(move_matches) > 0:
                        move_match = True
                        move_max = move_matches['Price_Move'].max()
                
                if gap_match or move_match:
                    results.append({
                        'Ticker': ticker,
                        'Price': round(current_price, 2),
                        'Gap_Match': '✅' if gap_match else '❌',
                        'Max_Gap_%': round(gap_max, 2) if gap_match else 0,
                        'Move_Match': '✅' if move_match else '❌',
                        'Max_Move_%': round(move_max, 2) if move_match else 0,
                    })
                    
            except Exception as e:
                continue
        
        progress_bar.progress(1.0)
        status_text.text("Done!")
        
        if results:
            df_results = pd.DataFrame(results)
            st.success(f"✅ Found {len(results)} stocks!")
            st.dataframe(df_results)
        else:
            st.warning("No stocks found. Try lower thresholds.")
            
    except Exception as e:
        st.error(f"Error: {str(e)}")
