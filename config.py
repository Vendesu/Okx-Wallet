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

# Konfigurasi Trading - Dynamic Symbol Selection
TRADING_MODE = os.getenv('TRADING_MODE', 'auto')  # auto, manual, trending, high_volume
TRADING_PAIRS = os.getenv('TRADING_PAIRS', '').split(',') if os.getenv('TRADING_PAIRS') else []

# Auto Trading Configuration
AUTO_SYMBOL_LIMIT = int(os.getenv('AUTO_SYMBOL_LIMIT', '50'))  # Max symbols untuk auto mode
MIN_VOLUME_USD = float(os.getenv('MIN_VOLUME_USD', '1000000'))  # Min volume untuk auto selection
TRENDING_SYMBOL_LIMIT = int(os.getenv('TRENDING_SYMBOL_LIMIT', '20'))  # Trending symbols limit

# Trading Configuration
INITIAL_BALANCE = float(os.getenv('INITIAL_BALANCE', '1000'))
MAX_POSITION_SIZE = float(os.getenv('MAX_POSITION_SIZE', '0.1'))

# Money Management Configuration
MONEY_MANAGEMENT_ENABLED = os.getenv('MONEY_MANAGEMENT_ENABLED', 'true').lower() == 'true'

# Risk Per Trade
RISK_PER_TRADE_PERCENTAGE = float(os.getenv('RISK_PER_TRADE_PERCENTAGE', '2.0'))  # 2% risk per trade
MAX_RISK_PER_TRADE_USD = float(os.getenv('MAX_RISK_PER_TRADE_USD', '20'))  # Max $20 risk per trade
MIN_RISK_PER_TRADE_USD = float(os.getenv('MIN_RISK_PER_TRADE_USD', '5'))   # Min $5 risk per trade

# Position Sizing
POSITION_SIZING_METHOD = os.getenv('POSITION_SIZING_METHOD', 'kelly')  # kelly, fixed, percentage, martingale
FIXED_POSITION_SIZE_USD = float(os.getenv('FIXED_POSITION_SIZE_USD', '50'))  # Fixed $50 per trade
PERCENTAGE_POSITION_SIZE = float(os.getenv('PERCENTAGE_POSITION_SIZE', '5.0'))  # 5% of balance per trade
KELLY_FRACTION = float(os.getenv('KELLY_FRACTION', '0.25'))  # 25% of Kelly Criterion

# Portfolio Management
MAX_PORTFOLIO_RISK_PERCENTAGE = float(os.getenv('MAX_PORTFOLIO_RISK_PERCENTAGE', '10.0'))  # Max 10% portfolio risk
MAX_CORRELATED_POSITIONS = int(os.getenv('MAX_CORRELATED_POSITIONS', '3'))  # Max 3 correlated positions
MAX_SECTOR_EXPOSURE = float(os.getenv('MAX_SECTOR_EXPOSURE', '30.0'))  # Max 30% per sector

# Stop Loss & Take Profit
STOP_LOSS_PERCENTAGE = float(os.getenv('STOP_LOSS_PERCENTAGE', '2.0'))
TAKE_PROFIT_PERCENTAGE = float(os.getenv('TAKE_PROFIT_PERCENTAGE', '5.0'))
TRAILING_STOP_ENABLED = os.getenv('TRAILING_STOP_ENABLED', 'true').lower() == 'true'
TRAILING_STOP_PERCENTAGE = float(os.getenv('TRAILING_STOP_PERCENTAGE', '1.0'))
BREAK_EVEN_ENABLED = os.getenv('BREAK_EVEN_ENABLED', 'true').lower() == 'true'
BREAK_EVEN_PERCENTAGE = float(os.getenv('BREAK_EVEN_PERCENTAGE', '1.5'))

# Risk Management
MAX_DAILY_TRADES = int(os.getenv('MAX_DAILY_TRADES', '10'))
MAX_DAILY_LOSS = float(os.getenv('MAX_DAILY_LOSS', '50'))
MAX_WEEKLY_LOSS = float(os.getenv('MAX_WEEKLY_LOSS', '200'))
MAX_MONTHLY_LOSS = float(os.getenv('MAX_MONTHLY_LOSS', '500'))
COOLDOWN_PERIOD = int(os.getenv('COOLDOWN_PERIOD', '300'))  # 5 menit dalam detik

# Drawdown Protection
MAX_DRAWDOWN_PERCENTAGE = float(os.getenv('MAX_DRAWDOWN_PERCENTAGE', '15.0'))  # Max 15% drawdown
DRAWDOWN_COOLDOWN_HOURS = int(os.getenv('DRAWDOWN_COOLDOWN_HOURS', '24'))  # 24 jam cooldown after max drawdown

# Profit Taking
PROFIT_TAKING_ENABLED = os.getenv('PROFIT_TAKING_ENABLED', 'true').lower() == 'true'
PROFIT_TAKING_PERCENTAGE = float(os.getenv('PROFIT_TAKING_PERCENTAGE', '20.0'))  # Take 20% profit at target
SCALING_OUT_ENABLED = os.getenv('SCALING_OUT_ENABLED', 'true').lower() == 'true'
SCALING_OUT_LEVELS = os.getenv('SCALING_OUT_LEVELS', '25,50,75').split(',')  # Scale out at 25%, 50%, 75%

# Volatility Management
VOLATILITY_ADJUSTMENT_ENABLED = os.getenv('VOLATILITY_ADJUSTMENT_ENABLED', 'true').lower() == 'true'
HIGH_VOLATILITY_THRESHOLD = float(os.getenv('HIGH_VOLATILITY_THRESHOLD', '50.0'))  # 50% volatility threshold
LOW_VOLATILITY_THRESHOLD = float(os.getenv('LOW_VOLATILITY_THRESHOLD', '10.0'))   # 10% volatility threshold

# Market Condition Filters
MARKET_CONDITION_FILTERS = os.getenv('MARKET_CONDITION_FILTERS', 'true').lower() == 'true'
BEAR_MARKET_RISK_REDUCTION = float(os.getenv('BEAR_MARKET_RISK_REDUCTION', '0.5'))  # Reduce risk by 50% in bear market
BULL_MARKET_RISK_INCREASE = float(os.getenv('BULL_MARKET_RISK_INCREASE', '1.2'))   # Increase risk by 20% in bull market

# Konfigurasi Strategi
RSI_PERIOD = int(os.getenv('RSI_PERIOD', '14'))
RSI_OVERBOUGHT = int(os.getenv('RSI_OVERBOUGHT', '70'))
RSI_OVERSOLD = int(os.getenv('RSI_OVERSOLD', '30'))
MACD_FAST = int(os.getenv('MACD_FAST', '12'))
MACD_SLOW = int(os.getenv('MACD_SLOW', '26'))
MACD_SIGNAL = int(os.getenv('MACD_SIGNAL', '9'))

# Konfigurasi Data Source (untuk market data)
MARKET_DATA_SOURCE = os.getenv('MARKET_DATA_SOURCE', 'coingecko')  # coingecko, binance

# Symbol Filtering
EXCLUDED_SYMBOLS = os.getenv('EXCLUDED_SYMBOLS', 'USDT/USDT,USDC/USDT').split(',')  # Symbols yang di-exclude
INCLUDED_CATEGORIES = os.getenv('INCLUDED_CATEGORIES', 'all').split(',')  # all, defi, gaming, layer1, memecoin