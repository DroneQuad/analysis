import matplotlib
matplotlib.use('Agg')

import yfinance as yf
import requests
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import mplfinance as mpf
import io
import ta

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
    now = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
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

def calculate_indicators(data):
    if len(data) < 50:
        return pd.DataFrame()
    data['EMA5'] = data['Close'].ewm(span=5).mean()
    data['EMA20'] = data['Close'].ewm(span=20).mean()
    data['EMA50'] = data['Close'].ewm(span=50).mean()
    data['SMA5'] = data['Close'].rolling(window=5).mean()
    data['SMA20'] = data['Close'].rolling(window=20).mean()
    data['SMA50'] = data['Close'].rolling(window=50).mean()
    data['RSI'] = ta.momentum.RSIIndicator(close=data['Close'], window=14).rsi()
    macd = ta.trend.MACD(close=data['Close'])
    data['MACD'] = macd.macd()
    data['MACD_signal'] = macd.macd_signal()
    return data

def generate_entry_suggestion(data):
    if data is None or len(data) < 50:
        return "Data tidak cukup untuk memberikan saran."

    latest = data.iloc[-1]
    signals = []
    recommendation = "🔍 Rekomendasi: Tunggu konfirmasi arah"

    entry_price = None
    stop_loss = None
    take_profit = None

    try:
        atr = ta.volatility.AverageTrueRange(
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            window=14
        ).average_true_range().iloc[-1]
    except:
        atr = 0

    if latest['EMA5'] > latest['EMA20'] > latest['EMA50']:
        signals.append("📊 EMA trend naik (5>20>50)")
        if latest['RSI'] < 70:
            entry_price = round(latest['EMA20'], 2)
            stop_loss = round(latest['Low'] - atr, 2)
            take_profit = round(entry_price + 2 * (entry_price - stop_loss), 2)
            recommendation = "✅ BUY on pullback ke EMA20"
    elif latest['EMA5'] < latest['EMA20'] < latest['EMA50']:
        signals.append("📊 EMA trend turun (5<20<50)")
        if latest['RSI'] > 30:
            entry_price = round(latest['EMA20'], 2)
            stop_loss = round(latest['High'] + atr, 2)
            take_profit = round(entry_price - 2 * (stop_loss - entry_price), 2)
            recommendation = "⚠️ SELL on rebound ke EMA20"

    if latest['RSI'] < 30:
        signals.append("📉 RSI oversold → potensi Buy")
    elif latest['RSI'] > 70:
        signals.append("📈 RSI overbought → potensi Sell")

    if latest['MACD'] > latest['MACD_signal']:
        signals.append("🔼 MACD positif → momentum naik")
    else:
        signals.append("🔽 MACD negatif → momentum lemah")

    if latest['SMA5'] > latest['SMA20'] > latest['SMA50']:
        signals.append("📈 SMA menunjukkan tren naik stabil")
    elif latest['SMA5'] < latest['SMA20'] < latest['SMA50']:
        signals.append("📉 SMA menunjukkan tren turun stabil")

    output = "\n".join(signals + [recommendation])
    if entry_price is not None:
        output += f"\n🎯 Entry: ${entry_price}"
    if stop_loss is not None:
        output += f"\n🛑 SL: ${stop_loss}"
    if take_profit is not None:
        output += f"\n🎯 TP: ${take_profit}"

    return output
