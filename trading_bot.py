import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd
import numpy as np

from config import *
from trading_strategy import TradingStrategy
from okx_client import OKXWalletClient
from hyperliquid_client import HyperliquidClient
from market_data_client import MarketDataClient
from money_management import MoneyManagement, MarketCondition, TradeRisk

class TradingBot:
    def __init__(self):
        self.logger = self._setup_logging()
        self.strategy = TradingStrategy()
        self.okx_wallet = OKXWalletClient()
        self.hyperliquid_client = HyperliquidClient()
        self.market_data_client = MarketDataClient()
        self.money_management = MoneyManagement()
        
        # Trading state
        self.is_running = False
        self.daily_trades = 0
        self.daily_pnl = 0.0
        self.weekly_pnl = 0.0
        self.monthly_pnl = 0.0
        self.last_trade_time = None
        self.active_positions = {}
        self.trade_history = []
        self.initial_balance = INITIAL_BALANCE
        self.current_balance = INITIAL_BALANCE
        
        # Market data cache
        self.market_data_cache = {}
        self.last_update_time = {}
        
        # Dynamic symbols
        self.active_trading_pairs = []
        self.last_symbols_update = None
        self.symbols_update_interval = 3600  # Update symbols setiap 1 jam
        
        # Risk management
        self.portfolio_risk_level = 'LOW'
        self.last_risk_check = None
        self.risk_check_interval = 300  # Check risk setiap 5 menit
        
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
            
        # Setup trading pairs
        await self._setup_trading_pairs()
        
        # Initialize balance
        await self._update_balance()
        
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
        """Test koneksi ke semua service"""
        try:
            # Test OKX Wallet
            okx_ok = self.okx_wallet.test_connection()
            if not okx_ok:
                self.logger.error("❌ Koneksi OKX Wallet gagal")
                return False
                
            # Test Hyperliquid
            hyperliquid_ok = self.hyperliquid_client.test_connection()
            if not hyperliquid_ok:
                self.logger.error("❌ Koneksi Hyperliquid gagal")
                return False
                
            # Test Market Data
            market_data_ok = self.market_data_client.test_connection()
            if not market_data_ok:
                self.logger.error("❌ Koneksi Market Data gagal")
                return False
                
            self.logger.info("✅ Semua koneksi berhasil")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error saat test koneksi: {e}")
            return False
            
    async def _setup_trading_pairs(self):
        """Setup trading pairs berdasarkan mode yang dipilih"""
        try:
            self.logger.info(f"🔧 Setting up trading pairs dengan mode: {TRADING_MODE}")
            
            if TRADING_MODE == 'manual':
                # Gunakan pairs yang di-set manual
                self.active_trading_pairs = TRADING_PAIRS if TRADING_PAIRS else ['BTC/USDT', 'ETH/USDT']
                self.logger.info(f"📊 Manual mode: {len(self.active_trading_pairs)} pairs")
                
            elif TRADING_MODE == 'auto':
                # Auto-detect semua available symbols
                await self._update_trading_pairs()
                
            elif TRADING_MODE == 'trending':
                # Gunakan trending symbols
                trending_symbols = self.market_data_client.get_trending_symbols(TRENDING_SYMBOL_LIMIT)
                self.active_trading_pairs = trending_symbols
                self.logger.info(f"📈 Trending mode: {len(self.active_trading_pairs)} pairs")
                
            elif TRADING_MODE == 'high_volume':
                # Gunakan high volume symbols
                high_volume_symbols = self.market_data_client.get_high_volume_symbols(MIN_VOLUME_USD, AUTO_SYMBOL_LIMIT)
                self.active_trading_pairs = high_volume_symbols
                self.logger.info(f"💰 High volume mode: {len(self.active_trading_pairs)} pairs")
                
            else:
                # Default ke auto mode
                await self._update_trading_pairs()
                
            # Filter excluded symbols
            self.active_trading_pairs = [pair for pair in self.active_trading_pairs if pair not in EXCLUDED_SYMBOLS]
            
            self.logger.info(f"🎯 Trading pairs aktif: {len(self.active_trading_pairs)} pairs")
            if len(self.active_trading_pairs) <= 20:  # Show all if <= 20
                for pair in self.active_trading_pairs:
                    self.logger.info(f"  • {pair}")
            else:
                self.logger.info(f"  • Top 10: {', '.join(self.active_trading_pairs[:10])}")
                self.logger.info(f"  • ... dan {len(self.active_trading_pairs) - 10} pairs lainnya")
                
        except Exception as e:
            self.logger.error(f"❌ Error setup trading pairs: {e}")
            # Fallback ke default pairs
            self.active_trading_pairs = ['BTC/USDT', 'ETH/USDT']
            
    async def _update_trading_pairs(self):
        """Update trading pairs secara otomatis"""
        try:
            current_time = time.time()
            
            # Check if perlu update
            if (self.last_symbols_update and 
                (current_time - self.last_symbols_update) < self.symbols_update_interval):
                return
                
            self.logger.info("🔄 Updating trading pairs...")
            
            # Get all available symbols
            all_symbols = self.market_data_client.get_all_available_symbols(force_refresh=True)
            
            if all_symbols:
                # Apply filters
                filtered_symbols = self._filter_symbols(all_symbols)
                
                # Limit jumlah symbols
                if len(filtered_symbols) > AUTO_SYMBOL_LIMIT:
                    # Prioritaskan berdasarkan market cap atau volume
                    filtered_symbols = filtered_symbols[:AUTO_SYMBOL_LIMIT]
                    
                self.active_trading_pairs = filtered_symbols
                self.last_symbols_update = current_time
                
                self.logger.info(f"✅ Trading pairs updated: {len(self.active_trading_pairs)} pairs")
            else:
                self.logger.warning("⚠️ Tidak ada symbols yang ditemukan, gunakan default")
                self.active_trading_pairs = ['BTC/USDT', 'ETH/USDT']
                
        except Exception as e:
            self.logger.error(f"❌ Error update trading pairs: {e}")
            
    def _filter_symbols(self, symbols: List[str]) -> List[str]:
        """Filter symbols berdasarkan kriteria tertentu"""
        try:
            filtered = []
            
            for symbol in symbols:
                # Skip excluded symbols
                if symbol in EXCLUDED_SYMBOLS:
                    continue
                    
                # Skip invalid symbols
                if not symbol or '/' not in symbol:
                    continue
                    
                # Skip stablecoin pairs (optional)
                base_asset = symbol.split('/')[0]
                if base_asset in ['USDT', 'USDC', 'BUSD', 'DAI']:
                    continue
                    
                filtered.append(symbol)
                
            return filtered
            
        except Exception as e:
            self.logger.error(f"❌ Error filter symbols: {e}")
            return symbols
            
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
                    
                # Check risk management
                if await self._check_risk_management():
                    self.logger.warning("⚠️ Risk management triggered, pausing trading...")
                    await asyncio.sleep(300)  # Wait 5 menit
                    continue
                    
                # Update trading pairs (periodic)
                await self._update_trading_pairs()
                
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
                
                # Update balance
                await self._update_balance()
                
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
        
    async def _check_risk_management(self) -> bool:
        """Check risk management rules"""
        try:
            current_time = time.time()
            
            # Check if perlu check risk
            if (self.last_risk_check and 
                (current_time - self.last_risk_check) < self.risk_check_interval):
                return False
                
            self.last_risk_check = current_time
            
            # Check portfolio risk
            portfolio_risk = self.money_management.check_portfolio_risk(self.active_positions, self.current_balance)
            
            # Check correlation risk
            correlation_risk = self.money_management.check_correlation_risk(self.active_positions)
            
            # Check if should stop trading
            stop_trading = self.money_management.should_stop_trading(
                self.current_balance, 
                self.initial_balance, 
                self.daily_pnl, 
                self.weekly_pnl
            )
            
            # Log risk status
            if portfolio_risk.get('warnings'):
                for warning in portfolio_risk['warnings']:
                    self.logger.warning(f"🚨 {warning}")
                    
            if correlation_risk.get('warnings'):
                for warning in correlation_risk['warnings']:
                    self.logger.warning(f"⚠️ {warning}")
                    
            if stop_trading['should_stop']:
                self.logger.error(f"🛑 {stop_trading['reason']}")
                self.logger.info(f"💡 {stop_trading['recommendation']}")
                return True
                
            # Update portfolio risk level
            self.portfolio_risk_level = portfolio_risk.get('risk_level', 'LOW')
            
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Error check risk management: {e}")
            return False
            
    async def _update_market_data(self):
        """Update market data untuk semua trading pairs"""
        for pair in self.active_trading_pairs:
            try:
                # Get data dari market data client
                market_data = self.market_data_client.get_market_data(pair, '1h', 100)
                
                if market_data:
                    self.market_data_cache[pair] = market_data
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
        """Execute trading signals dengan money management"""
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
                    
                # Execute trade dengan money management
                if decision in ["BUY", "STRONG_BUY"]:
                    await self._execute_buy_order_with_mm(pair, signal_data)
                elif decision in ["SELL", "STRONG_SELL"]:
                    await self._execute_sell_order_with_mm(pair, signal_data)
                    
            except Exception as e:
                self.logger.error(f"❌ Error execute signal untuk {pair}: {e}")
                
    def _is_in_cooldown(self) -> bool:
        """Check apakah bot sedang dalam cooldown"""
        if not self.last_trade_time:
            return False
            
        time_diff = (datetime.now() - self.last_trade_time).total_seconds()
        return time_diff < COOLDOWN_PERIOD
        
    async def _execute_buy_order_with_mm(self, pair: str, signal_data: Dict):
        """Execute buy order dengan money management"""
        try:
            # Get current price
            current_price = self._get_current_price(pair)
            if not current_price:
                return
                
            # Calculate stop loss price
            stop_loss_percentage = STOP_LOSS_PERCENTAGE
            stop_loss_price = current_price * (1 - stop_loss_percentage / 100)
            
            # Calculate volatility
            volatility = self._calculate_volatility(pair)
            
            # Determine market condition
            market_condition = self._determine_market_condition(pair)
            
            # Calculate position size dengan money management
            trade_risk = self.money_management.calculate_position_size(
                balance=self.current_balance,
                entry_price=current_price,
                stop_loss_price=stop_loss_price,
                confidence=signal_data['confidence'],
                volatility=volatility,
                market_condition=market_condition
            )
            
            if not trade_risk or trade_risk.position_size <= 0:
                self.logger.warning(f"⚠️ Position size terlalu kecil untuk {pair}")
                return
                
            # Check if position size exceeds limits
            if trade_risk.position_size > MAX_POSITION_SIZE:
                trade_risk.position_size = MAX_POSITION_SIZE
                self.logger.info(f"📏 Position size dibatasi ke {MAX_POSITION_SIZE} untuk {pair}")
                
            # Place order di Hyperliquid
            coin = pair.split('/')[0]  # Extract coin name
            order_result = self.hyperliquid_client.place_order(
                coin=coin,
                side="BUY",
                size=trade_risk.position_size,
                price=current_price,
                order_type="LIMIT"
            )
            
            if order_result:
                # Record trade dengan money management data
                self._record_trade_with_mm(pair, "BUY", trade_risk, signal_data)
                
                # Update money management
                self.money_management.update_trade_history({
                    'pair': pair,
                    'side': 'BUY',
                    'entry_price': current_price,
                    'position_size': trade_risk.position_size,
                    'confidence': signal_data['confidence'],
                    'risk_amount': trade_risk.risk_amount
                })
                
                self.logger.info(f"✅ Buy order berhasil untuk {pair}: {trade_risk.position_size:.4f} @ ${current_price:.2f}")
                self.logger.info(f"💰 Risk: ${trade_risk.risk_amount:.2f} ({trade_risk.risk_percentage:.1f}%)")
            else:
                self.logger.error(f"❌ Buy order gagal untuk {pair}")
                
        except Exception as e:
            self.logger.error(f"❌ Error execute buy order untuk {pair}: {e}")
            
    async def _execute_sell_order_with_mm(self, pair: str, signal_data: Dict):
        """Execute sell order dengan money management"""
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
                # Calculate PnL
                entry_price = self._get_entry_price(pair)
                pnl = (current_price - entry_price) * position_size
                pnl_percentage = ((current_price - entry_price) / entry_price) * 100
                
                # Record trade dengan PnL
                self._record_trade_with_mm(pair, "SELL", None, signal_data, pnl, pnl_percentage, entry_price)
                
                # Update money management
                self.money_management.update_trade_history({
                    'pair': pair,
                    'side': 'SELL',
                    'entry_price': entry_price,
                    'exit_price': current_price,
                    'position_size': position_size,
                    'pnl': pnl,
                    'pnl_percentage': pnl_percentage,
                    'confidence': signal_data['confidence']
                })
                
                self.logger.info(f"✅ Sell order berhasil untuk {pair}: {position_size:.4f} @ ${current_price:.2f}")
                self.logger.info(f"💰 PnL: ${pnl:.2f} ({pnl_percentage:.1f}%)")
            else:
                self.logger.error(f"❌ Sell order gagal untuk {pair}")
                
        except Exception as e:
            self.logger.error(f"❌ Error execute sell order untuk {pair}: {e}")
            
    def _calculate_volatility(self, pair: str) -> float:
        """Calculate volatility untuk pair"""
        try:
            if pair in self.market_data_cache:
                prices = self.market_data_cache[pair].get('prices', [])
                if len(prices) > 1:
                    returns = [(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices))]
                    volatility = np.std(returns) * 100  # Convert to percentage
                    return volatility
            return 0
        except Exception as e:
            self.logger.error(f"❌ Error calculate volatility untuk {pair}: {e}")
            return 0
            
    def _determine_market_condition(self, pair: str) -> MarketCondition:
        """Determine market condition untuk pair"""
        try:
            if pair in self.market_data_cache:
                prices = self.market_data_cache[pair].get('prices', [])
                if len(prices) >= 20:
                    # Simple trend analysis
                    recent_prices = prices[-20:]
                    first_price = recent_prices[0]
                    last_price = recent_prices[-1]
                    
                    # Calculate trend
                    trend_percentage = ((last_price - first_price) / first_price) * 100
                    
                    if trend_percentage > 10:
                        return MarketCondition.BULL
                    elif trend_percentage < -10:
                        return MarketCondition.BEAR
                    else:
                        return MarketCondition.SIDEWAYS
                        
            return MarketCondition.SIDEWAYS
            
        except Exception as e:
            self.logger.error(f"❌ Error determine market condition untuk {pair}: {e}")
            return MarketCondition.SIDEWAYS
            
    def _get_current_price(self, pair: str) -> Optional[float]:
        """Get current price untuk pair tertentu"""
        try:
            # Use market data client
            return self.market_data_client.get_current_price(pair)
        except Exception as e:
            self.logger.error(f"❌ Error get current price untuk {pair}: {e}")
            return None
            
    def _get_entry_price(self, pair: str) -> float:
        """Get entry price untuk pair (simplified)"""
        # In real implementation, this should track actual entry prices
        # For now, use current price as approximation
        return self._get_current_price(pair) or 0
        
    async def _get_available_balance(self) -> float:
        """Get available balance dari Hyperliquid"""
        try:
            user_state = self.hyperliquid_client.get_user_state()
            if user_state and 'data' in user_state:
                # Extract USDC balance
                for asset in user_state['data'].get('assetPositions', []):
                    if asset.get('coin') == 'USDC':
                        return float(asset.get('free', 0))
            return self.current_balance
        except Exception as e:
            self.logger.error(f"❌ Error get balance: {e}")
            return self.current_balance
            
    def _record_trade_with_mm(self, pair: str, side: str, trade_risk: TradeRisk, signal_data: Dict, pnl: float = 0, pnl_percentage: float = 0, entry_price: float = 0):
        """Record trade dengan money management data"""
        trade = {
            'timestamp': datetime.now(),
            'pair': pair,
            'side': side,
            'size': trade_risk.position_size if trade_risk else 0,
            'price': trade_risk.entry_price if trade_risk else entry_price,
            'confidence': signal_data['confidence'],
            'sentiment': signal_data['sentiment'],
            'pnl': pnl,
            'pnl_percentage': pnl_percentage,
            'risk_amount': trade_risk.risk_amount if trade_risk else 0,
            'risk_percentage': trade_risk.risk_percentage if trade_risk else 0
        }
        
        self.trade_history.append(trade)
        self.daily_trades += 1
        self.last_trade_time = datetime.now()
        
        # Update PnL
        if side == "SELL":
            self.daily_pnl += pnl
            self.weekly_pnl += pnl
            self.monthly_pnl += pnl
            
        # Update active positions
        if side == "BUY" and trade_risk:
            self.active_positions[pair] = self.active_positions.get(pair, 0) + trade_risk.position_size
        elif side == "SELL":
            self.active_positions[pair] = max(0, self.active_positions.get(pair, 0) - trade['size'])
            
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
                        await self._execute_sell_order_with_mm(pair, {
                            'decision': 'STRONG_SELL',
                            'confidence': 1.0,
                            'sentiment': {'sentiment': -1.0}
                        })
                except Exception as e:
                    self.logger.error(f"❌ Error close position untuk {pair}: {e}")
                    
    async def _update_balance(self):
        """Update current balance"""
        try:
            balance = await self._get_available_balance()
            if balance > 0:
                self.current_balance = balance
                
        except Exception as e:
            self.logger.error(f"❌ Error update balance: {e}")
            
    def get_status(self) -> Dict:
        """Get status bot trading"""
        return {
            'is_running': self.is_running,
            'daily_trades': self.daily_trades,
            'daily_pnl': self.daily_pnl,
            'weekly_pnl': self.weekly_pnl,
            'monthly_pnl': self.monthly_pnl,
            'active_positions': self.active_positions,
            'last_trade_time': self.last_trade_time,
            'total_trades': len(self.trade_history),
            'trading_mode': TRADING_MODE,
            'active_pairs_count': len(self.active_trading_pairs),
            'last_symbols_update': self.last_symbols_update,
            'portfolio_risk_level': self.portfolio_risk_level,
            'current_balance': self.current_balance,
            'initial_balance': self.initial_balance
        }
        
    def get_wallet_balance(self) -> Optional[Dict]:
        """Get balance dari OKX Wallet"""
        try:
            # Get native token balance
            native_balance = self.okx_wallet.get_balance()
            
            # Get USDC balance if available
            usdc_balance = None
            # You can add USDC contract address here
            # usdc_balance = self.okx_wallet.get_balance("0xA0b86a33E6441b8c4C8C1C1B8C4C8C1C1B8C4C8C")
            
            return {
                'native': native_balance,
                'usdc': usdc_balance,
                'network': self.okx_wallet.network
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error get wallet balance: {e}")
            return None
            
    def get_trading_pairs_info(self) -> Dict:
        """Get informasi tentang trading pairs yang aktif"""
        try:
            pairs_info = {}
            
            for pair in self.active_trading_pairs:
                # Get current price
                current_price = self._get_current_price(pair)
                
                # Get market info
                market_info = self.market_data_client.get_market_info(pair)
                
                pairs_info[pair] = {
                    'current_price': current_price,
                    'market_info': market_info,
                    'has_position': pair in self.active_positions and self.active_positions[pair] > 0,
                    'position_size': self.active_positions.get(pair, 0)
                }
                
            return pairs_info
            
        except Exception as e:
            self.logger.error(f"❌ Error get trading pairs info: {e}")
            return {}
            
    def get_money_management_info(self) -> Dict:
        """Get money management information"""
        try:
            # Get portfolio metrics
            portfolio_metrics = self.money_management.get_portfolio_metrics(
                self.current_balance, 
                self.initial_balance
            )
            
            # Get money management summary
            mm_summary = self.money_management.get_money_management_summary()
            
            # Get portfolio risk
            portfolio_risk = self.money_management.check_portfolio_risk(
                self.active_positions, 
                self.current_balance
            )
            
            # Get correlation risk
            correlation_risk = self.money_management.check_correlation_risk(self.active_positions)
            
            return {
                'portfolio_metrics': portfolio_metrics,
                'money_management_summary': mm_summary,
                'portfolio_risk': portfolio_risk,
                'correlation_risk': correlation_risk,
                'current_balance': self.current_balance,
                'initial_balance': self.initial_balance
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error get money management info: {e}")
            return {}