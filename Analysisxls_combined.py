import matplotlib
matplotlib.use('Agg')  # Gunakan backend non-GUI

import yfinance as yf
import numpy as np
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import mplfinance as mpf
import io

# ========== FUNGSI UTAMA UNTUK GUI ==========

def fetch_market_data():
    symbol_map = {
        "BTCUSD": {"ticker": "BTC-USD", "type": "crypto"},
        "ETHUSD": {"ticker": "ETH-USD", "type": "crypto"},
        "XAUUSD": {"ticker": "GC=F", "type": "commodity"},
        "USOIL": {"ticker": "CL=F", "type": "commodity"},
        "USTEC": {"ticker": "^NDX", "type": "index"},
    }
    assets = []
    for symbol, info in symbol_map.items():
        price = get_price(info["ticker"])
        if price is None:
            continue
        levels = get_technical_levels(info["ticker"], price)
        bias = levels["bias"]
        assets.append({
            "symbol": symbol,
            "price": price,
            "bias": bias,
            "support": levels["support"],
            "resistance": levels["resistance"],
            "volatility": levels["volatility"],
            "fallback_used": False
        })
    return assets, []

def get_price(ticker):
    try:
        data = yf.Ticker(ticker).history(period="1d", interval="15m")
        return round(data["Close"].iloc[-1], 2)
    except:
        return None

def get_technical_levels(ticker, price):
    try:
        data = yf.Ticker(ticker).history(period="7d", interval="1h")
        short_ma = data["Close"].tail(5).mean()
        long_ma = data["Close"].mean()
        bias = "Bullish" if short_ma > long_ma else "Bearish"
        vol = data["Close"].pct_change().std() * 100
        return {
            "bias": bias,
            "support": round(price * 0.95, 2),
            "resistance": round(price * 1.05, 2),
            "volatility": f"{vol:.2f}%" if not np.isnan(vol) else "N/A"
        }
    except:
        return {
            "bias": "Neutral",
            "support": price * 0.95,
            "resistance": price * 1.05,
            "volatility": "N/A"
        }

def generate_comment(symbol, bias):
    if bias == "Bullish":
        return f"{symbol}: Potensi breakout, tren menguat."
    elif bias == "Bearish":
        return f"{symbol}: Waspadai koreksi, tren melemah."
    return f"{symbol}: Perlu konfirmasi lebih lanjut."

def generate_short_report(assets_data):
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    text = f"📈 *MARKET ANALYSIS REPORT*\n*Updated: {now}*\n\n"
    for a in assets_data:
        text += f"- {a['symbol']}: ${a['price']:,} {a['bias']}\n"
        text += f"  📌 {generate_comment(a['symbol'], a['bias'])}\n"
    return text

def generate_chart_with_ema(ticker, symbol, timeframe='15m'):
    try:
        data = yf.Ticker(ticker).history(period='7d', interval=timeframe)
        if data.empty:
            return None
        data['EMA5'] = data['Close'].ewm(span=5).mean()
        data['EMA20'] = data['Close'].ewm(span=20).mean()
        apds = [
            mpf.make_addplot(data['EMA5'], color='lime'),
            mpf.make_addplot(data['EMA20'], color='orange')
        ]
        fig, ax = mpf.plot(
            data,
            type='candle',
            addplot=apds,
            returnfig=True,
            title=f"{symbol} {timeframe} Chart",
            style='yahoo',
            volume=False
        )
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plt.close(fig)
        return buf
    except:
        return None
