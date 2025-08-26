"""
Trading Bot - Main Package
"""

__version__ = "1.0.0"
__author__ = "Trading Bot Team"
__description__ = "Automated cryptocurrency trading bot with Telegram interface"

# Import main components
from .core.TradingBot import TradingBot
from .core.TelegramBot import TelegramTradingBot
from .core.Main import TradingBotRunner

# Import clients
from .clients.MarketDataClient import MarketDataClient
from .clients.OKXWalletClient import OKXWalletClient
from .clients.HyperliquidClient import HyperliquidClient

# Import strategies and management
from .strategies.TradingStrategy import TradingStrategy
from .management.MoneyManagement import MoneyManagement, MarketCondition, TradeRisk

__all__ = [
    'TradingBot',
    'TelegramTradingBot', 
    'TradingBotRunner',
    'MarketDataClient',
    'OKXWalletClient',
    'HyperliquidClient',
    'TradingStrategy',
    'MoneyManagement',
    'MarketCondition',
    'TradeRisk'
]