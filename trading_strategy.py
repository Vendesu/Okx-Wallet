import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import logging

class TradingStrategy:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        """Menghitung Relative Strength Index (RSI)"""
        if len(prices) < period:
            return 50.0
            
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gains = np.mean(gains[-period:])
        avg_losses = np.mean(losses[-period:])
        
        if avg_losses == 0:
            return 100.0
            
        rs = avg_gains / avg_losses
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
        
    def calculate_macd(self, prices: List[float], fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[float, float, float]:
        """Menghitung MACD (Moving Average Convergence Divergence)"""
        if len(prices) < slow:
            return 0.0, 0.0, 0.0
            
        prices_array = np.array(prices)
        ema_fast = self._calculate_ema(prices_array, fast)
        ema_slow = self._calculate_ema(prices_array, slow)
        
        macd_line = ema_fast - ema_slow
        signal_line = self._calculate_ema(np.array([macd_line]), signal)
        histogram = macd_line - signal_line
        
        return macd_line, signal_line, histogram
        
    def _calculate_ema(self, prices: np.ndarray, period: int) -> float:
        """Menghitung Exponential Moving Average (EMA)"""
        if len(prices) < period:
            return prices[-1] if len(prices) > 0 else 0
            
        alpha = 2 / (period + 1)
        ema = prices[0]
        
        for price in prices[1:]:
            ema = alpha * price + (1 - alpha) * ema
            
        return ema
        
    def calculate_bollinger_bands(self, prices: List[float], period: int = 20, std_dev: float = 2.0) -> Tuple[float, float, float]:
        """Menghitung Bollinger Bands"""
        if len(prices) < period:
            return prices[-1], prices[-1], prices[-1]
            
        recent_prices = prices[-period:]
        sma = np.mean(recent_prices)
        std = np.std(recent_prices)
        
        upper_band = sma + (std_dev * std)
        lower_band = sma - (std_dev * std)
        
        return upper_band, sma, lower_band
        
    def analyze_market_sentiment(self, prices: List[float], volumes: List[float] = None) -> Dict[str, float]:
        """Menganalisis sentiment pasar berdasarkan berbagai indikator"""
        if len(prices) < 50:
            return {"sentiment": 0.0, "confidence": 0.0}
            
        # RSI Analysis
        rsi = self.calculate_rsi(prices)
        
        # MACD Analysis
        macd_line, signal_line, histogram = self.calculate_macd(prices)
        
        # Bollinger Bands Analysis
        upper_band, middle_band, lower_band = self.calculate_bollinger_bands(prices)
        current_price = prices[-1]
        
        # Volume Analysis (if available)
        volume_signal = 0.0
        if volumes and len(volumes) >= 20:
            avg_volume = np.mean(volumes[-20:])
            current_volume = volumes[-1]
            volume_signal = 1.0 if current_volume > avg_volume * 1.5 else -1.0 if current_volume < avg_volume * 0.5 else 0.0
        
        # Price Trend Analysis
        short_ma = np.mean(prices[-10:])
        long_ma = np.mean(prices[-30:])
        trend_signal = 1.0 if short_ma > long_ma else -1.0
        
        # Momentum Analysis
        momentum = (prices[-1] - prices[-10]) / prices[-10] * 100
        
        # Sentiment Score Calculation
        sentiment_score = 0.0
        
        # RSI Contribution (30%)
        if rsi < 30:
            sentiment_score += 0.3  # Oversold - bullish
        elif rsi > 70:
            sentiment_score -= 0.3  # Overbought - bearish
        else:
            sentiment_score += (50 - rsi) / 50 * 0.3  # Neutral to moderate
            
        # MACD Contribution (25%)
        if macd_line > signal_line and histogram > 0:
            sentiment_score += 0.25  # Bullish crossover
        elif macd_line < signal_line and histogram < 0:
            sentiment_score -= 0.25  # Bearish crossover
        else:
            sentiment_score += (macd_line - signal_line) / abs(signal_line) * 0.25 if signal_line != 0 else 0
            
        # Bollinger Bands Contribution (20%)
        if current_price < lower_band:
            sentiment_score += 0.2  # Price below lower band - potential bounce
        elif current_price > upper_band:
            sentiment_score -= 0.2  # Price above upper band - potential reversal
        else:
            bb_position = (current_price - lower_band) / (upper_band - lower_band)
            sentiment_score += (0.5 - bb_position) * 0.4  # Center is neutral
            
        # Trend Contribution (15%)
        sentiment_score += trend_signal * 0.15
        
        # Volume Contribution (10%)
        sentiment_score += volume_signal * 0.1
        
        # Normalize sentiment to [-1, 1]
        sentiment_score = max(-1.0, min(1.0, sentiment_score))
        
        # Calculate confidence based on data quality
        confidence = min(1.0, len(prices) / 100.0)
        
        return {
            "sentiment": sentiment_score,
            "confidence": confidence,
            "rsi": rsi,
            "macd": macd_line,
            "macd_signal": signal_line,
            "bollinger_upper": upper_band,
            "bollinger_middle": middle_band,
            "bollinger_lower": lower_band,
            "trend": trend_signal,
            "momentum": momentum
        }
        
    def generate_trading_signals(self, market_data: Dict[str, List[float]]) -> Dict[str, Dict]:
        """Generate trading signals untuk semua trading pairs"""
        signals = {}
        
        for pair, data in market_data.items():
            if 'prices' not in data or len(data['prices']) < 50:
                continue
                
            sentiment = self.analyze_market_sentiment(
                data['prices'], 
                data.get('volumes', None)
            )
            
            # Generate trading decision
            decision = self._make_trading_decision(sentiment, data)
            
            signals[pair] = {
                "decision": decision,
                "sentiment": sentiment,
                "confidence": sentiment["confidence"],
                "timestamp": pd.Timestamp.now()
            }
            
        return signals
        
    def _make_trading_decision(self, sentiment: Dict, data: Dict) -> str:
        """Membuat keputusan trading berdasarkan sentiment dan data pasar"""
        sentiment_score = sentiment["sentiment"]
        confidence = sentiment["confidence"]
        
        # Minimum confidence threshold
        if confidence < 0.3:
            return "HOLD"
            
        # Strong signals
        if sentiment_score > 0.7 and confidence > 0.6:
            return "STRONG_BUY"
        elif sentiment_score < -0.7 and confidence > 0.6:
            return "STRONG_SELL"
        elif sentiment_score > 0.3 and confidence > 0.5:
            return "BUY"
        elif sentiment_score < -0.3 and confidence > 0.5:
            return "SELL"
        else:
            return "HOLD"
            
    def calculate_position_size(self, balance: float, risk_per_trade: float, 
                              stop_loss_pct: float, confidence: float) -> float:
        """Menghitung ukuran posisi berdasarkan risk management"""
        # Adjust position size based on confidence
        confidence_multiplier = 0.5 + (confidence * 0.5)  # 0.5 to 1.0
        
        # Calculate position size based on risk
        risk_amount = balance * (risk_per_trade / 100)
        position_size = risk_amount / (stop_loss_pct / 100)
        
        # Apply confidence multiplier
        adjusted_position_size = position_size * confidence_multiplier
        
        # Ensure position size doesn't exceed maximum
        max_position = balance * 0.1  # Maximum 10% of balance per trade
        
        return min(adjusted_position_size, max_position)