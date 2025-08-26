# 🚀 Quick Start Guide - Trading Bot

Panduan cepat untuk menjalankan Trading Bot dalam 5 menit!

## ⚡ Langkah Cepat

### 1. **Setup Otomatis (Recommended)**
```bash
# Clone repository
git clone <repository-url>
cd trading-bot

# Jalankan setup wizard
python setup.py
```

### 2. **Setup Manual**
```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env dengan API keys
nano .env
```

## 🔑 Konfigurasi API Keys

### **Telegram Bot**
1. Chat dengan @BotFather di Telegram
2. Buat bot baru dengan `/newbot`
3. Copy token ke `TELEGRAM_TOKEN`
4. Chat dengan bot dan gunakan `/start`
5. Copy chat ID ke `TELEGRAM_CHAT_ID`

### **OKX Exchange**
1. Login ke [OKX](https://www.okx.com)
2. Buka API Management
3. Buat API key baru
4. Copy ke `OKX_API_KEY`, `OKX_SECRET_KEY`, `OKX_PASSPHRASE`

### **Hyperliquid**
1. Setup wallet di [Hyperliquid](https://hyperliquid.xyz)
2. Export private key
3. Copy ke `HYPERLIQUID_PRIVATE_KEY`

## 🧪 Test Bot

```bash
# Test semua komponen
python test_bot.py

# Jika semua PASS, bot siap digunakan!
```

## 🚀 Jalankan Bot

```bash
# Jalankan bot
python run_bot.py

# Atau gunakan main.py
python main.py
```

## 📱 Gunakan Telegram

1. **Start Bot**: `/start`
2. **Mulai Trading**: `/start_bot`
3. **Monitor Status**: `/status`
4. **Lihat Balance**: `/balance`
5. **Lihat Posisi**: `/positions`
6. **History Trading**: `/trades`
7. **Bantuan**: `/help`

## ⚠️ Penting!

- **Test dulu** di sandbox mode
- **Monitor bot** secara berkala
- **Gunakan modal** yang siap hilang
- **Jangan share** file .env

## 🆘 Troubleshooting

### **Import Error**
```bash
pip install -r requirements.txt
```

### **API Key Error**
- Pastikan semua API keys sudah diisi
- Cek permission API keys
- Test koneksi dengan `test_bot.py`

### **Bot Tidak Merespon**
- Cek log file
- Pastikan bot sudah start
- Cek internet connection

## 📞 Support

- **Issues**: GitHub repository
- **Documentation**: README.md
- **Testing**: `python test_bot.py`

---

**🎯 Bot siap digunakan! Selamat trading! 🚀📈**