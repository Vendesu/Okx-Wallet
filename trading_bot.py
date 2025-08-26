import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd

from config import *
from trading_strategy import TradingStrategy
from okx_client import OKXClient
from hyperliquid_client import HyperliquidClient

class TradingBot:
    def __init__(self):
        self.logger = self._setup_logging()
        self.strategy = TradingStrategy()
        self.okx_client = OKXClient()
        self.hyperliquid_client = HyperliquidClient()
        
        # Trading state
        self.is_running = False
        self.daily_trades = 0
        self.daily_pnl = 0.0
        self.last_trade_time = None
        self.active_positions = {}
        self.trade_history = []
        
        # Market data cache
        self.market_data_cache = {}
        self.last_update_time = {}
        
    def _setup_logging(self) -> logging.Logger:
        """Setup logging untuk bot"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('trading_bot.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)
        
    async def start(self):
        """Start bot trading"""
        self.logger.info("🚀 Memulai Trading Bot...")
        
        # Test koneksi
        if not self._test_connections():
            self.logger.error("❌ Koneksi gagal, bot tidak bisa dimulai")
            return False
            
        self.is_running = True
        self.logger.info("✅ Bot trading berhasil dimulai!")
        
        # Reset daily counters
        self._reset_daily_counters()
        
        # Start main loop
        await self._main_loop()
        
    async def stop(self):
        """Stop bot trading"""
        self.logger.info("🛑 Menghentikan bot trading...")
        self.is_running = False
        
        # Close all positions
        await self._close_all_positions()
        
        self.logger.info("✅ Bot trading berhasil dihentikan")
        
    def _test_connections(self) -> bool:
        """Test koneksi ke semua exchange"""
        try:
            # Test OKX
            okx_ok = self.okx_client.test_connection()
            if not okx_ok:
                self.logger.error("❌ Koneksi OKX gagal")
                return False
                
            # Test Hyperliquid
            hyperliquid_ok = self.hyperliquid_client.test_connection()
            if not hyperliquid_ok:
                self.logger.error("❌ Koneksi Hyperliquid gagal")
                return False
                
            self.logger.info("✅ Semua koneksi berhasil")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error saat test koneksi: {e}")
            return False
            
    def _reset_daily_counters(self):
        """Reset counter harian"""
        self.daily_trades = 0
        self.daily_pnl = 0.0
        self.last_trade_time = None
        
    async def _main_loop(self):
        """Main loop bot trading"""
        while self.is_running:
            try:
                # Check daily limits
                if self._check_daily_limits():
                    self.logger.info("⏰ Daily limits tercapai, menunggu reset...")
                    await asyncio.sleep(3600)  # Sleep 1 jam
                    continue
                    
                # Update market data
                await self._update_market_data()
                
                # Generate trading signals
                signals = self._generate_signals()
                
                # Execute trading decisions
                if signals:
                    await self._execute_trading_signals(signals)
                    
                # Update positions
                await self._update_positions()
                
                # Risk management
                await self._risk_management()
                
                # Wait before next iteration
                await asyncio.sleep(COOLDOWN_PERIOD)
                
            except Exception as e:
                self.logger.error(f"❌ Error dalam main loop: {e}")
                await asyncio.sleep(60)  # Wait 1 menit sebelum retry
                
    def _check_daily_limits(self) -> bool:
        """Check apakah daily limits sudah tercapai"""
        # Check daily trades
        if self.daily_trades >= MAX_DAILY_TRADES:
            return True
            
        # Check daily loss
        if self.daily_pnl <= -MAX_DAILY_LOSS:
            return True
            
        # Check if it's a new day
        now = datetime.now()
        if self.last_trade_time and now.date() > self.last_trade_time.date():
            self._reset_daily_counters()
            
        return False
        
    async def _update_market_data(self):
        """Update market data untuk semua trading pairs"""
        for pair in TRADING_PAIRS:
            try:
                # Get data from OKX
                okx_data = self.okx_client.get_market_data(pair, '1h', 100)
                
                if okx_data:
                    self.market_data_cache[pair] = okx_data
                    self.last_update_time[pair] = datetime.now()
                    self.logger.debug(f"✅ Market data updated untuk {pair}")
                    
            except Exception as e:
                self.logger.error(f"❌ Error update market data untuk {pair}: {e}")
                
    def _generate_signals(self) -> Dict:
        """Generate trading signals berdasarkan market data"""
        try:
            if not self.market_data_cache:
                return {}
                
            # Filter data yang cukup fresh
            current_time = datetime.now()
            fresh_data = {}
            
            for pair, data in self.market_data_cache.items():
                if pair in self.last_update_time:
                    time_diff = (current_time - self.last_update_time[pair]).total_seconds()
                    if time_diff < 3600:  # Data harus kurang dari 1 jam
                        fresh_data[pair] = data
                        
            if not fresh_data:
                return {}
                
            # Generate signals
            signals = self.strategy.generate_trading_signals(fresh_data)
            return signals
            
        except Exception as e:
            self.logger.error(f"❌ Error generate signals: {e}")
            return {}
            
    async def _execute_trading_signals(self, signals: Dict):
        """Execute trading signals"""
        for pair, signal_data in signals.items():
            try:
                decision = signal_data['decision']
                confidence = signal_data['confidence']
                
                if decision == "HOLD":
                    continue
                    
                # Check cooldown
                if self._is_in_cooldown():
                    self.logger.info(f"⏰ Cooldown aktif, skip trading untuk {pair}")
                    continue
                    
                # Execute trade
                if decision in ["BUY", "STRONG_BUY"]:
                    await self._execute_buy_order(pair, signal_data)
                elif decision in ["SELL", "STRONG_SELL"]:
                    await self._execute_sell_order(pair, signal_data)
                    
            except Exception as e:
                self.logger.error(f"❌ Error execute signal untuk {pair}: {e}")
                
    def _is_in_cooldown(self) -> bool:
        """Check apakah bot sedang dalam cooldown"""
        if not self.last_trade_time:
            return False
            
        time_diff = (datetime.now() - self.last_trade_time).total_seconds()
        return time_diff < COOLDOWN_PERIOD
        
    async def _execute_buy_order(self, pair: str, signal_data: Dict):
        """Execute buy order"""
        try:
            # Get current price
            current_price = self._get_current_price(pair)
            if not current_price:
                return
                
            # Calculate position size
            balance = await self._get_available_balance()
            position_size = self.strategy.calculate_position_size(
                balance, 2.0, STOP_LOSS_PERCENTAGE, signal_data['confidence']
            )
            
            if position_size <= 0:
                self.logger.warning(f"⚠️ Position size terlalu kecil untuk {pair}")
                return
                
            # Place order di Hyperliquid
            coin = pair.split('/')[0]  # Extract coin name
            order_result = self.hyperliquid_client.place_order(
                coin=coin,
                side="BUY",
                size=position_size,
                price=current_price,
                order_type="LIMIT"
            )
            
            if order_result:
                self._record_trade(pair, "BUY", position_size, current_price, signal_data)
                self.logger.info(f"✅ Buy order berhasil untuk {pair}: {position_size} @ {current_price}")
            else:
                self.logger.error(f"❌ Buy order gagal untuk {pair}")
                
        except Exception as e:
            self.logger.error(f"❌ Error execute buy order untuk {pair}: {e}")
            
    async def _execute_sell_order(self, pair: str, signal_data: Dict):
        """Execute sell order"""
        try:
            # Check if we have position to sell
            if pair not in self.active_positions or self.active_positions[pair] <= 0:
                self.logger.info(f"ℹ️ Tidak ada posisi untuk dijual di {pair}")
                return
                
            # Get current price
            current_price = self._get_current_price(pair)
            if not current_price:
                return
                
            # Sell entire position
            position_size = self.active_positions[pair]
            coin = pair.split('/')[0]
            
            order_result = self.hyperliquid_client.place_order(
                coin=coin,
                side="SELL",
                size=position_size,
                price=current_price,
                order_type="LIMIT"
            )
            
            if order_result:
                self._record_trade(pair, "SELL", position_size, current_price, signal_data)
                self.logger.info(f"✅ Sell order berhasil untuk {pair}: {position_size} @ {current_price}")
            else:
                self.logger.error(f"❌ Sell order gagal untuk {pair}")
                
        except Exception as e:
            self.logger.error(f"❌ Error execute sell order untuk {pair}: {e}")
            
    def _get_current_price(self, pair: str) -> Optional[float]:
        """Get current price untuk pair tertentu"""
        try:
            if pair in self.market_data_cache and self.market_data_cache[pair]['prices']:
                return self.market_data_cache[pair]['prices'][-1]
            return None
        except Exception as e:
            self.logger.error(f"❌ Error get current price untuk {pair}: {e}")
            return None
            
    async def _get_available_balance(self) -> float:
        """Get available balance dari Hyperliquid"""
        try:
            user_state = self.hyperliquid_client.get_user_state()
            if user_state and 'data' in user_state:
                # Extract USDC balance
                for asset in user_state['data'].get('assetPositions', []):
                    if asset.get('coin') == 'USDC':
                        return float(asset.get('free', 0))
            return INITIAL_BALANCE
        except Exception as e:
            self.logger.error(f"❌ Error get balance: {e}")
            return INITIAL_BALANCE
            
    def _record_trade(self, pair: str, side: str, size: float, price: float, signal_data: Dict):
        """Record trade untuk tracking"""
        trade = {
            'timestamp': datetime.now(),
            'pair': pair,
            'side': side,
            'size': size,
            'price': price,
            'confidence': signal_data['confidence'],
            'sentiment': signal_data['sentiment']
        }
        
        self.trade_history.append(trade)
        self.daily_trades += 1
        self.last_trade_time = datetime.now()
        
        # Update active positions
        if side == "BUY":
            self.active_positions[pair] = self.active_positions.get(pair, 0) + size
        elif side == "SELL":
            self.active_positions[pair] = max(0, self.active_positions.get(pair, 0) - size)
            
    async def _update_positions(self):
        """Update status posisi yang sedang dibuka"""
        try:
            positions = self.hyperliquid_client.get_positions()
            if positions:
                # Update active positions
                for position in positions:
                    coin = position.get('coin')
                    size = float(position.get('size', 0))
                    
                    if size > 0:
                        pair = f"{coin}/USDT"
                        self.active_positions[pair] = size
                        
        except Exception as e:
            self.logger.error(f"❌ Error update positions: {e}")
            
    async def _risk_management(self):
        """Risk management untuk semua posisi"""
        for pair, position_size in self.active_positions.items():
            if position_size <= 0:
                continue
                
            try:
                current_price = self._get_current_price(pair)
                if not current_price:
                    continue
                    
                # Check stop loss
                if self._should_stop_loss(pair, current_price):
                    await self._execute_stop_loss(pair, current_price)
                    
                # Check take profit
                if self._should_take_profit(pair, current_price):
                    await self._execute_take_profit(pair, current_price)
                    
            except Exception as e:
                self.logger.error(f"❌ Error risk management untuk {pair}: {e}")
                
    def _should_stop_loss(self, pair: str, current_price: float) -> bool:
        """Check apakah harus execute stop loss"""
        # Implementation depends on your entry price tracking
        # For now, using a simple percentage-based approach
        return False  # Placeholder
        
    def _should_take_profit(self, pair: str, current_price: float) -> bool:
        """Check apakah harus execute take profit"""
        # Implementation depends on your entry price tracking
        # For now, using a simple percentage-based approach
        return False  # Placeholder
        
    async def _execute_stop_loss(self, pair: str, current_price: float):
        """Execute stop loss"""
        try:
            coin = pair.split('/')[0]
            position_size = self.active_positions[pair]
            
            order_result = self.hyperliquid_client.place_order(
                coin=coin,
                side="SELL",
                size=position_size,
                price=current_price,
                order_type="MARKET"
            )
            
            if order_result:
                self.logger.info(f"🛑 Stop loss executed untuk {pair}")
                self.active_positions[pair] = 0
                
        except Exception as e:
            self.logger.error(f"❌ Error execute stop loss untuk {pair}: {e}")
            
    async def _execute_take_profit(self, pair: str, current_price: float):
        """Execute take profit"""
        try:
            coin = pair.split('/')[0]
            position_size = self.active_positions[pair]
            
            order_result = self.hyperliquid_client.place_order(
                coin=coin,
                side="SELL",
                size=position_size,
                price=current_price,
                order_type="MARKET"
            )
            
            if order_result:
                self.logger.info(f"💰 Take profit executed untuk {pair}")
                self.active_positions[pair] = 0
                
        except Exception as e:
            self.logger.error(f"❌ Error execute take profit untuk {pair}: {e}")
            
    async def _close_all_positions(self):
        """Close semua posisi yang sedang dibuka"""
        for pair, position_size in self.active_positions.items():
            if position_size > 0:
                try:
                    current_price = self._get_current_price(pair)
                    if current_price:
                        await self._execute_sell_order(pair, {
                            'decision': 'STRONG_SELL',
                            'confidence': 1.0,
                            'sentiment': {'sentiment': -1.0}
                        })
                except Exception as e:
                    self.logger.error(f"❌ Error close position untuk {pair}: {e}")
                    
    def get_status(self) -> Dict:
        """Get status bot trading"""
        return {
            'is_running': self.is_running,
            'daily_trades': self.daily_trades,
            'daily_pnl': self.daily_pnl,
            'active_positions': self.active_positions,
            'last_trade_time': self.last_trade_time,
            'total_trades': len(self.trade_history)
        }