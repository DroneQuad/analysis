import streamlit as st
import pandas as pd
from datetime import datetime
import io
import requests
import yfinance as yf
from streamlit_autorefresh import st_autorefresh
import streamlit.components.v1 as components

from Analysisxls_combined import (
    fetch_market_data,
    generate_short_report,
    generate_chart_with_ema,
    generate_comment,
    calculate_indicators,
    generate_entry_suggestion
)

NEWS_API_KEY = "edff44088506404b8a0dfe4adcdc451a"

def get_news(symbol, category=None):
    query_map = {
        "BTCUSD": "bitcoin",
        "ETHUSD": "ethereum",
        "XAUUSD": "gold",
        "USOIL": "oil",
        "USTEC": "nasdaq"
    }
    keyword = query_map.get(symbol, symbol)
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": keyword,
        "apiKey": NEWS_API_KEY,
        "pageSize": 5,
        "sortBy": "publishedAt",
        "language": "en"
    }
    if category and category != "All":
        params["q"] += f" {category.lower()}"
    try:
        r = requests.get(url, params=params, timeout=10)
        data = r.json()
        if data["status"] == "ok":
            return data["articles"]
    except:
        return []
    return []

def get_tradingview_embed(symbol):
    tv_map = {
        "BTCUSD": "BINANCE:BTCUSDT",
        "ETHUSD": "BINANCE:ETHUSDT",
        "XAUUSD": "OANDA:XAUUSD",
        "USOIL": "TVC:USOIL",
        "USTEC": "NASDAQ:NDX"
    }
    tv_symbol = tv_map.get(symbol, "BINANCE:BTCUSDT")
    return f"""
        <iframe src="https://s.tradingview.com/embed-widget/advanced-chart/?symbol={tv_symbol}&theme=dark&style=1&timezone=Etc/UTC&interval=60&hide_side_toolbar=false"
        width="100%" height="420" frameborder="0" allowtransparency="true" scrolling="no"></iframe>
    """

st.set_page_config(page_title="Market Analysis Dashboard", layout="wide")
st.title("📈 Market Analysis Dashboard")
st_autorefresh(interval=5000, key="refresh")

assets_data, macro_drivers = fetch_market_data()
df = pd.DataFrame(assets_data)
df['Komentar'] = df.apply(lambda row: generate_comment(row['symbol'], row['bias']), axis=1)

st.subheader("📊 Ringkasan Analisa Market")
st.dataframe(df[['symbol', 'price', 'bias', 'Komentar']], use_container_width=True)

show_only_signals = st.checkbox("🔎 Tampilkan hanya simbol dengan sinyal entry (BUY/SELL)")

# Ambil simbol yang sinyalnya bukan 'Tunggu konfirmasi arah'
def is_active_signal(symbol):
    ticker = symbol_map[symbol]
    try:
        data_raw = yf.Ticker(ticker).history(period='7d', interval='15m')
        data_ind = calculate_indicators(data_raw)
        signal_text = generate_entry_suggestion(data_ind)
        return "BUY" in signal_text or "SELL" in signal_text
    except:
        return False

if show_only_signals:
    symbol_map = {s: t for s, t in symbol_map.items() if is_active_signal(s)}


symbol_map = {
    "BTCUSD": "BTC-USD",
    "ETHUSD": "ETH-USD",
    "XAUUSD": "GC=F",
    "USOIL": "CL=F",
    "USTEC": "^NDX"
}

tabs = st.tabs(list(symbol_map.keys()))
timeframe_options = ['5m', '15m', '1h', '4h', '1d']
news_categories = ["All", "Market", "Crypto", "Commodities", "Indices"]

for i, (symbol, ticker) in enumerate(symbol_map.items()):
    with tabs[i]:
        st.header(f"📌 {symbol}")
        tf = st.selectbox("⏱️ Pilih timeframe:", timeframe_options, key=f"tf_{symbol}")
        chart_buf = generate_chart_with_ema(ticker, symbol, timeframe=tf)
        if chart_buf:
            st.image(chart_buf, caption=f"{symbol} {tf} Chart + EMA5/20")
        else:
            st.warning("Chart tidak tersedia.")

        selected_data = next((x for x in assets_data if x["symbol"] == symbol), None)
        if selected_data:
            st.markdown(f"""
            ### 📋 Analisa Lengkap {symbol}
            - **Harga**: ${selected_data['price']:,}
            - **Bias**: {selected_data['bias']}
            - **Support**: {selected_data['support']}
            - **Resistance**: {selected_data['resistance']}
            - **Volatilitas**: {selected_data['volatility']}
            - **Komentar**: {generate_comment(symbol, selected_data['bias'])}
            """)

        data_raw = yf.Ticker(ticker).history(period='7d', interval=tf)
        data_ind = calculate_indicators(data_raw)
        suggestion = generate_entry_suggestion(data_ind)
        st.markdown("### 📌 Saran Entry Otomatis")
        st.info(suggestion)

        st.markdown("### 📈 Chart Interaktif TradingView")
        components.html(get_tradingview_embed(symbol), height=430)

        st.markdown("### 📰 Berita Global Terkait")
        selected_cat = st.selectbox("🗂️ Filter kategori berita:", news_categories, key=f"news_cat_{symbol}")
        news = get_news(symbol, category=selected_cat)
        if news:
            for article in news:
                st.markdown(f"""**[{article['title']}]({article['url']})**  
_{article['source']['name']} • {article['publishedAt'][:10]}_""")
                if article['description']:
                    st.caption(article['description'])
        else:
            st.info("Tidak ada berita ditemukan.")
