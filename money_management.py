import logging
import math
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from config import *

class PositionSizingMethod(Enum):
    KELLY = "kelly"
    FIXED = "fixed"
    PERCENTAGE = "percentage"
    MARTINGALE = "martingale"
    VOLATILITY_ADJUSTED = "volatility_adjusted"

class MarketCondition(Enum):
    BULL = "bull"
    BEAR = "bear"
    SIDEWAYS = "sideways"
    VOLATILE = "volatile"

@dataclass
class TradeRisk:
    entry_price: float
    stop_loss_price: float
    take_profit_price: float
    position_size: float
    risk_amount: float
    risk_percentage: float
    confidence: float
    volatility: float

@dataclass
class PortfolioMetrics:
    total_balance: float
    total_pnl: float
    total_pnl_percentage: float
    daily_pnl: float
    weekly_pnl: float
    monthly_pnl: float
    max_drawdown: float
    max_drawdown_percentage: float
    sharpe_ratio: float
    win_rate: float
    profit_factor: float
    average_win: float
    average_loss: float
    risk_reward_ratio: float

class MoneyManagement:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.trade_history = []
        self.portfolio_history = []
        self.risk_metrics = {}
        self.last_balance_update = None
        
    def calculate_position_size(self, 
                              balance: float, 
                              entry_price: float, 
                              stop_loss_price: float,
                              confidence: float,
                              volatility: float = None,
                              market_condition: MarketCondition = MarketCondition.SIDEWAYS) -> TradeRisk:
        """Calculate optimal position size berdasarkan money management rules"""
        try:
            if not MONEY_MANAGEMENT_ENABLED:
                return self._calculate_simple_position_size(balance, entry_price, stop_loss_price, confidence)
                
            # Calculate risk per trade
            risk_per_trade_usd = self._calculate_risk_per_trade(balance, confidence, market_condition)
            
            # Calculate stop loss distance
            stop_loss_distance = abs(entry_price - stop_loss_price)
            stop_loss_percentage = (stop_loss_distance / entry_price) * 100
            
            # Calculate position size based on method
            if POSITION_SIZING_METHOD == PositionSizingMethod.KELLY:
                position_size = self._kelly_position_sizing(balance, risk_per_trade_usd, stop_loss_percentage, confidence)
            elif POSITION_SIZING_METHOD == PositionSizingMethod.FIXED:
                position_size = self._fixed_position_sizing(balance, risk_per_trade_usd, entry_price)
            elif POSITION_SIZING_METHOD == PositionSizingMethod.PERCENTAGE:
                position_size = self._percentage_position_sizing(balance, risk_per_trade_usd, entry_price)
            elif POSITION_SIZING_METHOD == PositionSizingMethod.VOLATILITY_ADJUSTED:
                position_size = self._volatility_adjusted_position_sizing(balance, risk_per_trade_usd, stop_loss_percentage, volatility)
            else:
                position_size = self._kelly_position_sizing(balance, risk_per_trade_usd, stop_loss_percentage, confidence)
                
            # Apply volatility adjustment if enabled
            if VOLATILITY_ADJUSTMENT_ENABLED and volatility:
                position_size = self._adjust_for_volatility(position_size, volatility)
                
            # Apply market condition adjustment
            position_size = self._adjust_for_market_condition(position_size, market_condition)
            
            # Calculate final metrics
            risk_amount = position_size * stop_loss_distance
            risk_percentage = (risk_amount / balance) * 100
            
            # Calculate take profit
            take_profit_price = self._calculate_take_profit(entry_price, stop_loss_percentage)
            
            return TradeRisk(
                entry_price=entry_price,
                stop_loss_price=stop_loss_price,
                take_profit_price=take_profit_price,
                position_size=position_size,
                risk_amount=risk_amount,
                risk_percentage=risk_percentage,
                confidence=confidence,
                volatility=volatility or 0
            )
            
        except Exception as e:
            self.logger.error(f"❌ Error calculate position size: {e}")
            return self._calculate_simple_position_size(balance, entry_price, stop_loss_price, confidence)
            
    def _calculate_risk_per_trade(self, balance: float, confidence: float, market_condition: MarketCondition) -> float:
        """Calculate risk amount per trade"""
        try:
            # Base risk percentage
            base_risk_percentage = RISK_PER_TRADE_PERCENTAGE
            
            # Adjust based on confidence
            if confidence >= 0.8:
                risk_multiplier = 1.0  # Full risk for high confidence
            elif confidence >= 0.6:
                risk_multiplier = 0.8  # 80% risk for medium confidence
            elif confidence >= 0.4:
                risk_multiplier = 0.6  # 60% risk for low confidence
            else:
                risk_multiplier = 0.4  # 40% risk for very low confidence
                
            # Calculate risk amount
            risk_amount = (balance * base_risk_percentage / 100) * risk_multiplier
            
            # Apply limits
            risk_amount = max(MIN_RISK_PER_TRADE_USD, min(risk_amount, MAX_RISK_PER_TRADE_USD))
            
            return risk_amount
            
        except Exception as e:
            self.logger.error(f"❌ Error calculate risk per trade: {e}")
            return MIN_RISK_PER_TRADE_USD
            
    def _kelly_position_sizing(self, balance: float, risk_amount: float, stop_loss_percentage: float, confidence: float) -> float:
        """Kelly Criterion position sizing"""
        try:
            # Kelly Criterion formula: f = (bp - q) / b
            # where: f = fraction of capital to bet
            #        b = odds received on the bet
            #        p = probability of winning
            #        q = probability of losing
            
            # Estimate win probability based on confidence
            win_probability = confidence
            loss_probability = 1 - win_probability
            
            # Calculate odds (risk/reward ratio)
            take_profit_percentage = stop_loss_percentage * 2.5  # 2.5:1 risk/reward
            odds = take_profit_percentage / stop_loss_percentage
            
            # Kelly fraction
            kelly_fraction = (odds * win_probability - loss_probability) / odds
            
            # Apply Kelly fraction limit
            kelly_fraction = max(0, min(kelly_fraction, KELLY_FRACTION))
            
            # Calculate position size
            position_size = (balance * kelly_fraction) / (stop_loss_percentage / 100)
            
            return position_size
            
        except Exception as e:
            self.logger.error(f"❌ Error Kelly position sizing: {e}")
            return self._fixed_position_sizing(balance, risk_amount, 0)
            
    def _fixed_position_sizing(self, balance: float, risk_amount: float, entry_price: float) -> float:
        """Fixed dollar amount position sizing"""
        try:
            position_size = FIXED_POSITION_SIZE_USD / entry_price
            return position_size
            
        except Exception as e:
            self.logger.error(f"❌ Error fixed position sizing: {e}")
            return 0
            
    def _percentage_position_sizing(self, balance: float, risk_amount: float, entry_price: float) -> float:
        """Percentage of balance position sizing"""
        try:
            position_value = balance * (PERCENTAGE_POSITION_SIZE / 100)
            position_size = position_value / entry_price
            return position_size
            
        except Exception as e:
            self.logger.error(f"❌ Error percentage position sizing: {e}")
            return 0
            
    def _volatility_adjusted_position_sizing(self, balance: float, risk_amount: float, stop_loss_percentage: float, volatility: float) -> float:
        """Volatility-adjusted position sizing"""
        try:
            # Base position size
            base_position_size = risk_amount / (stop_loss_percentage / 100)
            
            # Adjust for volatility
            if volatility > HIGH_VOLATILITY_THRESHOLD:
                # High volatility: reduce position size
                volatility_multiplier = 0.7
            elif volatility < LOW_VOLATILITY_THRESHOLD:
                # Low volatility: increase position size
                volatility_multiplier = 1.2
            else:
                # Normal volatility: no adjustment
                volatility_multiplier = 1.0
                
            adjusted_position_size = base_position_size * volatility_multiplier
            
            return adjusted_position_size
            
        except Exception as e:
            self.logger.error(f"❌ Error volatility adjusted position sizing: {e}")
            return self._fixed_position_sizing(balance, risk_amount, 0)
            
    def _adjust_for_volatility(self, position_size: float, volatility: float) -> float:
        """Adjust position size for volatility"""
        try:
            if volatility > HIGH_VOLATILITY_THRESHOLD:
                # Reduce position size in high volatility
                return position_size * 0.8
            elif volatility < LOW_VOLATILITY_THRESHOLD:
                # Increase position size in low volatility
                return position_size * 1.1
            else:
                return position_size
                
        except Exception as e:
            self.logger.error(f"❌ Error volatility adjustment: {e}")
            return position_size
            
    def _adjust_for_market_condition(self, position_size: float, market_condition: MarketCondition) -> float:
        """Adjust position size for market condition"""
        try:
            if market_condition == MarketCondition.BEAR:
                # Reduce risk in bear market
                return position_size * BEAR_MARKET_RISK_REDUCTION
            elif market_condition == MarketCondition.BULL:
                # Increase risk in bull market
                return position_size * BULL_MARKET_RISK_INCREASE
            elif market_condition == MarketCondition.VOLATILE:
                # Reduce risk in volatile market
                return position_size * 0.7
            else:
                # No adjustment for sideways market
                return position_size
                
        except Exception as e:
            self.logger.error(f"❌ Error market condition adjustment: {e}")
            return position_size
            
    def _calculate_take_profit(self, entry_price: float, stop_loss_percentage: float) -> float:
        """Calculate take profit price"""
        try:
            # Use risk/reward ratio of 2.5:1
            take_profit_percentage = stop_loss_percentage * 2.5
            
            if entry_price > 0:
                take_profit_price = entry_price * (1 + take_profit_percentage / 100)
                return take_profit_price
            else:
                return 0
                
        except Exception as e:
            self.logger.error(f"❌ Error calculate take profit: {e}")
            return 0
            
    def _calculate_simple_position_size(self, balance: float, entry_price: float, stop_loss_price: float, confidence: float) -> TradeRisk:
        """Fallback simple position sizing"""
        try:
            # Simple 2% risk per trade
            risk_percentage = 2.0
            risk_amount = balance * (risk_percentage / 100)
            
            stop_loss_distance = abs(entry_price - stop_loss_price)
            position_size = risk_amount / stop_loss_distance
            
            take_profit_price = entry_price * (1 + (stop_loss_distance / entry_price) * 2.5)
            
            return TradeRisk(
                entry_price=entry_price,
                stop_loss_price=stop_loss_price,
                take_profit_price=take_profit_price,
                position_size=position_size,
                risk_amount=risk_amount,
                risk_percentage=risk_percentage,
                confidence=confidence,
                volatility=0
            )
            
        except Exception as e:
            self.logger.error(f"❌ Error simple position sizing: {e}")
            return None
            
    def check_portfolio_risk(self, active_positions: Dict, balance: float) -> Dict:
        """Check portfolio risk levels"""
        try:
            portfolio_risk = {
                'total_risk': 0,
                'risk_percentage': 0,
                'max_risk_allowed': balance * (MAX_PORTFOLIO_RISK_PERCENTAGE / 100),
                'risk_level': 'LOW',
                'warnings': [],
                'recommendations': []
            }
            
            # Calculate total portfolio risk
            for pair, position in active_positions.items():
                if isinstance(position, dict) and 'risk_amount' in position:
                    portfolio_risk['total_risk'] += position['risk_amount']
                else:
                    # Estimate risk if not available
                    portfolio_risk['total_risk'] += balance * 0.02  # Assume 2% risk per position
                    
            portfolio_risk['risk_percentage'] = (portfolio_risk['total_risk'] / balance) * 100
            
            # Determine risk level
            if portfolio_risk['risk_percentage'] <= 5:
                portfolio_risk['risk_level'] = 'LOW'
            elif portfolio_risk['risk_percentage'] <= 10:
                portfolio_risk['risk_level'] = 'MEDIUM'
            elif portfolio_risk['risk_percentage'] <= 15:
                portfolio_risk['risk_level'] = 'HIGH'
            else:
                portfolio_risk['risk_level'] = 'EXTREME'
                
            # Generate warnings and recommendations
            if portfolio_risk['risk_percentage'] > MAX_PORTFOLIO_RISK_PERCENTAGE:
                portfolio_risk['warnings'].append(f"⚠️ Portfolio risk ({portfolio_risk['risk_percentage']:.1f}%) melebihi batas maksimal ({MAX_PORTFOLIO_RISK_PERCENTAGE}%)")
                portfolio_risk['recommendations'].append("🔴 Kurangi posisi atau tutup beberapa posisi")
                
            if portfolio_risk['risk_level'] == 'EXTREME':
                portfolio_risk['warnings'].append("🚨 Portfolio risk level EXTREME - Hentikan trading segera!")
                portfolio_risk['recommendations'].append("🛑 Tutup semua posisi dan review strategy")
                
            return portfolio_risk
            
        except Exception as e:
            self.logger.error(f"❌ Error check portfolio risk: {e}")
            return {'error': str(e)}
            
    def check_correlation_risk(self, active_positions: Dict) -> Dict:
        """Check correlation risk between positions"""
        try:
            correlation_risk = {
                'high_correlation_pairs': [],
                'sector_exposure': {},
                'warnings': [],
                'recommendations': []
            }
            
            # Group positions by sector (simplified)
            sectors = {
                'layer1': ['BTC', 'ETH', 'SOL', 'ADA', 'DOT', 'AVAX', 'ATOM'],
                'defi': ['UNI', 'LINK', 'AAVE', 'COMP', 'SUSHI', 'CRV'],
                'gaming': ['AXS', 'MANA', 'SAND', 'ENJ', 'GALA', 'ILV'],
                'memecoin': ['DOGE', 'SHIB', 'PEPE', 'FLOKI', 'BONK']
            }
            
            sector_exposure = {sector: 0 for sector in sectors}
            
            for pair in active_positions.keys():
                base_asset = pair.split('/')[0]
                
                # Find sector for base asset
                for sector, assets in sectors.items():
                    if base_asset in assets:
                        sector_exposure[sector] += 1
                        break
                        
            correlation_risk['sector_exposure'] = sector_exposure
            
            # Check for high correlation
            for sector, count in sector_exposure.items():
                if count > MAX_CORRELATED_POSITIONS:
                    correlation_risk['high_correlation_pairs'].append(sector)
                    correlation_risk['warnings'].append(f"⚠️ Terlalu banyak posisi di sector {sector}: {count} positions")
                    correlation_risk['recommendations'].append(f"🔄 Diversifikasi ke sector lain, kurangi exposure di {sector}")
                    
            return correlation_risk
            
        except Exception as e:
            self.logger.error(f"❌ Error check correlation risk: {e}")
            return {'error': str(e)}
            
    def calculate_drawdown(self, balance_history: List[float]) -> Dict:
        """Calculate drawdown metrics"""
        try:
            if not balance_history or len(balance_history) < 2:
                return {'max_drawdown': 0, 'max_drawdown_percentage': 0}
                
            peak = balance_history[0]
            max_drawdown = 0
            max_drawdown_percentage = 0
            
            for balance in balance_history:
                if balance > peak:
                    peak = balance
                    
                drawdown = peak - balance
                drawdown_percentage = (drawdown / peak) * 100
                
                if drawdown > max_drawdown:
                    max_drawdown = drawdown
                    max_drawdown_percentage = drawdown_percentage
                    
            return {
                'max_drawdown': max_drawdown,
                'max_drawdown_percentage': max_drawdown_percentage,
                'current_drawdown': peak - balance_history[-1] if balance_history else 0,
                'peak_balance': peak
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error calculate drawdown: {e}")
            return {'max_drawdown': 0, 'max_drawdown_percentage': 0}
            
    def should_stop_trading(self, balance: float, initial_balance: float, daily_pnl: float, weekly_pnl: float) -> Dict:
        """Check if trading should be stopped"""
        try:
            stop_trading = {
                'should_stop': False,
                'reason': '',
                'duration': 0,
                'recommendation': ''
            }
            
            # Check daily loss limit
            if daily_pnl <= -MAX_DAILY_LOSS:
                stop_trading['should_stop'] = True
                stop_trading['reason'] = f"Daily loss limit tercapai: ${daily_pnl:.2f}"
                stop_trading['duration'] = COOLDOWN_PERIOD
                stop_trading['recommendation'] = "Tunggu hingga reset daily counter"
                
            # Check weekly loss limit
            elif weekly_pnl <= -MAX_WEEKLY_LOSS:
                stop_trading['should_stop'] = True
                stop_trading['reason'] = f"Weekly loss limit tercapai: ${weekly_pnl:.2f}"
                stop_trading['duration'] = 86400  # 24 jam
                stop_trading['recommendation'] = "Review strategy dan tunggu 24 jam"
                
            # Check drawdown limit
            drawdown = ((initial_balance - balance) / initial_balance) * 100
            if drawdown >= MAX_DRAWDOWN_PERCENTAGE:
                stop_trading['should_stop'] = True
                stop_trading['reason'] = f"Maximum drawdown tercapai: {drawdown:.1f}%"
                stop_trading['duration'] = DRAWDOWN_COOLDOWN_HOURS * 3600  # Convert to seconds
                stop_trading['recommendation'] = f"Tunggu {DRAWDOWN_COOLDOWN_HOURS} jam dan review strategy"
                
            return stop_trading
            
        except Exception as e:
            self.logger.error(f"❌ Error check stop trading: {e}")
            return {'should_stop': False, 'reason': 'Error', 'duration': 0, 'recommendation': ''}
            
    def update_trade_history(self, trade: Dict):
        """Update trade history for analysis"""
        try:
            self.trade_history.append({
                'timestamp': datetime.now(),
                'pair': trade.get('pair', ''),
                'side': trade.get('side', ''),
                'entry_price': trade.get('entry_price', 0),
                'exit_price': trade.get('exit_price', 0),
                'position_size': trade.get('position_size', 0),
                'pnl': trade.get('pnl', 0),
                'pnl_percentage': trade.get('pnl_percentage', 0),
                'confidence': trade.get('confidence', 0),
                'risk_amount': trade.get('risk_amount', 0)
            })
            
            # Keep only last 1000 trades
            if len(self.trade_history) > 1000:
                self.trade_history = self.trade_history[-1000:]
                
        except Exception as e:
            self.logger.error(f"❌ Error update trade history: {e}")
            
    def get_portfolio_metrics(self, current_balance: float, initial_balance: float) -> PortfolioMetrics:
        """Calculate comprehensive portfolio metrics"""
        try:
            if not self.trade_history:
                return PortfolioMetrics(
                    total_balance=current_balance,
                    total_pnl=0,
                    total_pnl_percentage=0,
                    daily_pnl=0,
                    weekly_pnl=0,
                    monthly_pnl=0,
                    max_drawdown=0,
                    max_drawdown_percentage=0,
                    sharpe_ratio=0,
                    win_rate=0,
                    profit_factor=0,
                    average_win=0,
                    average_loss=0,
                    risk_reward_ratio=0
                )
                
            # Calculate basic metrics
            total_pnl = current_balance - initial_balance
            total_pnl_percentage = (total_pnl / initial_balance) * 100
            
            # Calculate daily/weekly/monthly PnL
            now = datetime.now()
            daily_pnl = sum(trade['pnl'] for trade in self.trade_history 
                           if (now - trade['timestamp']).days == 0)
            weekly_pnl = sum(trade['pnl'] for trade in self.trade_history 
                            if (now - trade['timestamp']).days <= 7)
            monthly_pnl = sum(trade['pnl'] for trade in self.trade_history 
                             if (now - trade['timestamp']).days <= 30)
            
            # Calculate win rate and profit factor
            winning_trades = [t for t in self.trade_history if t['pnl'] > 0]
            losing_trades = [t for t in self.trade_history if t['pnl'] < 0]
            
            win_rate = len(winning_trades) / len(self.trade_history) * 100 if self.trade_history else 0
            
            total_wins = sum(t['pnl'] for t in winning_trades)
            total_losses = abs(sum(t['pnl'] for t in losing_trades))
            profit_factor = total_wins / total_losses if total_losses > 0 else 0
            
            # Calculate averages
            average_win = total_wins / len(winning_trades) if winning_trades else 0
            average_loss = total_losses / len(losing_trades) if losing_trades else 0
            risk_reward_ratio = average_win / average_loss if average_loss > 0 else 0
            
            # Calculate drawdown
            balance_history = [initial_balance]
            for trade in self.trade_history:
                balance_history.append(balance_history[-1] + trade['pnl'])
                
            drawdown_info = self.calculate_drawdown(balance_history)
            
            # Calculate Sharpe ratio (simplified)
            returns = [trade['pnl_percentage'] for trade in self.trade_history if trade['pnl_percentage'] != 0]
            if returns:
                avg_return = np.mean(returns)
                std_return = np.std(returns)
                sharpe_ratio = avg_return / std_return if std_return > 0 else 0
            else:
                sharpe_ratio = 0
                
            return PortfolioMetrics(
                total_balance=current_balance,
                total_pnl=total_pnl,
                total_pnl_percentage=total_pnl_percentage,
                daily_pnl=daily_pnl,
                weekly_pnl=weekly_pnl,
                monthly_pnl=monthly_pnl,
                max_drawdown=drawdown_info['max_drawdown'],
                max_drawdown_percentage=drawdown_info['max_drawdown_percentage'],
                sharpe_ratio=sharpe_ratio,
                win_rate=win_rate,
                profit_factor=profit_factor,
                average_win=average_win,
                average_loss=average_loss,
                risk_reward_ratio=risk_reward_ratio
            )
            
        except Exception as e:
            self.logger.error(f"❌ Error get portfolio metrics: {e}")
            return None
            
    def get_money_management_summary(self) -> Dict:
        """Get money management summary"""
        try:
            return {
                'enabled': MONEY_MANAGEMENT_ENABLED,
                'position_sizing_method': POSITION_SIZING_METHOD,
                'risk_per_trade_percentage': RISK_PER_TRADE_PERCENTAGE,
                'max_portfolio_risk': MAX_PORTFOLIO_RISK_PERCENTAGE,
                'max_drawdown': MAX_DRAWDOWN_PERCENTAGE,
                'trailing_stop_enabled': TRAILING_STOP_ENABLED,
                'profit_taking_enabled': PROFIT_TAKING_ENABLED,
                'volatility_adjustment_enabled': VOLATILITY_ADJUSTMENT_ENABLED,
                'market_condition_filters': MARKET_CONDITION_FILTERS
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error get money management summary: {e}")
            return {}