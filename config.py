import os
from dotenv import load_dotenv

load_dotenv()

# Konfigurasi Telegram Bot
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# Konfigurasi OKX Wallet (Blockchain)
OKX_WALLET_PRIVATE_KEY = os.getenv('OKX_WALLET_PRIVATE_KEY')
OKX_WALLET_ADDRESS = os.getenv('OKX_WALLET_ADDRESS')
OKX_NETWORK = os.getenv('OKX_NETWORK', 'ethereum')  # ethereum, polygon, bsc, dll

# Konfigurasi Hyperliquid
HYPERLIQUID_PRIVATE_KEY = os.getenv('HYPERLIQUID_PRIVATE_KEY')
HYPERLIQUID_BASE_URL = "https://api.hyperliquid.xyz"

# Konfigurasi Trading
TRADING_PAIRS = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT']
INITIAL_BALANCE = float(os.getenv('INITIAL_BALANCE', '1000'))
MAX_POSITION_SIZE = float(os.getenv('MAX_POSITION_SIZE', '0.1'))
STOP_LOSS_PERCENTAGE = float(os.getenv('STOP_LOSS_PERCENTAGE', '2.0'))
TAKE_PROFIT_PERCENTAGE = float(os.getenv('TAKE_PROFIT_PERCENTAGE', '5.0'))

# Konfigurasi Strategi
RSI_PERIOD = int(os.getenv('RSI_PERIOD', '14'))
RSI_OVERBOUGHT = int(os.getenv('RSI_OVERBOUGHT', '70'))
RSI_OVERSOLD = int(os.getenv('RSI_OVERSOLD', '30'))
MACD_FAST = int(os.getenv('MACD_FAST', '12'))
MACD_SLOW = int(os.getenv('MACD_SLOW', '26'))
MACD_SIGNAL = int(os.getenv('MACD_SIGNAL', '9'))

# Konfigurasi Risk Management
MAX_DAILY_TRADES = int(os.getenv('MAX_DAILY_TRADES', '10'))
MAX_DAILY_LOSS = float(os.getenv('MAX_DAILY_LOSS', '50'))
COOLDOWN_PERIOD = int(os.getenv('COOLDOWN_PERIOD', '300'))  # 5 menit dalam detik

# Konfigurasi Data Source (untuk market data)
MARKET_DATA_SOURCE = os.getenv('MARKET_DATA_SOURCE', 'coingecko')  # coingecko, binance, dll