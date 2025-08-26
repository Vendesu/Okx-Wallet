import ccxt
import logging
from typing import Dict, List, Optional
from config import OKX_API_KEY, OKX_SECRET_KEY, OKX_PASSPHRASE, OKX_SANDBOX

class OKXClient:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.exchange = None
        self._initialize_exchange()
        
    def _initialize_exchange(self):
        """Inisialisasi koneksi ke OKX exchange"""
        try:
            self.exchange = ccxt.okx({
                'apiKey': OKX_API_KEY,
                'secret': OKX_SECRET_KEY,
                'password': OKX_PASSPHRASE,
                'sandbox': OKX_SANDBOX,
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'spot'
                }
            })
            
            if OKX_SANDBOX:
                self.exchange.set_sandbox_mode(True)
                
            self.logger.info("OKX client berhasil diinisialisasi")
            
        except Exception as e:
            self.logger.error(f"Gagal menginisialisasi OKX client: {e}")
            raise
            
    def get_market_data(self, symbol: str, timeframe: str = '1h', limit: int = 100) -> Optional[Dict]:
        """Mendapatkan data market dari OKX"""
        try:
            if not self.exchange:
                self._initialize_exchange()
                
            # Fetch OHLCV data
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            
            if not ohlcv:
                return None
                
            # Convert to structured format
            data = {
                'prices': [float(candle[4]) for candle in ohlcv],  # Close prices
                'volumes': [float(candle[5]) for candle in ohlcv],  # Volumes
                'highs': [float(candle[2]) for candle in ohlcv],   # High prices
                'lows': [float(candle[3]) for candle in ohlcv],    # Low prices
                'opens': [float(candle[1]) for candle in ohlcv],   # Open prices
                'timestamps': [candle[0] for candle in ohlcv]      # Timestamps
            }
            
            return data
            
        except Exception as e:
            self.logger.error(f"Gagal mendapatkan data market untuk {symbol}: {e}")
            return None
            
    def get_balance(self) -> Optional[Dict]:
        """Mendapatkan balance dari OKX account"""
        try:
            if not self.exchange:
                self._initialize_exchange()
                
            balance = self.exchange.fetch_balance()
            
            # Filter hanya balance yang ada
            available_balance = {}
            for currency, info in balance.items():
                if info['free'] > 0 or info['used'] > 0:
                    available_balance[currency] = {
                        'free': float(info['free']),
                        'used': float(info['used']),
                        'total': float(info['total'])
                    }
                    
            return available_balance
            
        except Exception as e:
            self.logger.error(f"Gagal mendapatkan balance: {e}")
            return None
            
    def get_ticker(self, symbol: str) -> Optional[Dict]:
        """Mendapatkan ticker information untuk symbol tertentu"""
        try:
            if not self.exchange:
                self._initialize_exchange()
                
            ticker = self.exchange.fetch_ticker(symbol)
            
            return {
                'symbol': ticker['symbol'],
                'last': float(ticker['last']),
                'bid': float(ticker['bid']),
                'ask': float(ticker['ask']),
                'high': float(ticker['high']),
                'low': float(ticker['low']),
                'volume': float(ticker['baseVolume']),
                'change': float(ticker['change']),
                'change_percentage': float(ticker['percentage'])
            }
            
        except Exception as e:
            self.logger.error(f"Gagal mendapatkan ticker untuk {symbol}: {e}")
            return None
            
    def get_order_book(self, symbol: str, limit: int = 20) -> Optional[Dict]:
        """Mendapatkan order book untuk symbol tertentu"""
        try:
            if not self.exchange:
                self._initialize_exchange()
                
            order_book = self.exchange.fetch_order_book(symbol, limit)
            
            return {
                'bids': [[float(price), float(amount)] for price, amount in order_book['bids']],
                'asks': [[float(price), float(amount)] for price, amount in order_book['asks']],
                'timestamp': order_book['timestamp'],
                'datetime': order_book['datetime']
            }
            
        except Exception as e:
            self.logger.error(f"Gagal mendapatkan order book untuk {symbol}: {e}")
            return None
            
    def get_recent_trades(self, symbol: str, limit: int = 50) -> Optional[List[Dict]]:
        """Mendapatkan recent trades untuk symbol tertentu"""
        try:
            if not self.exchange:
                self._initialize_exchange()
                
            trades = self.exchange.fetch_trades(symbol, limit=limit)
            
            formatted_trades = []
            for trade in trades:
                formatted_trades.append({
                    'id': trade['id'],
                    'timestamp': trade['timestamp'],
                    'datetime': trade['datetime'],
                    'symbol': trade['symbol'],
                    'side': trade['side'],
                    'amount': float(trade['amount']),
                    'price': float(trade['price']),
                    'cost': float(trade['cost'])
                })
                
            return formatted_trades
            
        except Exception as e:
            self.logger.error(f"Gagal mendapatkan recent trades untuk {symbol}: {e}")
            return None
            
    def get_markets(self) -> Optional[List[str]]:
        """Mendapatkan daftar semua available markets"""
        try:
            if not self.exchange:
                self._initialize_exchange()
                
            markets = self.exchange.load_markets()
            return list(markets.keys())
            
        except Exception as e:
            self.logger.error(f"Gagal mendapatkan markets: {e}")
            return None
            
    def test_connection(self) -> bool:
        """Test koneksi ke OKX"""
        try:
            if not self.exchange:
                self._initialize_exchange()
                
            # Try to fetch time
            server_time = self.exchange.fetch_time()
            self.logger.info(f"Koneksi OKX berhasil, server time: {server_time}")
            return True
            
        except Exception as e:
            self.logger.error(f"Koneksi OKX gagal: {e}")
            return False