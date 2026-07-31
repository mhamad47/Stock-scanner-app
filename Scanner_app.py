

US Stock Multi-Filter Scanner - Streamlit Web App
Run with: streamlit run scanner_app.py


import streamlit as st 
import yfinance as yf 
import pandas as pd 
import numpy as np 
from datetime import datetime, timedelta 
import requests 
import io 
import warnings 
warnings.filterwarnings('ignore')


PAGE CONFIGURATION

st.set_page_config( 
page_title="Stock Scanner Pro", 
page_icon="📊", 
layout="wide", 
initial_sidebar_state="expanded" 
)

Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .filter-section {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .filter-header {
        font-size: 1.2rem;
        font-weight: bold;
        color: #2c3e50;
        margin-bottom: 0.5rem;
    }
    .stCheckbox {
        margin-top: 0.5rem;
    }
    .stButton button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
        font-size: 1.2rem;
        font-weight: bold;
        padding: 0.5rem;
        border-radius: 5px;
    }
    .stButton button:hover {
        background-color: #2c8cbe;
    }
    .metric-card {
        background-color: white;
        padding: 1rem;
        border-radius: 5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>

""", unsafe_allow_html=True)


SIDEBAR - FILTER CONFIGURATION

st.sidebar.markdown("<h1 style='text-align: center; color: #1f77b4;'>⚙️ FILTERS</h1>", unsafe_allow_html=True)

 GENERAL SETTINGS 
st.sidebar.markdown("### 📅 Time Period") 
lookback_years = st.sidebar.number_input("Years to scan", min_value=1, max_value=20, value=10, step=1) 
lookback_months = st.sidebar.number_input("Additional months", min_value=0, max_value=11, value=0, step=1)

 PRICE FILTER 
st.sidebar.markdown("---") 
st.sidebar.markdown("### 💰 Price Filter") 
price_enabled = st.sidebar.checkbox("Enable Price Filter", value=True) 
if price_enabled: 
col1, col2 = st.sidebar.columns(2) 
with col1: 
min_price = st.number_input("Min Price ($)", min_value=1.0, max_value=1000.0, value=5.0, step=0.5) 
with col2: 
max_price = st.number_input("Max Price ($)", min_value=1.0, max_value=10000.0, value=500.0, step=5.0)

 VOLUME FILTER 
st.sidebar.markdown("---") 
st.sidebar.markdown("### 📈 Volume Filter") 
volume_enabled = st.sidebar.checkbox("Enable Volume Filter", value=True) 
if volume_enabled: 
min_volume = st.number_input("Min Daily $ Volume", min_value=100000, max_value=50000000, value=1000000, step=100000, format="%d") 
volume_days = st.number_input("Volume Lookback Days", min_value=5, max_value=90, value=30, step=5)

 ADR FILTER 
st.sidebar.markdown("---") 
st.sidebar.markdown("### 📊 ADR Filter") 
adr_enabled = st.sidebar.checkbox("Enable ADR Filter", value=False) 
if adr_enabled: 
col1, col2 = st.sidebar.columns(2) 
with col1: 
min_adr = st.number_input("Min ADR %", min_value=1.0, max_value=50.0, value=3.0, step=0.5) 
with col2: 
max_adr = st.number_input("Max ADR %", min_value=1.0, max_value=100.0, value=15.0, step=1.0) 
adr_days = st.number_input("ADR Lookback Days", min_value=5, max_value=50, value=20, step=5)

 MARKET CAP FILTER 
st.sidebar.markdown("---") 
st.sidebar.markdown("### 🏢 Market Cap Filter") 
mcap_enabled = st.sidebar.checkbox("Enable Market Cap Filter", value=False) 
if mcap_enabled: 
col1, col2 = st.sidebar.columns(2) 
with col1: 
min_mcap = st.number_input("Min Market Cap ($B)", min_value=0.1, max_value=1000.0, value=1.0, step=0.1) 
with col2: 
max_mcap = st.number_input("Max Market Cap ($B)", min_value=0.1, max_value=5000.0, value=100.0, step=1.0)

 GAP UP FILTER 
st.sidebar.markdown("---") 
st.sidebar.markdown("### 🚀 Gap Up Filter") 
gap_enabled = st.sidebar.checkbox("Enable Gap Filter", value=True) 
if gap_enabled: 
col1, col2 = st.sidebar.columns(2) 
with col1: 
min_gap = st.number_input("Min Gap %", min_value=1.0, max_value=100.0, value=10.0, step=1.0) 
with col2: 
gap_volume_mult = st.number_input("Volume Multiplier", min_value=1.0, max_value=20.0, value=1.5, step=0.1) 
gap_volume_days = st.number_input("Volume Lookback Days", min_value=5, max_value=60, value=21, step=1)

 MA FILTER 
st.sidebar.markdown("---") 
st.sidebar.markdown("### 📉 Moving Average Filter") 
ma_enabled = st.sidebar.checkbox("Enable MA Filter", value=False) 
if ma_enabled: 
ma_period = st.selectbox("MA Period", options=[20, 30, 50, 100, 200], index=2) 
ma_position = st.radio("Price position", options=["above", "below"], index=0)

 MOMENTUM FILTER 
st.sidebar.markdown("---") 
st.sidebar.markdown("### ⚡ Momentum Filter") 
momentum_enabled = st.sidebar.checkbox("Enable Momentum Filter", value=True) 
if momentum_enabled: 
col1, col2 = st.sidebar.columns(2) 
with col1: 
min_move = st.number_input("Min Move %", min_value=5.0, max_value=500.0, value=50.0, step=5.0) 
with col2: 
max_move = st.number_input("Max Move %", min_value=10.0, max_value=1000.0, value=200.0, step=10.0) 
move_days = st.number_input("Move Days", min_value=5, max_value=90, value=22, step=1)

 EARNINGS FILTER 
st.sidebar.markdown("---") 
st.sidebar.markdown("### 📅 Earnings Filter") 
earnings_enabled = st.sidebar.checkbox("Enable Earnings Filter", value=False) 
if earnings_enabled: 
earnings_window = st.selectbox("Window", options=[("Earnings Day", 0), ("+1 Day", 1), ("+2 Days", 2)], format_func=lambda x: x[0])[1]

 SCAN BUTTON 
st.sidebar.markdown("---") 
scan_button = st.sidebar.button("🔍 START SCAN", use_container_width=True)


MAIN CONTENT

st.markdown("<h1 class='main-header'>📊 US Stock Scanner Pro</h1>", unsafe_allow_html=True)

Display active filters summary
st.markdown("### 🔍 Active Filters") 
cols = st.columns(4) 
filter_count = 0

if price_enabled: 
cols[filter_count % 4].markdown(f"✅ Price: ${min_price} - ${max_price}") 
filter_count += 1 
if volume_enabled: 
cols[filter_count % 4].markdown(f"✅ Volume: ${min_volume:,}+ ({volume_days}d avg)") 
filter_count += 1 
if adr_enabled: 
cols[filter_count % 4].markdown(f"✅ ADR: {min_adr}% - {max_adr}%") 
filter_count += 1 
if mcap_enabled: 
cols[filter_count % 4].markdown(f"✅ Market Cap: ${min_mcap}B - ${max_mcap}B") 
filter_count += 1 
if gap_enabled: 
cols[filter_count % 4].markdown(f"✅ Gap: {min_gap}%+ ({gap_volume_mult}x volume)") 
filter_count += 1 
if ma_enabled: 
cols[filter_count % 4].markdown(f"✅ MA: Price {ma_position.upper()} {ma_period}-day SMA") 
filter_count += 1 
if momentum_enabled: 
cols[filter_count % 4].markdown(f"✅ Momentum: {min_move}%+ in {move_days} days") 
filter_count += 1 
if earnings_enabled: 
cols[filter_count % 4].markdown(f"✅ Earnings: On earnings day + {earnings_window} days") 
filter_count += 1

if filter_count  0: 
st.warning("⚠️ No filters enabled! Please enable at least one filter.")

st.markdown("---")


SCAN FUNCTION

@st.cache_data(ttl=3600) 
def get_tickers(): 
"""Get NASDAQ ticker list""" 
try: 
url = "https://www.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt" 
response = requests.get(url) 
data = io.StringIO(response.text) 
df_nasdaq = pd.read_csv(data, sep='|') 
tickers = df_nasdaq[df_nasdaq['Test Issue']  'N']['Symbol'].tolist()

    # Clean tickers
    tickers = [str(t) for t in tickers if pd.notna(t) and str(t).strip() != '']
    exclude_patterns = ['^', '$', '.', 'W', 'R', 'Z']
    tickers = [t for t in tickers if not any(p in t for p in exclude_patterns) and len(t) <= 4]
    return tickers
except:
    return []
def scan_stock(ticker, filters): 
"""Scan individual stock""" 
try: 
lookback_days = filters['lookback_days'] 
end_date = datetime.now() 
start_date = end_date - timedelta(days=lookback_days)

    stock = yf.Ticker(ticker)
    df = stock.history(start=start_date, end=end_date)
    
    if len(df) < 252:
        return None
    
    current_price = df['Close'].iloc[-1]
    
    # Price filter
    if filters['price_enabled']:
        if current_price < filters['min_price']:
            return None
        if current_price > filters['max_price']:
            return None
    
    # Volume filter
    if filters['volume_enabled']:
        df['Dollar_Volume'] = df['Close'] * df['Volume']
        avg_vol = df['Dollar_Volume'].tail(filters['volume_days']).mean()
        if avg_vol < filters['min_volume']:
            return None
    
    # ADR filter
    if filters['adr_enabled']:
        df['Daily_Range'] = ((df['High'] - df['Low']) / df['Low']) * 100
        adr = df['Daily_Range'].tail(filters['adr_days']).mean()
        if adr < filters['min_adr'] or adr > filters['max_adr']:
            return None
    
    # Market Cap filter
    if filters['mcap_enabled']:
        info = yf.Ticker(ticker).info
        mcap = info.get('marketCap', None)
        if mcap is None or mcap < filters['min_mcap'] or mcap > filters['max_mcap']:
            return None
    
    # Calculate indicators
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    df['SMA_200'] = df['Close'].rolling(window=200).mean()
    df['Previous_Close'] = df['Close'].shift(1)
    df['Gap_Pct'] = ((df['Open'] - df['Previous_Close']) / df['Previous_Close']) * 100
    df['Volume_SMA'] = df['Volume'].rolling(window=filters['gap_volume_days']).mean()
    df['Volume_Ratio'] = df['Volume'] / df['Volume_SMA']
    df['Price_Move'] = ((df['Close'] - df['Close'].shift(filters['move_days'])) / df['Close'].shift(filters['move_days'])) * 100
    
    # Gap filter
    gap_dates = []
    if filters['gap_enabled']:
        gap_condition = (df['Gap_Pct'] >= filters['min_gap']) & (df['Volume_Ratio'] >= filters['gap_volume_mult'])
        
        if filters['earnings_enabled']:
            stock_obj = yf.Ticker(ticker)
            earnings = stock_obj.earnings_dates
            if earnings is not None and len(earnings) > 0:
                earnings_dates = earnings.index.tolist()
                earnings_set = set()
                for date in earnings_dates:
                    earnings_set.add(date.strftime('%Y-%m-%d'))
                    for i in range(1, filters['earnings_window'] + 1):
                        earnings_set.add((date + timedelta(days=i)).strftime('%Y-%m-%d'))
                df['Is_Earnings'] = df.index.strftime('%Y-%m-%d').isin(earnings_set)
                gap_condition = gap_condition & (df['Is_Earnings'] == True)
        
        gap_dates = df[gap_condition].index.tolist()
    
    # MA filter
    if filters['ma_enabled']:
        ma_col = f'SMA_{filters["ma_period"]}'
        if filters['ma_period'] not in [50, 200]:
            df[f'SMA_{filters["ma_period"]}'] = df['Close'].rolling(window=filters['ma_period']).mean()
            ma_col = f'SMA_{filters["ma_period"]}'
        
        if filters['ma_position'] == 'above':
            if current_price <= df[ma_col].iloc[-1]:
                return None
        else:
            if current_price >= df[ma_col].iloc[-1]:
                return None
    
    # Momentum filter
    move_dates = []
    if filters['momentum_enabled']:
        move_condition = (df['Price_Move'] >= filters['min_move'])
        if filters['max_move']:
            move_condition = move_condition & (df['Price_Move'] <= filters['max_move'])
        move_dates = df[move_condition].index.tolist()
    
    # Check results
    if filters['gap_enabled'] and filters['momentum_enabled']:
        if len(gap_dates) == 0 and len(move_dates) == 0:
            return None
    elif filters['gap_enabled'] and len(gap_dates) == 0:
        return None
    elif filters['momentum_enabled'] and len(move_dates) == 0:
        return None
    
    return {
        'Ticker': ticker,
        'Current_Price': round(current_price, 2),
        'Gap_Count': len(gap_dates) if filters['gap_enabled'] else None,
        'Max_Gap_%': round(df.loc[gap_dates, 'Gap_Pct'].max(), 2) if gap_dates else None,
        'Move_Count': len(move_dates) if filters['momentum_enabled'] else None,
        'Max_Move_%': round(df.loc[move_dates, 'Price_Move'].max(), 2) if move_dates else None,
        'Current_Move_%': round(df['Price_Move'].iloc[-1], 2) if filters['momentum_enabled'] else None,
    }
except:
    return None

EXECUTE SCAN

if scan_button: 
# Get tickers 
with st.spinner("Loading NASDAQ ticker list..."): 
tickers = get_tickers()

if not tickers:
    st.error("Failed to load ticker list. Please try again.")
else:
    # Prepare filters
    filters = {
        'lookback_days': (lookback_years * 365) + (lookback_months * 30),
        'price_enabled': price_enabled,
        'min_price': min_price if price_enabled else 0,
        'max_price': max_price if price_enabled else float('inf'),
        'volume_enabled': volume_enabled,
        'min_volume': min_volume if volume_enabled else 0,
        'volume_days': volume_days if volume_enabled else 30,
        'adr_enabled': adr_enabled,
        'min_adr': min_adr if adr_enabled else 0,
        'max_adr': max_adr if adr_enabled else float('inf'),
        'adr_days': adr_days if adr_enabled else 20,
        'mcap_enabled': mcap_enabled,
        'min_mcap': min_mcap * 1e9 if mcap_enabled else 0,
        'max_mcap': max_mcap * 1e9 if mcap_enabled else float('inf'),
        'gap_enabled': gap_enabled,
        'min_gap': min_gap if gap_enabled else 0,
        'gap_volume_mult': gap_volume_mult if gap_enabled else 1.0,
        'gap_volume_days': gap_volume_days if gap_enabled else 21,
        'ma_enabled': ma_enabled,
        'ma_period': ma_period if ma_enabled else 50,
        'ma_position': ma_position if ma_enabled else 'above',
        'momentum_enabled': momentum_enabled,
        'min_move': min_move if momentum_enabled else 0,
        'max_move': max_move if momentum_enabled else float('inf'),
        'move_days': move_days if momentum_enabled else 22,
        'earnings_enabled': earnings_enabled,
        'earnings_window': earnings_window if earnings_enabled else 0,
    }
    
    # Progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Scan stocks
    results = []
    total_stocks = len(tickers)
    
    for i, ticker in enumerate(tickers):
        if i % 50 == 0:
            status_text.text(f"Scanning {i}/{total_stocks} stocks...")
            progress_bar.progress(i / total_stocks)
        
        result = scan_stock(ticker, filters)
        if result:
            results.append(result)
    
    progress_bar.progress(1.0)
    status_text.text("Scan complete!")
    
    # Display results
    if results:
        df_results = pd.DataFrame(results)
        
        # Sort
        if gap_enabled:
            df_results = df_results.sort_values('Max_Gap_%', ascending=False)
        elif momentum_enabled:
            df_results = df_results.sort_values('Max_Move_%', ascending=False)
        
        st.markdown("---")
        st.markdown(f"## ✅ Found {len(results)} Stocks Matching Your Filters")
        
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Scanned", total_stocks)
        with col2:
            st.metric("Matches Found", len(results))
        with col3:
            st.metric("Success Rate", f"{len(results)/total_stocks*100:.2f}%")
        with col4:
            if gap_enabled and len(results) > 0:
                st.metric("Avg Max Gap", f"{df_results['Max_Gap_%'].mean():.2f}%")
            elif momentum_enabled and len(results) > 0:
                st.metric("Avg Max Move", f"{df_results['Max_Move_%'].mean():.2f}%")
        
        # Display table
        display_cols = ['Ticker', 'Current_Price']
        if gap_enabled:
            display_cols.extend(['Gap_Count', 'Max_Gap_%'])
        if momentum_enabled:
            display_cols.extend(['Move_Count', 'Max_Move_%', 'Current_Move_%'])
        
        st.dataframe(df_results[display_cols], use_container_width=True)
        
        # Export button
        csv = df_results.to_csv(index=False)
        st.download_button(
            label="📥 Download Results as CSV",
            data=csv,
            file_name=f"scanner_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    else:
        st.warning("No stocks found matching your criteria. Try adjusting the filters.")

FOOTER

st.markdown("---") 
st.markdown("💡 Tips: Adjust filters in the sidebar and click 'START SCAN' to run.")
