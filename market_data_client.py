import requests
import logging
import time
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from config import MARKET_DATA_SOURCE

class MarketDataClient:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.data_source = MARKET_DATA_SOURCE
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'TradingBot/1.0'
        })
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 1.0  # 1 second between requests
        
    def _rate_limit(self):
        """Rate limiting untuk API calls"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            time.sleep(sleep_time)
            
        self.last_request_time = time.time()
        
    def get_market_data(self, symbol: str, timeframe: str = '1h', limit: int = 100) -> Optional[Dict]:
        """Mendapatkan market data berdasarkan data source"""
        try:
            if self.data_source == 'coingecko':
                return self._get_coingecko_data(symbol, timeframe, limit)
            elif self.data_source == 'binance':
                return self._get_binance_data(symbol, timeframe, limit)
            else:
                # Default ke CoinGecko
                return self._get_coingecko_data(symbol, timeframe, limit)
                
        except Exception as e:
            self.logger.error(f"Gagal mendapatkan market data untuk {symbol}: {e}")
            return None
            
    def _get_coingecko_data(self, symbol: str, timeframe: str = '1h', limit: int = 100) -> Optional[Dict]:
        """Mendapatkan data dari CoinGecko API"""
        try:
            # Convert symbol ke CoinGecko format
            coin_id = self._symbol_to_coingecko_id(symbol)
            if not coin_id:
                return None
                
            # Get historical data
            days = self._timeframe_to_days(timeframe, limit)
            
            url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
            params = {
                'vs_currency': 'usd',
                'days': days,
                'interval': 'hourly' if timeframe == '1h' else 'daily'
            }
            
            self._rate_limit()
            response = self.session.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract prices and volumes
                prices = data.get('prices', [])
                volumes = data.get('total_volumes', [])
                
                if not prices:
                    return None
                    
                # Convert to our format
                formatted_data = {
                    'prices': [float(price[1]) for price in prices],
                    'volumes': [float(volume[1]) for volume in volumes],
                    'timestamps': [price[0] for price in prices],
                    'highs': [float(price[1]) for price in prices],  # Simplified
                    'lows': [float(price[1]) for price in prices],   # Simplified
                    'opens': [float(price[1]) for price in prices]   # Simplified
                }
                
                return formatted_data
            else:
                self.logger.error(f"CoinGecko API error: {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error saat get CoinGecko data: {e}")
            return None
            
    def _get_binance_data(self, symbol: str, timeframe: str = '1h', limit: int = 100) -> Optional[Dict]:
        """Mendapatkan data dari Binance API"""
        try:
            # Convert symbol ke Binance format
            binance_symbol = symbol.replace('/', '')
            
            # Convert timeframe ke Binance format
            interval = self._timeframe_to_binance_interval(timeframe)
            
            url = f"https://api.binance.com/api/v3/klines"
            params = {
                'symbol': binance_symbol,
                'interval': interval,
                'limit': limit
            }
            
            self._rate_limit()
            response = self.session.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                # Binance klines format: [open_time, open, high, low, close, volume, close_time, ...]
                formatted_data = {
                    'prices': [float(candle[4]) for candle in data],      # Close prices
                    'volumes': [float(candle[5]) for candle in data],     # Volumes
                    'highs': [float(candle[2]) for candle in data],       # High prices
                    'lows': [float(candle[3]) for candle in data],        # Low prices
                    'opens': [float(candle[1]) for candle in data],       # Open prices
                    'timestamps': [candle[0] for candle in data]          # Open time
                }
                
                return formatted_data
            else:
                self.logger.error(f"Binance API error: {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error saat get Binance data: {e}")
            return None
            
    def _symbol_to_coingecko_id(self, symbol: str) -> Optional[str]:
        """Convert trading symbol ke CoinGecko coin ID"""
        # Mapping common symbols ke CoinGecko IDs
        symbol_mapping = {
            'BTC/USDT': 'bitcoin',
            'ETH/USDT': 'ethereum',
            'SOL/USDT': 'solana',
            'ADA/USDT': 'cardano',
            'DOT/USDT': 'polkadot',
            'LINK/USDT': 'chainlink',
            'UNI/USDT': 'uniswap',
            'MATIC/USDT': 'matic-network',
            'AVAX/USDT': 'avalanche-2',
            'ATOM/USDT': 'cosmos',
            'LTC/USDT': 'litecoin',
            'BCH/USDT': 'bitcoin-cash',
            'XRP/USDT': 'ripple',
            'DOGE/USDT': 'dogecoin',
            'SHIB/USDT': 'shiba-inu'
        }
        
        return symbol_mapping.get(symbol, None)
        
    def _timeframe_to_days(self, timeframe: str, limit: int) -> int:
        """Convert timeframe ke jumlah hari untuk CoinGecko"""
        if timeframe == '1h':
            return max(1, limit // 24)  # 24 hours per day
        elif timeframe == '4h':
            return max(1, limit // 6)   # 6 periods per day
        elif timeframe == '1d':
            return limit
        else:
            return 30  # Default 30 days
            
    def _timeframe_to_binance_interval(self, timeframe: str) -> str:
        """Convert timeframe ke Binance interval format"""
        mapping = {
            '1m': '1m',
            '5m': '5m',
            '15m': '15m',
            '30m': '30m',
            '1h': '1h',
            '4h': '4h',
            '1d': '1d'
        }
        return mapping.get(timeframe, '1h')
        
    def get_current_price(self, symbol: str) -> Optional[float]:
        """Mendapatkan harga current untuk symbol tertentu"""
        try:
            if self.data_source == 'coingecko':
                return self._get_coingecko_current_price(symbol)
            elif self.data_source == 'binance':
                return self._get_binance_current_price(symbol)
            else:
                return self._get_coingecko_current_price(symbol)
                
        except Exception as e:
            self.logger.error(f"Error saat get current price untuk {symbol}: {e}")
            return None
            
    def _get_coingecko_current_price(self, symbol: str) -> Optional[float]:
        """Mendapatkan current price dari CoinGecko"""
        try:
            coin_id = self._symbol_to_coingecko_id(symbol)
            if not coin_id:
                return None
                
            url = f"https://api.coingecko.com/api/v3/simple/price"
            params = {
                'ids': coin_id,
                'vs_currencies': 'usd'
            }
            
            self._rate_limit()
            response = self.session.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                return data.get(coin_id, {}).get('usd')
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"Error saat get CoinGecko current price: {e}")
            return None
            
    def _get_binance_current_price(self, symbol: str) -> Optional[float]:
        """Mendapatkan current price dari Binance"""
        try:
            binance_symbol = symbol.replace('/', '')
            
            url = f"https://api.binance.com/api/v3/ticker/price"
            params = {'symbol': binance_symbol}
            
            self._rate_limit()
            response = self.session.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                return float(data.get('price', 0))
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"Error saat get Binance current price: {e}")
            return None
            
    def get_market_info(self, symbol: str) -> Optional[Dict]:
        """Mendapatkan informasi market untuk symbol tertentu"""
        try:
            if self.data_source == 'coingecko':
                return self._get_coingecko_market_info(symbol)
            elif self.data_source == 'binance':
                return self._get_binance_market_info(symbol)
            else:
                return self._get_coingecko_market_info(symbol)
                
        except Exception as e:
            self.logger.error(f"Error saat get market info untuk {symbol}: {e}")
            return None
            
    def _get_coingecko_market_info(self, symbol: str) -> Optional[Dict]:
        """Mendapatkan market info dari CoinGecko"""
        try:
            coin_id = self._symbol_to_coingecko_id(symbol)
            if not coin_id:
                return None
                
            url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
            
            self._rate_limit()
            response = self.session.get(url)
            
            if response.status_code == 200:
                data = response.json()
                market_data = data.get('market_data', {})
                
                return {
                    'symbol': symbol,
                    'name': data.get('name', ''),
                    'current_price': market_data.get('current_price', {}).get('usd', 0),
                    'market_cap': market_data.get('market_cap', {}).get('usd', 0),
                    'volume_24h': market_data.get('total_volume', {}).get('usd', 0),
                    'price_change_24h': market_data.get('price_change_24h', 0),
                    'price_change_percentage_24h': market_data.get('price_change_percentage_24h', 0),
                    'high_24h': market_data.get('high_24h', {}).get('usd', 0),
                    'low_24h': market_data.get('low_24h', {}).get('usd', 0)
                }
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"Error saat get CoinGecko market info: {e}")
            return None
            
    def _get_binance_market_info(self, symbol: str) -> Optional[Dict]:
        """Mendapatkan market info dari Binance"""
        try:
            binance_symbol = symbol.replace('/', '')
            
            # Get 24hr ticker
            url = f"https://api.binance.com/api/v3/ticker/24hr"
            params = {'symbol': binance_symbol}
            
            self._rate_limit()
            response = self.session.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                return {
                    'symbol': symbol,
                    'name': symbol,
                    'current_price': float(data.get('lastPrice', 0)),
                    'market_cap': 0,  # Binance doesn't provide market cap
                    'volume_24h': float(data.get('volume', 0)),
                    'price_change_24h': float(data.get('priceChange', 0)),
                    'price_change_percentage_24h': float(data.get('priceChangePercent', 0)),
                    'high_24h': float(data.get('highPrice', 0)),
                    'low_24h': float(data.get('lowPrice', 0))
                }
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"Error saat get Binance market info: {e}")
            return None
            
    def test_connection(self) -> bool:
        """Test koneksi ke market data source"""
        try:
            # Test dengan Bitcoin
            test_symbol = 'BTC/USDT'
            
            if self.data_source == 'coingecko':
                # Test CoinGecko
                price = self._get_coingecko_current_price(test_symbol)
                if price and price > 0:
                    self.logger.info(f"✅ CoinGecko connection berhasil, BTC price: ${price:,.2f}")
                    return True
                    
            elif self.data_source == 'binance':
                # Test Binance
                price = self._get_binance_current_price(test_symbol)
                if price and price > 0:
                    self.logger.info(f"✅ Binance connection berhasil, BTC price: ${price:,.2f}")
                    return True
                    
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Market data connection gagal: {e}")
            return False