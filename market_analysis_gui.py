import streamlit as st
import pandas as pd
from datetime import datetime
from Analysisxls_combined import fetch_market_data, generate_entry_suggestion, backtest_signals, calculate_signal_accuracy, fetch_news_links
from streamlit_autorefresh import st_autorefresh
import streamlit.components.v1 as components
import yfinance as yf
import feedparser
import joblib
import numpy as np
import os
from ta.volatility import AverageTrueRange

st.set_page_config(page_title="📈 Market Dashboard Pro", layout="wide")
st.title("📈 Market Analysis Dashboard By DroneQuad")
# # st_autorefresh(interval=5000, key="refresh_counter")  # Disabled to avoid page flicker  # Disabled full page refresh

if not os.path.exists("ai_signal_booster_model.pkl"):
    st.error("Model AI tidak ditemukan.")
    st.stop()

@st.cache_resource
def load_ai_model():
    return joblib.load("ai_signal_booster_model.pkl")

ai_model = load_ai_model()

@st.cache_data(ttl=5)
def load_price_data(ticker, tf):
    try:
        data = yf.Ticker(ticker).history(period='7d', interval=tf)
        if data.empty:
            data = yf.Ticker(ticker).history(period='7d', interval='1h')
        return data
    except:
        return pd.DataFrame()

def fetch_news_feed(symbol):
    try:
        feed = feedparser.parse(f'https://news.google.com/rss/search?q={symbol}')
        return feed.entries[:3]
    except:
        return []

def render_heatmap_box(symbol, bias):
    color = {"Bullish": "#4CAF50", "Bearish": "#F44336"}.get(bias, "#9E9E9E")
    return f"<div style='background-color:{color};padding:5px;margin:2px;border-radius:5px;color:white'>{symbol}: {bias}</div>"

def get_tradingview_symbol(symbol):
    mapping = {
        "BTCUSD": "BINANCE:BTCUSDT",
        "ETHUSD": "BINANCE:ETHUSDT",
        "XAUUSD": "TVC:GOLD",
        "USOIL": "TVC:USOIL",
        "USTEC": "NASDAQ:NDX"
    }
    return mapping.get(symbol, f"BINANCE:{symbol}")

def generate_ai_features(df):
    df['return'] = df['Close'].pct_change()
    df['EMA5'] = df['Close'].ewm(span=5).mean()
    df['EMA20'] = df['Close'].ewm(span=20).mean()
    df['EMA_diff'] = df['EMA5'] - df['EMA20']
    df['RSI'] = 100 - (100 / (1 + df['return'].rolling(14).mean() / df['return'].rolling(14).std()))
    df.dropna(inplace=True)
    return df[['return', 'EMA_diff', 'RSI']]

assets_data, _ = fetch_market_data()
df = pd.DataFrame(assets_data)

symbol_map = {
    "BTCUSD": "BTC-USD",
    "ETHUSD": "ETH-USD",
    "XAUUSD": "GC=F",
    "USOIL": "CL=F",
    "USTEC": "^NDX"
}

filter_signal = st.checkbox("🔎 Tampilkan hanya simbol dengan sinyal entry (BUY/SELL)")
active_signals = {}

for symbol, ticker in symbol_map.items():
    try:
        data = load_price_data(ticker, '1h')
        bt = backtest_signals(data)
        if bt['Signal'].iloc[-1] != 0:
            active_signals[symbol] = "BUY" if bt['Signal'].iloc[-1] == 1 else "SELL"
    except:
        continue

if filter_signal:
    symbol_map = {s: t for s, t in symbol_map.items() if s in active_signals}

