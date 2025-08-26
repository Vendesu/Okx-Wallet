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

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from config import *
from strategies.TradingStrategy import TradingStrategy
from clients.OKXWalletClient import OKXWalletClient
from clients.HyperliquidClient import HyperliquidClient
from clients.MarketDataClient import MarketDataClient

class BotTester:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.strategy = TradingStrategy()
        self.okx_wallet = OKXWalletClient()
        self.hyperliquid_client = HyperliquidClient()
        self.market_data_client = MarketDataClient()
        
    async def test_all_components(self):
        """Test semua komponen bot"""
        print("🧪 Memulai testing semua komponen Trading Bot...\n")
        
        results = []
        
        # Test 1: Config
        results.append(("Config", self.test_config()))
        
        # Test 2: Trading Strategy
        results.append(("Trading Strategy", self.test_trading_strategy()))
        
        # Test 3: Market Data Client
        results.append(("Market Data Client", self.test_market_data_client()))
        
        # Test 4: OKX Wallet Client
        results.append(("OKX Wallet Client", await self.test_okx_wallet_client()))
        
        # Test 5: Hyperliquid Client
        results.append(("Hyperliquid Client", await self.test_hyperliquid_client()))
        
        # Test 6: Integration Test
        results.append(("Integration", self.test_integration()))
        
        # Test 7: Money Management
        results.append(("Money Management", self.test_money_management()))
        
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
                'OKX_WALLET_PRIVATE_KEY', 'OKX_WALLET_ADDRESS', 'OKX_NETWORK',
                'HYPERLIQUID_PRIVATE_KEY', 'MARKET_DATA_SOURCE'
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
            
    def test_market_data_client(self):
        """Test market data client"""
        try:
            print("📈 Testing Market Data Client...")
            
            # Test connection
            if not self.market_data_client.test_connection():
                print("  ❌ Koneksi market data gagal")
                return False
                
            print("  ✅ Koneksi market data berhasil")
            
            # Test get current price
            btc_price = self.market_data_client.get_current_price("BTC/USDT")
            if btc_price and btc_price > 0:
                print(f"  ✅ Current price berhasil: BTC = ${btc_price:,.2f}")
            else:
                print("  ⚠️ Current price kosong atau error")
                
            # Test get market data
            market_data = self.market_data_client.get_market_data("BTC/USDT", "1h", 10)
            if market_data and len(market_data.get('prices', [])) > 0:
                print(f"  ✅ Market data berhasil: {len(market_data['prices'])} data points")
            else:
                print("  ⚠️ Market data kosong")
                
            # Test get all available symbols
            all_symbols = self.market_data_client.get_all_available_symbols()
            if all_symbols and len(all_symbols) > 0:
                print(f"  ✅ All symbols berhasil: {len(all_symbols)} symbols")
                print(f"    Sample: {', '.join(all_symbols[:5])}")
            else:
                print("  ⚠️ All symbols kosong")
                
            # Test get trending symbols
            trending_symbols = self.market_data_client.get_trending_symbols(5)
            if trending_symbols and len(trending_symbols) > 0:
                print(f"  ✅ Trending symbols berhasil: {len(trending_symbols)} symbols")
                print(f"    Trending: {', '.join(trending_symbols[:5])}")
            else:
                print("  ⚠️ Trending symbols kosong")
                
            # Test get high volume symbols
            high_volume_symbols = self.market_data_client.get_high_volume_symbols(1000000, 5)
            if high_volume_symbols and len(high_volume_symbols) > 0:
                print(f"  ✅ High volume symbols berhasil: {len(high_volume_symbols)} symbols")
                print(f"    High Volume: {', '.join(high_volume_symbols[:5])}")
            else:
                print("  ⚠️ High volume symbols kosong")
                
            return True
            
        except Exception as e:
            print(f"  ❌ Error testing market data client: {e}")
            return False
            
    async def test_okx_wallet_client(self):
        """Test OKX wallet client"""
        try:
            print("🏦 Testing OKX Wallet Client...")
            
            # Test connection
            if not self.okx_wallet.test_connection():
                print("  ❌ Koneksi OKX Wallet gagal")
                return False
                
            print("  ✅ Koneksi OKX Wallet berhasil")
            
            # Test get balance (if private key available)
            if OKX_WALLET_PRIVATE_KEY and OKX_WALLET_PRIVATE_KEY != "your_okx_wallet_private_key_here":
                try:
                    balance = self.okx_wallet.get_balance()
                    if balance:
                        print(f"  ✅ Balance berhasil: {balance['token']} = {balance['balance']:.6f}")
                    else:
                        print("  ⚠️ Balance kosong (mungkin private key invalid)")
                except Exception as e:
                    print(f"  ⚠️ Balance error: {e}")
            else:
                print("  ⚠️ OKX Wallet private key tidak dikonfigurasi")
                
            return True
            
        except Exception as e:
            print(f"  ❌ Error testing OKX wallet client: {e}")
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

    def test_money_management(self):
        """Test money management system"""
        try:
            print("💰 Testing Money Management System...")
            
            from management.MoneyManagement import MoneyManagement, MarketCondition, TradeRisk
            
            mm = MoneyManagement()
            
            # Test position sizing
            balance = 1000
            entry_price = 100
            stop_loss_price = 98
            confidence = 0.8
            
            trade_risk = mm.calculate_position_size(
                balance=balance,
                entry_price=entry_price,
                stop_loss_price=stop_loss_price,
                confidence=confidence,
                volatility=20.0,
                market_condition=MarketCondition.BULL
            )
            
            if trade_risk:
                print(f"  ✅ Position sizing berhasil:")
                print(f"    └ Position Size: {trade_risk.position_size:.4f}")
                print(f"    └ Risk Amount: ${trade_risk.risk_amount:.2f}")
                print(f"    └ Risk Percentage: {trade_risk.risk_percentage:.1f}%")
                print(f"    └ Take Profit: ${trade_risk.take_profit_price:.2f}")
            else:
                print("  ❌ Position sizing gagal")
                return False
                
            # Test portfolio risk check
            active_positions = {
                'BTC/USDT': {'risk_amount': 20},
                'ETH/USDT': {'risk_amount': 15}
            }
            
            portfolio_risk = mm.check_portfolio_risk(active_positions, balance)
            if portfolio_risk:
                print(f"  ✅ Portfolio risk check berhasil:")
                print(f"    └ Risk Level: {portfolio_risk.get('risk_level', 'Unknown')}")
                print(f"    └ Risk Percentage: {portfolio_risk.get('risk_percentage', 0):.1f}%")
            else:
                print("  ❌ Portfolio risk check gagal")
                
            # Test correlation risk check
            correlation_risk = mm.check_correlation_risk(active_positions)
            if correlation_risk:
                print(f"  ✅ Correlation risk check berhasil:")
                sector_exposure = correlation_risk.get('sector_exposure', {})
                for sector, count in sector_exposure.items():
                    print(f"    └ {sector}: {count} positions")
            else:
                print("  ❌ Correlation risk check gagal")
                
            # Test drawdown calculation
            balance_history = [1000, 1050, 1020, 1100, 1080]
            drawdown_info = mm.calculate_drawdown(balance_history)
            if drawdown_info:
                print(f"  ✅ Drawdown calculation berhasil:")
                print(f"    └ Max Drawdown: ${drawdown_info.get('max_drawdown', 0):.2f}")
                print(f"    └ Max Drawdown %: {drawdown_info.get('max_drawdown_percentage', 0):.1f}%")
            else:
                print("  ❌ Drawdown calculation gagal")
                
            # Test stop trading check
            stop_trading = mm.should_stop_trading(balance, 1000, -60, -150)
            if stop_trading:
                print(f"  ✅ Stop trading check berhasil:")
                print(f"    └ Should Stop: {stop_trading.get('should_stop', False)}")
                if stop_trading.get('should_stop'):
                    print(f"    └ Reason: {stop_trading.get('reason', 'Unknown')}")
            else:
                print("  ❌ Stop trading check gagal")
                
            # Test portfolio metrics
            portfolio_metrics = mm.get_portfolio_metrics(balance, 1000)
            if portfolio_metrics:
                print(f"  ✅ Portfolio metrics berhasil:")
                print(f"    └ Total PnL: ${portfolio_metrics.total_pnl:.2f}")
                print(f"    └ Win Rate: {portfolio_metrics.win_rate:.1f}%")
            else:
                print("  ❌ Portfolio metrics gagal")
                
            # Test money management summary
            mm_summary = mm.get_money_management_summary()
            if mm_summary:
                print(f"  ✅ Money management summary berhasil:")
                print(f"    └ Enabled: {mm_summary.get('enabled', False)}")
                print(f"    └ Position Sizing: {mm_summary.get('position_sizing_method', 'Unknown')}")
            else:
                print("  ❌ Money management summary gagal")
                
            return True
            
        except Exception as e:
            print(f"  ❌ Error testing money management: {e}")
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