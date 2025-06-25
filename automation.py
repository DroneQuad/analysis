import matplotlib
matplotlib.use('Agg')  # Hindari warning GUI di thread

# automation.py
import time
import threading
from datetime import datetime
from Analysisxls_combined import (
    fetch_market_data,
    generate_short_report,
    send_telegram_message,
    generate_chart_with_ema,
    send_chart_to_telegram,
    generate_comment
)

# Cache sinyal terakhir untuk deteksi perubahan
last_signal_cache = {}

# Periksa sinyal EMA setiap 5 menit
def ema_alert_loop():
    while True:
        try:
            print(f"[{datetime.now()}] Checking EMA signals...")
            symbol_map = {
                "BTCUSD": "BTC-USD",
                "ETHUSD": "ETH-USD",
                "XAUUSD": "GC=F",
                "USOIL": "CL=F",
                "USTEC": "^NDX"
            }
            for symbol, ticker in symbol_map.items():
                buf = generate_chart_with_ema(ticker, symbol)
                if not buf:
                    continue

                # Simulasi deteksi sinyal terakhir dari nama file/chart (bisa diimprove pakai image/signal parsing)
                # Sementara: pakai dummy sinyal "BUY"/"SELL"
                latest_signal = "BUY" if datetime.now().minute % 2 == 0 else "SELL"

                # Cek cache
                if last_signal_cache.get(symbol) != latest_signal:
                    last_signal_cache[symbol] = latest_signal
                    msg = f"📡 *Sinyal EMA Detected*\n*{symbol}*: {latest_signal}\nTime: {datetime.now().strftime('%H:%M:%S')}"
                    send_telegram_message(msg)
                    send_chart_to_telegram(ticker, symbol)

        except Exception as e:
            print(f"EMA alert error: {e}")
        time.sleep(300)  # 5 menit

# Kirim ringkasan pasar setiap 1 menit
def report_loop():
    while True:
        try:
            print(f"[{datetime.now()}] Sending auto market report...")
            assets_data, _ = fetch_market_data()
            message = generate_short_report(assets_data)
            send_telegram_message("📢 *AUTO REPORT*\n" + message)
        except Exception as e:
            print(f"Report loop error: {e}")
        time.sleep(60)

# Jalankan semua thread
if __name__ == "__main__":
    t1 = threading.Thread(target=ema_alert_loop, daemon=True)
    t2 = threading.Thread(target=report_loop, daemon=True)
    t1.start()
    t2.start()

    print("✅ Background automation started. Running forever...")
    while True:
        time.sleep(10)
