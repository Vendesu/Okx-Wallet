import requests
import json
import logging
import time
from typing import Dict, List, Optional
from config import HYPERLIQUID_PRIVATE_KEY, HYPERLIQUID_BASE_URL
import hmac
import hashlib
import base64

class HyperliquidClient:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.base_url = HYPERLIQUID_BASE_URL
        self.private_key = HYPERLIQUID_PRIVATE_KEY
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'TradingBot/1.0'
        })
        
    def _generate_signature(self, data: str) -> str:
        """Generate signature untuk autentikasi"""
        try:
            if not self.private_key:
                raise ValueError("Private key tidak tersedia")
                
            # Convert private key to bytes
            private_key_bytes = self.private_key.encode('utf-8')
            
            # Create HMAC signature
            signature = hmac.new(
                private_key_bytes,
                data.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            return signature
            
        except Exception as e:
            self.logger.error(f"Gagal generate signature: {e}")
            return ""
            
    def get_market_info(self) -> Optional[Dict]:
        """Mendapatkan informasi market dari Hyperliquid"""
        try:
            url = f"{self.base_url}/info"
            response = self.session.get(url)
            
            if response.status_code == 200:
                return response.json()
            else:
                self.logger.error(f"Gagal mendapatkan market info: {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error saat mendapatkan market info: {e}")
            return None
            
    def get_orderbook(self, coin: str) -> Optional[Dict]:
        """Mendapatkan orderbook untuk coin tertentu"""
        try:
            url = f"{self.base_url}/info"
            payload = {
                "type": "orderBook",
                "coin": coin
            }
            
            response = self.session.post(url, json=payload)
            
            if response.status_code == 200:
                return response.json()
            else:
                self.logger.error(f"Gagal mendapatkan orderbook untuk {coin}: {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error saat mendapatkan orderbook: {e}")
            return None
            
    def get_user_state(self) -> Optional[Dict]:
        """Mendapatkan state user dari Hyperliquid"""
        try:
            if not self.private_key:
                self.logger.warning("Private key tidak tersedia untuk user state")
                return None
                
            url = f"{self.base_url}/info"
            payload = {
                "type": "clearinghouseState",
                "user": self.private_key
            }
            
            response = self.session.post(url, json=payload)
            
            if response.status_code == 200:
                return response.json()
            else:
                self.logger.error(f"Gagal mendapatkan user state: {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error saat mendapatkan user state: {e}")
            return None
            
    def place_order(self, coin: str, side: str, size: float, 
                   price: Optional[float] = None, order_type: str = "LIMIT") -> Optional[Dict]:
        """Place order di Hyperliquid"""
        try:
            if not self.private_key:
                self.logger.error("Private key tidak tersedia untuk trading")
                return None
                
            url = f"{self.base_url}/exchange"
            
            # Prepare order data
            order_data = {
                "type": "order",
                "coin": coin,
                "side": side.upper(),
                "size": str(size),
                "orderType": order_type.upper()
            }
            
            if price and order_type.upper() == "LIMIT":
                order_data["price"] = str(price)
                
            # Generate signature
            signature = self._generate_signature(json.dumps(order_data))
            if not signature:
                return None
                
            # Add signature to headers
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {signature}'
            }
            
            response = self.session.post(url, json=order_data, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                self.logger.info(f"Order berhasil ditempatkan: {result}")
                return result
            else:
                self.logger.error(f"Gagal place order: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error saat place order: {e}")
            return None
            
    def cancel_order(self, coin: str, order_id: str) -> Optional[Dict]:
        """Cancel order di Hyperliquid"""
        try:
            if not self.private_key:
                self.logger.error("Private key tidak tersedia untuk cancel order")
                return None
                
            url = f"{self.base_url}/exchange"
            
            cancel_data = {
                "type": "cancel",
                "coin": coin,
                "orderId": order_id
            }
            
            # Generate signature
            signature = self._generate_signature(json.dumps(cancel_data))
            if not signature:
                return None
                
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {signature}'
            }
            
            response = self.session.post(url, json=cancel_data, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                self.logger.info(f"Order berhasil di-cancel: {result}")
                return result
            else:
                self.logger.error(f"Gagal cancel order: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error saat cancel order: {e}")
            return None
            
    def get_open_orders(self) -> Optional[List[Dict]]:
        """Mendapatkan daftar open orders"""
        try:
            if not self.private_key:
                self.logger.warning("Private key tidak tersedia untuk open orders")
                return None
                
            url = f"{self.base_url}/info"
            payload = {
                "type": "openOrders",
                "user": self.private_key
            }
            
            response = self.session.post(url, json=payload)
            
            if response.status_code == 200:
                return response.json()
            else:
                self.logger.error(f"Gagal mendapatkan open orders: {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error saat mendapatkan open orders: {e}")
            return None
            
    def get_positions(self) -> Optional[List[Dict]]:
        """Mendapatkan daftar posisi yang sedang dibuka"""
        try:
            if not self.private_key:
                self.logger.warning("Private key tidak tersedia untuk positions")
                return None
                
            url = f"{self.base_url}/info"
            payload = {
                "type": "userFills",
                "user": self.private_key
            }
            
            response = self.session.post(url, json=payload)
            
            if response.status_code == 200:
                return response.json()
            else:
                self.logger.error(f"Gagal mendapatkan positions: {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error saat mendapatkan positions: {e}")
            return None
            
    def get_trade_history(self, limit: int = 100) -> Optional[List[Dict]]:
        """Mendapatkan history trading"""
        try:
            if not self.private_key:
                self.logger.warning("Private key tidak tersedia untuk trade history")
                return None
                
            url = f"{self.base_url}/info"
            payload = {
                "type": "userFills",
                "user": self.private_key,
                "limit": limit
            }
            
            response = self.session.post(url, json=payload)
            
            if response.status_code == 200:
                return response.json()
            else:
                self.logger.error(f"Gagal mendapatkan trade history: {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error saat mendapatkan trade history: {e}")
            return None
            
    def get_market_price(self, coin: str) -> Optional[float]:
        """Mendapatkan harga market untuk coin tertentu"""
        try:
            ticker = self.get_market_info()
            if ticker and 'data' in ticker:
                for market in ticker['data']:
                    if market.get('name') == coin:
                        return float(market.get('markPrice', 0))
            return None
            
        except Exception as e:
            self.logger.error(f"Error saat mendapatkan market price: {e}")
            return None
            
    def test_connection(self) -> bool:
        """Test koneksi ke Hyperliquid"""
        try:
            market_info = self.get_market_info()
            if market_info:
                self.logger.info("Koneksi Hyperliquid berhasil")
                return True
            else:
                self.logger.error("Koneksi Hyperliquid gagal")
                return False
                
        except Exception as e:
            self.logger.error(f"Error saat test koneksi Hyperliquid: {e}")
            return False