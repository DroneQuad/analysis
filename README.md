
# 📈 Market Analysis Dashboard by DroneQuad

Sebuah dashboard analisa pasar otomatis berbasis Streamlit, untuk memantau pergerakan harga dan sinyal trading pada instrumen Crypto, Forex, dan Komoditas secara real-time.

---

## 🚀 Fitur Utama

- 🔄 Auto refresh data harga multi-timeframe
- 📊 Analisa teknikal lengkap (EMA, RSI, MACD, SMA)
- 💡 Saran entry BUY/SELL otomatis + SL/TP + RRR
- 🧠 Prediksi AI arah pasar (Confidence Score)
- 🧪 Backtest mini sinyal sebelumnya
- 🌐 Embed chart candlestick dari TradingView
- 📰 News Feed global berdasarkan simbol
- 🔥 Heatmap sektoral dan highlight sinyal aktif

---

## 🗂️ Struktur File

| File                          | Deskripsi                                       |
|-------------------------------|------------------------------------------------|
| `market_analysis_gui.py`      | Aplikasi utama Streamlit GUI                   |
| `Analysisxls_combined.py`     | Modul backend analisa teknikal & data pasar    |
| `ai_signal_booster_model.pkl` | Model AI `.pkl` untuk prediksi arah market     |
| `requirements.txt`            | Daftar dependensi Python                       |

---

## ▶️ Cara Menjalankan Lokal

1. Install Python ≥ 3.9
2. Clone atau unzip project
3. Jalankan:

```bash
pip install -r requirements.txt
streamlit run market_analysis_gui.py
```

---

## 🧠 Syarat AI Model

Pastikan file `ai_signal_booster_model.pkl` berada di direktori yang sama.  
Model ini digunakan untuk prediksi probabilitas arah naik/turun berdasarkan fitur teknikal.

---

## 🌐 Siap untuk Streamlit Cloud

Semua file telah disiapkan untuk deployment gratis di [Streamlit Cloud](https://streamlit.io/cloud).  
Pastikan file ini tersedia:
- `market_analysis_gui.py`
- `Analysisxls_combined.py`
- `ai_signal_booster_model.pkl`
- `requirements.txt`

---

## 📩 Kontak & Lisensi

Dikembangkan oleh DroneQuad  
Lisensi: Free for personal trading & research use
