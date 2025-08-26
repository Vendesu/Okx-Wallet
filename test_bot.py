#!/usr/bin/env python3
"""
Test script untuk memverifikasi semua komponen Trading Bot
"""

import asyncio
import logging
import sys
import os
from pathlib import Path

# Add current directory to Python path
sys.path.append(str(Path(__file__).parent))

from config import *
from trading_strategy import TradingStrategy
from okx_client import OKXClient
from hyperliquid_client import HyperliquidClient

class BotTester:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.strategy = TradingStrategy()
        self.okx_client = OKXClient()
        self.hyperliquid_client = HyperliquidClient()
        
    async def test_all_components(self):
        """Test semua komponen bot"""
        print("🧪 Memulai testing semua komponen Trading Bot...\n")
        
        results = []
        
        # Test 1: Config
        results.append(("Config", self.test_config()))
        
        # Test 2: Trading Strategy
        results.append(("Trading Strategy", self.test_trading_strategy()))
        
        # Test 3: OKX Client
        results.append(("OKX Client", await self.test_okx_client()))
        
        # Test 4: Hyperliquid Client
        results.append(("Hyperliquid Client", await self.test_hyperliquid_client()))
        
        # Test 5: Integration Test
        results.append(("Integration", self.test_integration()))
        
        # Print results
        print("\n📊 **Hasil Testing:**\n")
        for component, success in results:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{component}: {status}")
            
        # Summary
        passed = sum(1 for _, success in results if success)
        total = len(results)
        
        print(f"\n🎯 **Summary:** {passed}/{total} komponen berhasil")
        
        if passed == total:
            print("🎉 Semua komponen berfungsi dengan baik!")
            print("🚀 Bot siap digunakan!")
        else:
            print("⚠️ Beberapa komponen gagal. Silakan cek error di atas.")
            
        return passed == total
        
    def test_config(self):
        """Test konfigurasi"""
        try:
            print("🔧 Testing Config...")
            
            # Check required configs
            required_configs = [
                'TELEGRAM_TOKEN', 'TELEGRAM_CHAT_ID',
                'OKX_API_KEY', 'OKX_SECRET_KEY', 'OKX_PASSPHRASE',
                'HYPERLIQUID_PRIVATE_KEY'
            ]
            
            for config in required_configs:
                if not getattr(sys.modules['config'], config, None):
                    print(f"  ❌ {config} tidak tersedia")
                    return False
                    
            print("  ✅ Semua config tersedia")
            return True
            
        except Exception as e:
            print(f"  ❌ Error testing config: {e}")
            return False
            
    def test_trading_strategy(self):
        """Test trading strategy"""
        try:
            print("📊 Testing Trading Strategy...")
            
            # Test RSI calculation
            prices = [100, 101, 102, 101, 100, 99, 98, 97, 96, 95]
            rsi = self.strategy.calculate_rsi(prices, 5)
            print(f"  ✅ RSI calculation: {rsi:.2f}")
            
            # Test MACD calculation
            macd_line, signal_line, histogram = self.strategy.calculate_macd(prices)
            print(f"  ✅ MACD calculation: {macd_line:.4f}, {signal_line:.4f}, {histogram:.4f}")
            
            # Test Bollinger Bands
            upper, middle, lower = self.strategy.calculate_bollinger_bands(prices)
            print(f"  ✅ Bollinger Bands: {upper:.2f}, {middle:.2f}, {lower:.2f}")
            
            # Test sentiment analysis
            sentiment = self.strategy.analyze_market_sentiment(prices)
            print(f"  ✅ Sentiment analysis: {sentiment['sentiment']:.3f}, confidence: {sentiment['confidence']:.3f}")
            
            return True
            
        except Exception as e:
            print(f"  ❌ Error testing trading strategy: {e}")
            return False
            
    async def test_okx_client(self):
        """Test OKX client"""
        try:
            print("🏦 Testing OKX Client...")
            
            # Test connection
            if not self.okx_client.test_connection():
                print("  ❌ Koneksi OKX gagal")
                return False
                
            print("  ✅ Koneksi OKX berhasil")
            
            # Test market data (if API keys available)
            if OKX_API_KEY and OKX_API_KEY != "your_okx_api_key_here":
                try:
                    market_data = self.okx_client.get_market_data("BTC/USDT", "1h", 10)
                    if market_data:
                        print(f"  ✅ Market data berhasil: {len(market_data['prices'])} data points")
                    else:
                        print("  ⚠️ Market data kosong (mungkin API key invalid)")
                except Exception as e:
                    print(f"  ⚠️ Market data error: {e}")
            else:
                print("  ⚠️ OKX API key tidak dikonfigurasi")
                
            return True
            
        except Exception as e:
            print(f"  ❌ Error testing OKX client: {e}")
            return False
            
    async def test_hyperliquid_client(self):
        """Test Hyperliquid client"""
        try:
            print("🔗 Testing Hyperliquid Client...")
            
            # Test connection
            if not self.hyperliquid_client.test_connection():
                print("  ❌ Koneksi Hyperliquid gagal")
                return False
                
            print("  ✅ Koneksi Hyperliquid berhasil")
            
            # Test market info
            market_info = self.hyperliquid_client.get_market_info()
            if market_info:
                print(f"  ✅ Market info berhasil")
            else:
                print("  ⚠️ Market info kosong")
                
            return True
            
        except Exception as e:
            print(f"  ❌ Error testing Hyperliquid client: {e}")
            return False
            
    def test_integration(self):
        """Test integrasi antar komponen"""
        try:
            print("🔗 Testing Integration...")
            
            # Test strategy with mock data
            mock_market_data = {
                'BTC/USDT': {
                    'prices': [50000, 50100, 50200, 50150, 50050] * 20,  # 100 data points
                    'volumes': [1000, 1100, 1200, 1150, 1050] * 20
                }
            }
            
            signals = self.strategy.generate_trading_signals(mock_market_data)
            if signals:
                print(f"  ✅ Signal generation berhasil: {len(signals)} signals")
                for pair, signal in signals.items():
                    print(f"    - {pair}: {signal['decision']} (confidence: {signal['confidence']:.2f})")
            else:
                print("  ⚠️ Signal generation kosong")
                
            return True
            
        except Exception as e:
            print(f"  ❌ Error testing integration: {e}")
            return False

async def main():
    """Main function untuk testing"""
    print("🧪 Trading Bot Component Tester\n")
    
    # Check if .env exists
    if not os.path.exists('.env'):
        print("❌ File .env tidak ditemukan!")
        print("📝 Silakan copy .env.example ke .env dan isi dengan API keys yang sesuai")
        return
        
    try:
        # Create tester and run tests
        tester = BotTester()
        success = await tester.test_all_components()
        
        if success:
            print("\n🎉 **Testing selesai dengan sukses!**")
            print("🚀 Bot siap digunakan dengan python run_bot.py")
        else:
            print("\n⚠️ **Testing selesai dengan beberapa error**")
            print("🔧 Silakan perbaiki error sebelum menggunakan bot")
            
    except Exception as e:
        print(f"\n❌ **Fatal error saat testing:** {e}")
        print("🔍 Cek log untuk detail error")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Testing dihentikan oleh user")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)