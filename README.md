# 📈 Market Analysis Dashboard (Streamlit)

Web-based GUI untuk analisa teknikal multi-instrumen menggunakan:
- EMA, SMA, MACD, RSI, ATR
- Saran entry otomatis + confidence score
- Candlestick chart interaktif TradingView
- Berita real-time dari NewsAPI
- Multi-timeframe + auto refresh + sinyal BUY/SELL

## 🚀 Cara Deploy ke Streamlit Cloud

### 1. Buat repository GitHub
Upload file berikut:
- `market_analysis_gui.py`
- `Analysisxls_combined.py`
- `requirements.txt`

### 2. Tambahkan API Key NewsAPI
Gunakan secrets Streamlit Cloud:
Masukkan `NEWS_API_KEY` lewat menu “Secrets” di Streamlit Cloud UI:
```
[general]
NEWS_API_KEY = "isi_api_key_anda_disini"
```

### 3. Deploy
- Buka [https://streamlit.io/cloud](https://streamlit.io/cloud)
- Login dengan GitHub
- Klik **New App**
- Pilih repo, branch dan file utama: `market_analysis_gui.py`
- Klik **Deploy**

App akan berjalan otomatis.

## ⚠️ Notes
- Pastikan semua library ada di `requirements.txt`
- Gunakan API key asli NewsAPI Anda (free tier cukup)