tabs = st.tabs(list(symbol_map.keys()))
for i, (symbol, ticker) in enumerate(symbol_map.items()):
    with tabs[i]:
        st.header(f"📌 {symbol}")
        tf = st.selectbox("🕒 Pilih timeframe:", ["5m", "15m", "1h", "4h", "1d"], key=symbol)

        col1, col2 = st.columns([3, 1])
        with col1:
            tf_map = {"5m": "5", "15m": "15", "1h": "60", "4h": "240", "1d": "D"}
            interval_code = tf_map.get(tf, "60")
            tvsymbol = get_tradingview_symbol(symbol)
            st.markdown("### 📈 Chart Interaktif TradingView (Candlestick)")
            components.html(f'''<iframe src="https://www.tradingview.com/widgetembed/?symbol={tvsymbol}&interval={interval_code}&theme=dark&style=1" width="100%" height="500" frameborder="0"></iframe>''', height=520)

            st.markdown(f"### 📊 Analisa Lengkap {symbol}")
            try:
                row = df[df['symbol'] == symbol].iloc[0]
                st.markdown(f"""
- **Harga**: ${row['price']}
- **Bias**: {row['bias']}
- **Support**: {row['support']}
- **Resistance**: {row['resistance']}
- **Volatilitas**: {row['volatility']}
                """)
            except:
                st.warning("Data tidak tersedia untuk analisa lengkap.")

            st.markdown("### 🤖 Prediksi AI & Confidence (Arah & Volatilitas)")
            try:
                df_price = load_price_data(ticker, '1h')
                features = generate_ai_features(df_price)
                latest_features = features.iloc[-1:]
                prob = ai_model.predict_proba(latest_features)[0]
                direction = "⬆️ Naik" if prob[1] > 0.5 else "⬇️ Turun"
                st.metric("Prediksi AI", direction, delta=f"Confidence: {prob[1]*100:.2f}%")

                vol_pred = features['return'].rolling(20).std().iloc[-1] * 100
                st.caption(f"📉 Prediksi Volatilitas (1h): ±{vol_pred:.2f}%")

                bias = df[df['symbol'] == symbol]['bias'].values[0] if symbol in df['symbol'].values else ''
                if (direction == "⬆️ Naik" and bias == "Bearish") or (direction == "⬇️ Turun" and bias == "Bullish"):
                    st.warning("⚠️ AI dan analisa teknikal tidak selaras. Gunakan kehati-hatian.")
            except Exception as e:
                st.warning(f"Gagal memuat prediksi AI: {e}")

            st.markdown("### 🔍 Saran Entry Otomatis")
            try:
                data = load_price_data(ticker, tf)
                suggestion = generate_entry_suggestion(data)
                st.markdown(suggestion if suggestion else "Tidak ada saran.")
            except:
                suggestion = ""
                st.warning("Gagal memuat data untuk analisa sinyal.")

            
            st.markdown("### 🧠 Confidence Breakdown")
            try:
                if suggestion:
                    with st.expander("📊 Rincian Indikator"):
                        for line in suggestion.split('\n'):
                            if any(x in line for x in ["📊", "📉", "📈", "🔼", "🔽"]):
                                st.write("✅", line)
                    conf_score = sum(suggestion.count(k) for k in ['📊', '📉', '📈', '🔼', '🔽'])
                    total_signals = 6
                    conf_ratio = min(conf_score / total_signals, 1.0)
                    st.progress(conf_ratio)
                    st.caption(f"Confidence Score: {conf_ratio*100:.1f}%")
                else:
                    st.caption("Confidence tidak tersedia")
            except Exception as e:
                st.caption(f"Confidence error: {e}")
                st.caption(f"Confidence error: {e}")

            st.markdown("### 🧪 Backtest Mini")
            try:
                backtest = backtest_signals(data)
                signal_count = (backtest['Signal'] != 0).sum()
                st.markdown(f"💡 Total sinyal historis terdeteksi: {signal_count}")
                if signal_count >= 2:
                    accuracy = calculate_signal_accuracy(data)
                    st.success(f"🎯 Akurasi sinyal historis: {accuracy}%")
                # st.line_chart(...) removed as requested for cleaner UI
            except:
                st.warning("Gagal backtest sinyal historis.")

            st.markdown("### ⚖️ Risk Reward Ratio")
            try:
                if "RRR" in suggestion:
                    rrr_line = [line for line in suggestion.split('\n') if "RRR" in line][0]
                    st.success(rrr_line)
                else:
                    st.info("RRR tidak tersedia.")
            except:
                st.info("RRR tidak tersedia.")

            st.markdown("### 🧮 Evaluasi SL/TP Otomatis")
            try:
                atr = AverageTrueRange(data['High'], data['Low'], data['Close'], window=14).average_true_range().iloc[-1]
                sl_range = atr * 0.5
                tp_range = atr * 1.5
                st.success(f"SL: ±{sl_range:.2f}, TP: ±{tp_range:.2f} (berdasarkan ATR14)")
            except:
                st.warning("Tidak dapat menghitung SL/TP otomatis.")

            st.markdown("### 🌐 Berita Global Terkait")
            news_items = fetch_news_feed(symbol)
            if news_items:
                for n in news_items:
                    st.markdown(f"**[{n.title}]({n.link})**")
            else:
                st.caption("Tidak ada berita ditemukan.")

        with col2:
            st.markdown("### 🔥 Heatmap Sinyal")
            for a in assets_data:
                st.markdown(render_heatmap_box(a['symbol'], a['bias']), unsafe_allow_html=True)

            st.markdown("### 📡 Sinyal Aktif")
            if active_signals:
                for s in active_signals:
                    st.success(f"{s} → {active_signals[s]}")
            else:
                st.info("Tidak ada sinyal aktif.")
