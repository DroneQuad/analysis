import streamlit as st
import pandas as pd
from datetime import datetime
import io

from Analysisxls_combined import (
    fetch_market_data,
    generate_short_report,
    generate_chart_with_ema,
    generate_comment
)

st.set_page_config(page_title="Market Analysis Dashboard", layout="wide")
st.title("📈 Market Analysis Dashboard")

with st.spinner("Fetching market data..."):
    assets_data, macro_drivers = fetch_market_data()
    df = pd.DataFrame(assets_data)
    df['Komentar'] = df.apply(lambda row: generate_comment(row['symbol'], row['bias']), axis=1)

st.subheader("🔹 Ringkasan Analisa")
st.dataframe(df[['symbol', 'price', 'bias', 'Komentar']], use_container_width=True)

symbol_map = {
    "BTCUSD": "BTC-USD",
    "ETHUSD": "ETH-USD",
    "XAUUSD": "GC=F",
    "USOIL": "CL=F",
    "USTEC": "^NDX"
}

timeframes = ["5m", "15m", "1h", "4h", "1d"]

col1, col2 = st.columns(2)
with col1:
    selected = st.selectbox("📊 Pilih asset:", list(symbol_map.keys()))
with col2:
    tf = st.selectbox("⏱️ Timeframe:", timeframes)

ticker = symbol_map[selected]
chart_buf = generate_chart_with_ema(ticker, selected, tf)
if chart_buf:
    st.image(chart_buf, caption=f"{selected} {tf} Chart with EMA5/20")
else:
    st.warning("Chart tidak tersedia.")

st.markdown("---")
st.markdown("🛡️ _Data diperbarui real-time. Gunakan manajemen risiko yang bijak_.")
