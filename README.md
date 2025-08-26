# 🤖 Trading Bot Otomatis dengan Telegram

Bot trading cryptocurrency otomatis yang menggunakan strategi canggih dan dapat dikontrol melalui Telegram. Bot ini mengintegrasikan **OKX Wallet** untuk blockchain operations dan **Hyperliquid** untuk trading execution.

## 🚀 Fitur Utama

### 📊 **Analisis Market Otomatis**
- **RSI (Relative Strength Index)** - Mengidentifikasi kondisi overbought/oversold
- **MACD (Moving Average Convergence Divergence)** - Signal trend dan momentum
- **Bollinger Bands** - Analisis volatilitas dan support/resistance
- **Volume Analysis** - Konfirmasi signal dengan volume trading
- **Sentiment Analysis** - Kombinasi semua indikator untuk keputusan trading

### 🎯 **Strategi Trading Canggih**
- **Multi-Indicator Analysis** - Kombinasi RSI, MACD, dan Bollinger Bands
- **Confidence-Based Trading** - Ukuran posisi berdasarkan level confidence
- **Adaptive Position Sizing** - Menyesuaikan ukuran posisi dengan market condition
- **Real-time Signal Generation** - Update signal setiap jam

### 🛡️ **Risk Management Otomatis**
- **Stop Loss Otomatis** - Proteksi kerugian berdasarkan persentase
- **Take Profit Otomatis** - Realisasi profit pada target tertentu
- **Daily Trade Limits** - Batasan jumlah trade per hari
- **Daily Loss Limits** - Batasan kerugian maksimal per hari
- **Cooldown Period** - Jeda antar trade untuk menghindari overtrading

### 📱 **Kontrol Telegram Lengkap**
- **Start/Stop Bot** - Kontrol penuh bot trading
- **Real-time Monitoring** - Status bot, balance, dan posisi
- **Trade Notifications** - Notifikasi setiap trade yang dieksekusi
- **Interactive Buttons** - Interface yang mudah digunakan

### 🔗 **Blockchain Integration**
- **OKX Wallet Support** - Multi-chain wallet (Ethereum, Polygon, BSC, Arbitrum)
- **Market Data Sources** - CoinGecko & Binance API integration
- **Secure Transactions** - Private key management dan transaction signing

## 🔄 Alur Trading Bot

### 1. **Data Collection & Analysis**
```
Market Data APIs → Technical Indicators → Sentiment Score
     ↓
• CoinGecko/Binance untuk market data
• Calculate RSI, MACD, Bollinger Bands
• Analyze volume patterns
• Generate sentiment score (-1 to +1)
```

### 2. **Signal Generation**
```
Sentiment Analysis → Trading Decision → Confidence Level → Position Size
     ↓
• Strong Buy: Sentiment > +0.7, Confidence > 0.6
• Buy: Sentiment > +0.3, Confidence > 0.5
• Hold: -0.3 ≤ Sentiment ≤ +0.3
• Sell: Sentiment < -0.3, Confidence > 0.5
• Strong Sell: Sentiment < -0.7, Confidence > 0.6
```

### 3. **Risk Assessment**
```
Market Conditions → Risk Calculation → Position Sizing → Order Execution
     ↓
• Calculate optimal position size
• Apply confidence multiplier
• Check daily limits
• Verify cooldown period
```

### 4. **Order Execution**
```
Trading Signal → Hyperliquid → Order Placement → Position Tracking
     ↓
• Place limit orders
• Monitor order status
• Update active positions
• Track P&L
```

### 5. **Risk Management Loop**
```
Active Positions → Price Monitoring → Stop Loss/Take Profit → Position Closure
     ↓
• Continuous price monitoring
• Automatic stop loss execution
• Take profit realization
• Position size adjustment
```

## 🏗️ Arsitektur Sistem

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Telegram Bot  │    │  Trading Bot    │    │  Market Data    │
│                 │    │                 │    │                 │
│ • User Commands │◄──►│ • Strategy      │◄──►│ • CoinGecko     │
│ • Notifications │    │ • Risk Mgmt     │    │ • Binance API   │
│ • Status Report │    │ • Order Exec    │    │ • Real-time     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │ Hyperliquid     │
                       │                 │
                       │ • Order Exec    │
                       │ • Position Mgmt │
                       │ • Balance       │
                       └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │ OKX Wallet      │
                       │                 │
                       │ • Blockchain    │
                       │ • Multi-chain   │
                       │ • Transactions  │
                       └─────────────────┘
```

## 📋 Requirements

### **Dependencies**
- Python 3.8+
- python-telegram-bot
- web3 (blockchain integration)
- requests, aiohttp
- pandas, numpy

### **API Keys & Configuration Required**
- **Telegram Bot Token** - Dari @BotFather
- **OKX Wallet Private Key** - Wallet private key untuk blockchain
- **OKX Wallet Address** - Wallet address untuk tracking
- **OKX Network** - Blockchain network (ethereum, polygon, bsc, dll)
- **Hyperliquid Private Key** - Wallet private key untuk trading
- **Market Data Source** - CoinGecko atau Binance

## 🚀 Cara Instalasi

### 1. **Clone Repository**
```bash
git clone <repository-url>
cd trading-bot
```

### 2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

### 3. **Setup Environment Variables**
```bash
cp .env.example .env
# Edit .env dengan konfigurasi yang sesuai
```

### 4. **Konfigurasi**
```bash
# Telegram Bot
TELEGRAM_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# OKX Wallet (Blockchain)
OKX_WALLET_PRIVATE_KEY=your_wallet_private_key
OKX_WALLET_ADDRESS=your_wallet_address
OKX_NETWORK=ethereum  # atau polygon, bsc, arbitrum

