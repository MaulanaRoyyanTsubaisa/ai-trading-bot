# 🤖 AlphaSignal AI - Trading Terminal & Alert Bot

Platform Terminal Analitik Pasar & Bot Sinyal Trading bertenaga AI (terinspirasi dari konsep sistem terminal **SahamPro** / **Crypto AI Terminal** oleh Ricky Irawan @ceootb).

---

## 🌟 Fitur Utama

1. **Engine Analisis Kuantitatif & Teknikal Multi-Faktor:**
   - **RSI (14)** + Deteksi Divergensi & Level Jenuh Beli / Jenuh Jual.
   - **MACD (12, 26, 9)** + Konfirmasi Golden Cross / Death Cross.
   - **EMA Ribbon (20, 50, 200)** + Trend Alignment.
   - **Bollinger Bands** + Squeeze & Breakout Detector.
   - **SuperTrend & Dynamic Support/Resistance Pivot Levels**.
   - **ATR (Average True Range)** untuk kalkulasi dinamis Stop Loss & Take Profit Targets.

2. **Whale Tracker & Smart Money Flow (Bandarmology Radar):**
   - Deteksi anomali volume & lonjakan transaksi besar (*Whale Trades* > \$50.000).
   - Pengukuran **Chaikin Money Flow (CMF)** untuk mendeteksi akumulasi vs distribusi institusi.
   - Rasio kekuatan pembeli vs penjual (*Buyer vs Seller Dominance*).

3. **AI Signal Reasoner:**
   - Menghasilkan status sinyal terukur: `STRONG BUY`, `BUY`, `NEUTRAL`, `SELL`, `STRONG SELL`.
   - Menghitung **Confidence Score (%)**, **Entry Zone**, **Target TP1, TP2, TP3**, **Stop Loss**, dan **Risk/Reward Ratio (RRR)**.
   - Menyusun ringkasan analisa profesional dan deskriptif dalam Bahasa Indonesia.

4. **Telegram Alert Bot Otomatis:**
   - Mengirim notifikasi sinyal real-time dengan tampilan format kartu (emoji, status, level harga, dan catatan analisa AI).
   - Dilengkapi cooldown cerdas untuk menghindari spam alert berulang.
   - TP1, TP2, TP3, dan SL dikirim sebagai reply baru ke pesan sinyal awal; kartu awal ikut diedit dengan checklist terbaru.
   - Message ID dan progres sinyal disimpan ke disk sehingga tetap dapat dilanjutkan setelah service restart.

5. **Modern Cyberpunk Web Terminal Dashboard:**
   - **Live Ticker Bar**: Pergerakan harga crypto real-time.
   - **TradingView Interactive Chart**: Chart interaktif lengkap dengan indikator bawaan.
   - **AI Quant Screener**: Tabel filter multi-kriteria (Oversold, High Confidence, Whale Inflow, dll.).
   - **Whale Radar View**: Visualisasi aliran dana paus secara real-time.
   - **AI Copilot Chat**: Asisten tanya-jawab teknikal instan untuk pair mana pun.

---

## 🚀 Cara Menjalankan Aplikasi

### Produksi dengan Docker

```bash
docker compose up -d --build
docker compose logs -f app
```

Dashboard hanya diekspos ke `127.0.0.1:8000`. Gunakan reverse proxy atau SSH tunnel untuk mengaksesnya dari luar server.

### Opsi 1: Cara Cepat (1-Klik via Windows Batch File)
Cukup klik dua kali file **`start_terminal.bat`** di folder proyek:
```bash
start_terminal.bat
```
Browser akan otomatis membuka `http://localhost:8000`.

### Opsi 2: Menjalankan via Terminal / CLI
1. **Jalankan Server Backend:**
   ```bash
   python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
   ```
2. Buka browser di `http://localhost:8000`.

---

## 📲 Cara Menghubungkan Bot Telegram Sendiri

1. Buka Telegram dan cari **`@BotFather`**. Ketik `/newbot`, ikuti petunjuk, lalu salin **HTTP API Token**.
2. Cari **`@userinfobot`** atau buat channel/grup baru untuk mendapatkan **Chat ID** Anda.
3. Buka file `.env` di folder proyek, lalu isi:
   ```env
   TELEGRAM_BOT_TOKEN=7654321098:AAxxxxxxx-xxxxxxx
   TELEGRAM_CHAT_ID=123456789
   ```
4. Simpan file dan jalankan ulang server.
5. Anda juga bisa menguji pengiriman sinyal langsung dari tombol **"Bot Telegram"** di dashboard web terminal!

---

## 📁 Struktur Direktori

```
ai-trading-bot/
├── backend/
│   ├── main.py                  # FastAPI server & endpoints
│   ├── config.py                # Konfigurasi bot & scanning
│   └── services/
│       ├── market_data.py       # Data feed real-time (Binance Data Gateway)
│       ├── ta_engine.py         # Technical indicator & math calculations
│       ├── whale_tracker.py     # Deteksi transaksi besar & akumulasi bandar
│       ├── ai_analyst.py        # AI signal reasoning & target calculator
│       ├── telegram_bot.py      # Format & pengiriman alert Telegram
│       └── scheduler.py         # Background scanning cron loop
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── HeaderTicker.jsx
│   │   │   ├── SignalCard.jsx
│   │   │   ├── TradingViewChart.jsx
│   │   │   ├── WhaleRadar.jsx
│   │   │   ├── MarketScreener.jsx
│   │   │   ├── AICopilotChat.jsx
│   │   │   └── TelegramSettingsModal.jsx
│   │   ├── App.jsx
│   │   └── index.css
│   └── dist/                    # Static built frontend
├── start_terminal.bat           # 1-klik launcher Windows
├── .env.example                 # Template konfigurasi
└── README.md                    # Dokumentasi lengkap
```
