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
        
        # Cache untuk symbols
        self.available_symbols_cache = {}
        self.last_symbols_update = None
        self.symbols_cache_duration = 3600  # 1 jam
        
    def _rate_limit(self):
        """Rate limiting untuk API calls"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            time.sleep(sleep_time)
            
        self.last_request_time = time.time()
        
    def get_all_available_symbols(self, force_refresh: bool = False) -> List[str]:
        """Get semua available symbols secara otomatis"""
        try:
            # Check cache
            if (not force_refresh and 
                self.available_symbols_cache and 
                self.last_symbols_update and
                (time.time() - self.last_symbols_update) < self.symbols_cache_duration):
                
                self.logger.info(f"✅ Menggunakan cached symbols: {len(self.available_symbols_cache)} symbols")
                return list(self.available_symbols_cache.keys())
                
            # Fetch fresh symbols
            if self.data_source == 'coingecko':
                symbols = self._get_coingecko_all_symbols()
            elif self.data_source == 'binance':
                symbols = self._get_binance_all_symbols()
            else:
                symbols = self._get_coingecko_all_symbols()
                
            if symbols:
                # Update cache
                self.available_symbols_cache = {symbol: True for symbol in symbols}
                self.last_symbols_update = time.time()
                
                self.logger.info(f"✅ Berhasil fetch {len(symbols)} symbols dari {self.data_source}")
                return symbols
            else:
                self.logger.warning("⚠️ Tidak ada symbols yang ditemukan")
                return []
                
        except Exception as e:
            self.logger.error(f"❌ Error get all symbols: {e}")
            return []
            
    def _get_coingecko_all_symbols(self) -> List[str]:
        """Get semua symbols dari CoinGecko"""
        try:
            # Get top 1000 coins by market cap
            url = "https://api.coingecko.com/api/v3/coins/markets"
            params = {
                'vs_currency': 'usd',
                'order': 'market_cap_desc',
                'per_page': 1000,
                'page': 1,
                'sparkline': False
            }
            
            self._rate_limit()
            response = self.session.get(url, params=params)
            
            if response.status_code == 200:
                coins = response.json()
                symbols = []
                
                for coin in coins:
                    # Convert ke format trading pair
                    symbol = f"{coin['symbol'].upper()}/USDT"
                    symbols.append(symbol)
                    
                # Tambahkan beberapa stablecoins dan pairs populer
                additional_pairs = [
                    'BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'ADA/USDT',
                    'SOL/USDT', 'DOT/USDT', 'LINK/USDT', 'UNI/USDT',
                    'MATIC/USDT', 'AVAX/USDT', 'ATOM/USDT', 'LTC/USDT',
                    'BCH/USDT', 'XRP/USDT', 'DOGE/USDT', 'SHIB/USDT'
                ]
                
                # Gabungkan dan remove duplicates
                all_symbols = list(set(symbols + additional_pairs))
                all_symbols.sort()  # Sort alphabetically
                
                return all_symbols
            else:
                self.logger.error(f"CoinGecko API error: {response.status_code}")
                return []
                
        except Exception as e:
            self.logger.error(f"Error saat get CoinGecko symbols: {e}")
            return []
            
    def _get_binance_all_symbols(self) -> List[str]:
        """Get semua symbols dari Binance"""
        try:
            # Get exchange info
            url = "https://api.binance.com/api/v3/exchangeInfo"
            
            self._rate_limit()
            response = self.session.get(url)
            
            if response.status_code == 200:
                data = response.json()
                symbols = []
                
                for symbol_info in data.get('symbols', []):
                    symbol = symbol_info['symbol']
                    status = symbol_info['status']
                    quote_asset = symbol_info['quoteAsset']
                    
                    # Hanya USDT pairs yang aktif
                    if (status == 'TRADING' and 
                        quote_asset == 'USDT' and 
                        symbol.endswith('USDT')):
                        
                        # Convert ke format standard (BTC/USDT)
                        base_asset = symbol.replace('USDT', '')
                        trading_pair = f"{base_asset}/USDT"
                        symbols.append(trading_pair)
                        
                # Sort alphabetically
                symbols.sort()
                return symbols
            else:
                self.logger.error(f"Binance API error: {response.status_code}")
                return []
                
        except Exception as e:
            self.logger.error(f"Error saat get Binance symbols: {e}")
            return []
            
    def get_trending_symbols(self, limit: int = 20) -> List[str]:
        """Get trending symbols berdasarkan volume dan price change"""
        try:
            if self.data_source == 'coingecko':
                return self._get_coingecko_trending_symbols(limit)
            elif self.data_source == 'binance':
                return self._get_binance_trending_symbols(limit)
            else:
                return self._get_coingecko_trending_symbols(limit)
                
        except Exception as e:
            self.logger.error(f"Error saat get trending symbols: {e}")
            return []
            
    def _get_coingecko_trending_symbols(self, limit: int = 20) -> List[str]:
        """Get trending symbols dari CoinGecko"""
        try:
            # Get trending coins
            url = "https://api.coingecko.com/api/v3/search/trending"
            
            self._rate_limit()
            response = self.session.get(url)
            
            if response.status_code == 200:
                data = response.json()
                trending_symbols = []
                
                for coin in data.get('coins', [])[:limit]:
                    symbol = f"{coin['item']['symbol'].upper()}/USDT"
                    trending_symbols.append(symbol)
                    
                return trending_symbols
            else:
                return []
                
        except Exception as e:
            self.logger.error(f"Error saat get CoinGecko trending: {e}")
            return []
            
    def _get_binance_trending_symbols(self, limit: int = 20) -> List[str]:
        """Get trending symbols dari Binance berdasarkan 24h volume"""
        try:
            # Get 24hr ticker untuk semua symbols
            url = "https://api.binance.com/api/v3/ticker/24hr"
            
            self._rate_limit()
            response = self.session.get(url)
            
            if response.status_code == 200:
                tickers = response.json()
                
                # Filter USDT pairs dan sort berdasarkan volume
                usdt_tickers = []
                for ticker in tickers:
                    if ticker['symbol'].endswith('USDT'):
                        volume = float(ticker['volume'])
                        price_change = float(ticker['priceChangePercent'])
                        
                        usdt_tickers.append({
                            'symbol': ticker['symbol'].replace('USDT', '/USDT'),
                            'volume': volume,
                            'price_change': price_change
                        })
                        
                # Sort berdasarkan volume (descending)
                usdt_tickers.sort(key=lambda x: x['volume'], reverse=True)
                
                # Ambil top symbols
                trending_symbols = [ticker['symbol'] for ticker in usdt_tickers[:limit]]
                return trending_symbols
            else:
                return []
                
        except Exception as e:
            self.logger.error(f"Error saat get Binance trending: {e}")
            return []
            
    def get_high_volume_symbols(self, min_volume_usd: float = 1000000, limit: int = 50) -> List[str]:
        """Get symbols dengan volume tinggi"""
        try:
            if self.data_source == 'coingecko':
                return self._get_coingecko_high_volume_symbols(min_volume_usd, limit)
            elif self.data_source == 'binance':
                return self._get_binance_high_volume_symbols(min_volume_usd, limit)
            else:
                return self._get_coingecko_high_volume_symbols(min_volume_usd, limit)
                
        except Exception as e:
            self.logger.error(f"Error saat get high volume symbols: {e}")
            return []
            
    def _get_coingecko_high_volume_symbols(self, min_volume_usd: float, limit: int) -> List[str]:
        """Get high volume symbols dari CoinGecko"""
        try:
            # Get top coins by market cap
            url = "https://api.coingecko.com/api/v3/coins/markets"
            params = {
                'vs_currency': 'usd',
                'order': 'volume_desc',
                'per_page': limit * 2,  # Get more to filter
                'page': 1,
                'sparkline': False
            }
            
            self._rate_limit()
            response = self.session.get(url, params=params)
            
            if response.status_code == 200:
                coins = response.json()
                high_volume_symbols = []
                
                for coin in coins:
                    volume_24h = coin.get('total_volume', 0)
                    if volume_24h >= min_volume_usd:
                        symbol = f"{coin['symbol'].upper()}/USDT"
                        high_volume_symbols.append(symbol)
                        
                        if len(high_volume_symbols) >= limit:
                            break
                            
                return high_volume_symbols
            else:
                return []
                
        except Exception as e:
            self.logger.error(f"Error saat get CoinGecko high volume: {e}")
            return []
            
    def _get_binance_high_volume_symbols(self, min_volume_usd: float, limit: int) -> List[str]:
        """Get high volume symbols dari Binance"""
        try:
            # Get 24hr ticker
            url = "https://api.binance.com/api/v3/ticker/24hr"
            
            self._rate_limit()
            response = self.session.get(url)
            
            if response.status_code == 200:
                tickers = response.json()
                
                # Filter USDT pairs dan sort berdasarkan volume
                usdt_tickers = []
                for ticker in tickers:
                    if ticker['symbol'].endswith('USDT'):
                        volume = float(ticker['volume'])
                        price = float(ticker['lastPrice'])
                        volume_usd = volume * price
                        
                        if volume_usd >= min_volume_usd:
                            symbol = ticker['symbol'].replace('USDT', '/USDT')
                            usdt_tickers.append({
                                'symbol': symbol,
                                'volume_usd': volume_usd
                            })
                            
                # Sort berdasarkan volume USD (descending)
                usdt_tickers.sort(key=lambda x: x['volume_usd'], reverse=True)
                
                # Ambil top symbols
                high_volume_symbols = [ticker['symbol'] for ticker in usdt_tickers[:limit]]
                return high_volume_symbols
            else:
                return []
                
        except Exception as e:
            self.logger.error(f"Error saat get Binance high volume: {e}")
            return []
            
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