# Hyperliquid
HYPERLIQUID_PRIVATE_KEY=your_hyperliquid_private_key

# Market Data
MARKET_DATA_SOURCE=coingecko  # atau binance
```

### 5. **Run Bot**
```bash
python main.py
```

## 📱 Cara Penggunaan Telegram Bot

### **Commands Utama**
- `/start` - Mulai bot dan lihat menu utama
- `/start_bot` - Mulai bot trading otomatis
- `/stop_bot` - Hentikan bot trading
- `/status` - Lihat status bot dan posisi aktif
- `/balance` - Lihat balance dan risk management
- `/positions` - Lihat posisi yang sedang dibuka
- `/trades` - Lihat history trading
- `/help` - Bantuan lengkap

### **Interactive Buttons**
- 🚀 **Start Bot** - Mulai trading otomatis
- 🛑 **Stop Bot** - Hentikan trading
- 📊 **Status** - Monitor progress
- 💰 **Balance** - Cek balance
- 📈 **Positions** - Lihat posisi aktif

## ⚙️ Konfigurasi Trading

### **Risk Management**
```python
MAX_POSITION_SIZE = 0.1        # 10% dari balance per trade
STOP_LOSS_PERCENTAGE = 2.0     # Stop loss 2%
TAKE_PROFIT_PERCENTAGE = 5.0   # Take profit 5%
MAX_DAILY_TRADES = 10          # Max 10 trades per hari
MAX_DAILY_LOSS = 50            # Max loss $50 per hari
COOLDOWN_PERIOD = 300          # 5 menit cooldown antar trade
```

### **Strategy Parameters**
```python
RSI_PERIOD = 14                # RSI calculation period
RSI_OVERBOUGHT = 70           # RSI overbought threshold
RSI_OVERSOLD = 30             # RSI oversold threshold
MACD_FAST = 12                # MACD fast EMA
MACD_SLOW = 26                # MACD slow EMA
MACD_SIGNAL = 9               # MACD signal line
```

### **Blockchain Configuration**
```python
OKX_NETWORK = 'ethereum'      # ethereum, polygon, bsc, arbitrum
MARKET_DATA_SOURCE = 'coingecko'  # coingecko, binance
```

## 🔍 Monitoring & Logging

### **Log Files**
- `trading_bot.log` - Trading bot activities
- `trading_bot_system.log` - System-level logs

### **Real-time Notifications**
- Trade execution notifications
- Error alerts
- Daily summary reports
- Position updates

## 🛡️ Security Features

### **Private Key Protection**
- Environment variables untuk sensitive data
- No hardcoded credentials
- Secure blockchain transaction signing

### **Risk Controls**
- Position size limits
- Daily loss limits
- Automatic stop losses
- Cooldown periods

## 📊 Performance Metrics

### **Tracking Metrics**
- Total trades per day
- Win/loss ratio
- Daily P&L
- Position performance
- Strategy effectiveness

### **Optimization**
- Confidence-based position sizing
- Adaptive risk management
- Market condition analysis
- Performance monitoring

## 🚨 Disclaimer

**⚠️ PERINGATAN RISIKO:**
- Trading cryptocurrency memiliki risiko tinggi
- Bot ini untuk tujuan edukasi dan research
- Pastikan memahami risiko sebelum menggunakan
- Gunakan dengan modal yang siap hilang
- Monitor bot secara berkala
- **Jangan share private keys ke siapapun**

## 🤝 Support & Contributing

### **Issues & Bugs**
- Buat issue di GitHub repository
- Sertakan log error dan steps to reproduce
- Jelaskan environment dan konfigurasi

### **Feature Requests**
- Sertakan use case dan benefit
- Jelaskan implementasi yang diinginkan
- Diskusikan dengan maintainer

### **Contributing**
- Fork repository
- Buat feature branch
- Submit pull request
- Ikuti coding standards

## 📈 Roadmap

### **Phase 1 (Current)**
- ✅ Basic trading strategy
- ✅ OKX Wallet + Hyperliquid integration
- ✅ Telegram bot interface
- ✅ Risk management

### **Phase 2 (Next)**
- 🔄 Advanced strategies (ML-based)
- 🔄 Multiple blockchain support
- 🔄 Backtesting framework
- 🔄 Performance analytics

### **Phase 3 (Future)**
- 📊 Portfolio management
- 📊 Social trading features
- 📊 Mobile app
- 📊 Advanced AI strategies

## 📞 Contact

- **GitHub Issues**: [Repository Issues](link-to-repo)
- **Email**: your-email@example.com
- **Telegram**: @your-username

---

**🎯 Bot ini dirancang untuk trading otomatis yang aman dan profitable dengan risk management yang ketat. Selalu monitor dan test di environment sandbox sebelum menggunakan dengan modal asli.**
