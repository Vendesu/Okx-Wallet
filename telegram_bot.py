import asyncio
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from typing import Dict, List
import json

from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
from trading_bot import TradingBot

class TelegramTradingBot:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.trading_bot = TradingBot()
        self.application = None
        
    async def start(self):
        """Start Telegram bot"""
        try:
            self.application = Application.builder().token(TELEGRAM_TOKEN).build()
            
            # Add command handlers
            self.application.add_handler(CommandHandler("start", self._start_command))
            self.application.add_handler(CommandHandler("status", self._status_command))
            self.application.add_handler(CommandHandler("start_bot", self._start_trading_command))
            self.application.add_handler(CommandHandler("stop_bot", self._stop_trading_command))
            self.application.add_handler(CommandHandler("balance", self._balance_command))
            self.application.add_handler(CommandHandler("positions", self._positions_command))
            self.application.add_handler(CommandHandler("trades", self._trades_command))
            self.application.add_handler(CommandHandler("help", self._help_command))
            self.application.add_handler(CommandHandler("pairs_info", self._pairs_info_command))
            self.application.add_handler(CommandHandler("risk_analysis", self._risk_analysis_command))
            self.application.add_handler(CommandHandler("pnl_history", self._pnl_history_command))
            
            # Add callback query handler
            self.application.add_handler(CallbackQueryHandler(self._button_callback))
            
            # Start bot
            await self.application.initialize()
            await self.application.start()
            await self.application.updater.start_polling()
            
            self.logger.info("✅ Telegram bot berhasil dimulai!")
            
        except Exception as e:
            self.logger.error(f"❌ Gagal start Telegram bot: {e}")
            raise
            
    async def stop(self):
        """Stop Telegram bot"""
        try:
            if self.application:
                await self.application.updater.stop()
                await self.application.stop()
                await self.application.shutdown()
                
            self.logger.info("✅ Telegram bot berhasil dihentikan!")
            
        except Exception as e:
            self.logger.error(f"❌ Error saat stop Telegram bot: {e}")
            
    async def _start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_message = """
🤖 **Selamat Datang di Trading Bot!**

Saya adalah bot trading otomatis yang menggunakan strategi canggih untuk trading cryptocurrency.

**Fitur Utama:**
• 📊 Analisis market otomatis dengan RSI, MACD, dan Bollinger Bands
• 🚀 Trading otomatis di Hyperliquid menggunakan OKX data
• 🛡️ Risk management dengan stop loss dan take profit
• 📱 Kontrol penuh melalui Telegram

**Commands yang tersedia:**
/start_bot - Mulai bot trading
/stop_bot - Hentikan bot trading
/status - Lihat status bot
/balance - Lihat balance
/positions - Lihat posisi aktif
/trades - Lihat history trading
/help - Bantuan lengkap

**Status:** Bot siap digunakan! 🎯
        """
        
        keyboard = [
            [InlineKeyboardButton("🚀 Start Bot", callback_data="start_bot")],
            [InlineKeyboardButton("📊 Status", callback_data="status")],
            [InlineKeyboardButton("💰 Balance", callback_data="balance")],
            [InlineKeyboardButton("📈 Positions", callback_data="positions")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            welcome_message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
    async def _start_trading_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start_bot command"""
        try:
            if self.trading_bot.is_running:
                await update.message.reply_text("⚠️ Bot trading sudah berjalan!")
                return
                
            # Start trading bot in background
            asyncio.create_task(self.trading_bot.start())
            
            await update.message.reply_text(
                "🚀 **Bot Trading Dimulai!**\n\n"
                "Bot sedang memulai dan akan mulai trading otomatis dalam beberapa saat.\n"
                "Gunakan /status untuk memantau progress."
            )
            
        except Exception as e:
            await update.message.reply_text(f"❌ Error saat start bot: {e}")
            
    async def _stop_trading_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stop_bot command"""
        try:
            if not self.trading_bot.is_running:
                await update.message.reply_text("⚠️ Bot trading tidak sedang berjalan!")
                return
                
            # Stop trading bot
            await self.trading_bot.stop()
            
            await update.message.reply_text(
                "🛑 **Bot Trading Dihentikan!**\n\n"
                "Semua posisi aktif akan ditutup secara otomatis.\n"
                "Gunakan /start_bot untuk memulai kembali."
            )
            
        except Exception as e:
            await update.message.reply_text(f"❌ Error saat stop bot: {e}")
            
    async def _status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        try:
            status = self.trading_bot.get_status()
            
            status_message = f"""
📊 **Status Bot Trading**

🔄 **Status:** {'🟢 Berjalan' if status['is_running'] else '🔴 Berhenti'}
🎯 **Trading Mode:** {status['trading_mode'].upper()}
📈 **Active Pairs:** {status['active_pairs_count']} pairs
📊 **Total Trades Hari Ini:** {status['daily_trades']}
💰 **Daily PnL:** ${status['daily_pnl']:.2f}
📅 **Last Trade:** {status['last_trade_time'].strftime('%Y-%m-%d %H:%M:%S') if status['last_trade_time'] else 'Belum ada trade'}
📊 **Total Trades:** {status['total_trades']}

**Posisi Aktif:**
"""
            
            if status['active_positions']:
                for pair, size in status['active_positions'].items():
                    status_message += f"• {pair}: {size:.4f}\n"
            else:
                status_message += "Tidak ada posisi aktif\n"
                
            # Add trading pairs info
            if status['active_pairs_count'] > 0:
                status_message += f"\n**Trading Pairs Aktif:**\n"
                if status['active_pairs_count'] <= 10:
                    # Show all pairs if <= 10
                    pairs_info = self.trading_bot.get_trading_pairs_info()
                    for pair in list(pairs_info.keys())[:10]:
                        current_price = pairs_info[pair].get('current_price', 0)
                        if current_price:
                            status_message += f"• {pair}: ${current_price:,.2f}\n"
                        else:
                            status_message += f"• {pair}\n"
                else:
                    # Show sample pairs
                    pairs_info = self.trading_bot.get_trading_pairs_info()
                    sample_pairs = list(pairs_info.keys())[:5]
                    status_message += f"• Sample: {', '.join(sample_pairs)}\n"
                    status_message += f"• ... dan {status['active_pairs_count'] - 5} pairs lainnya\n"
                
            status_message += "\nGunakan /start_bot atau /stop_bot untuk kontrol bot."
            
            keyboard = [
                [InlineKeyboardButton("🔄 Refresh", callback_data="status")],
                [InlineKeyboardButton("💰 Balance", callback_data="balance")],
                [InlineKeyboardButton("📈 Positions", callback_data="positions")],
                [InlineKeyboardButton("🎯 Pairs Info", callback_data="pairs_info")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                status_message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            await update.message.reply_text(f"❌ Error saat get status: {e}")
            
    async def _balance_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /balance command"""
        try:
            # Get wallet balance
            wallet_balance = self.trading_bot.get_wallet_balance()
            
            # Get money management info
            mm_info = self.trading_bot.get_money_management_info()
            
            balance_message = f"""
💰 **Balance & Risk Management**

🏦 **Wallet Balance:**
• Network: {wallet_balance.get('network', 'Unknown') if wallet_balance else 'Unknown'}
• Native Token: {wallet_balance.get('native', 'Unknown') if wallet_balance else 'Unknown'}
• USDC: {wallet_balance.get('usdc', 'Unknown') if wallet_balance else 'Unknown'}

📊 **Trading Balance:**
• Initial Balance: ${self.trading_bot.initial_balance:,.2f}
• Current Balance: ${self.trading_bot.current_balance:,.2f}
• Total PnL: ${self.trading_bot.current_balance - self.trading_bot.initial_balance:,.2f}
• PnL Percentage: {((self.trading_bot.current_balance - self.trading_bot.initial_balance) / self.trading_bot.initial_balance * 100):.2f}%

🛡️ **Risk Management:**
• Portfolio Risk Level: {mm_info.get('portfolio_risk', {}).get('risk_level', 'Unknown')}
• Portfolio Risk: {mm_info.get('portfolio_risk', {}).get('risk_percentage', 0):.1f}%
• Max Risk Allowed: {mm_info.get('portfolio_risk', {}).get('max_risk_allowed', 0):.1f}%

📈 **Portfolio Metrics:**
"""
            
            portfolio_metrics = mm_info.get('portfolio_metrics')
            if portfolio_metrics:
                balance_message += f"""
• Win Rate: {portfolio_metrics.win_rate:.1f}%
• Profit Factor: {portfolio_metrics.profit_factor:.2f}
• Sharpe Ratio: {portfolio_metrics.sharpe_ratio:.2f}
• Max Drawdown: {portfolio_metrics.max_drawdown_percentage:.1f}%
• Risk/Reward Ratio: {portfolio_metrics.risk_reward_ratio:.2f}
"""
            else:
                balance_message += "• Belum ada data trading\n"
                
            # Add warnings if any
            portfolio_risk = mm_info.get('portfolio_risk', {})
            if portfolio_risk.get('warnings'):
                balance_message += "\n🚨 **Warnings:**\n"
                for warning in portfolio_risk['warnings']:
                    balance_message += f"• {warning}\n"
                    
            if portfolio_risk.get('recommendations'):
                balance_message += "\n💡 **Recommendations:**\n"
                for rec in portfolio_risk['recommendations']:
                    balance_message += f"• {rec}\n"
                    
            # Add money management summary
            mm_summary = mm_info.get('money_management_summary', {})
            if mm_summary:
                balance_message += f"""

⚙️ **Money Management Settings:**
• Enabled: {'✅' if mm_summary.get('enabled') else '❌'}
• Position Sizing: {mm_summary.get('position_sizing_method', 'Unknown')}
• Risk Per Trade: {mm_summary.get('risk_per_trade_percentage', 0)}%
• Max Portfolio Risk: {mm_summary.get('max_portfolio_risk', 0)}%
• Max Drawdown: {mm_summary.get('max_drawdown', 0)}%
• Trailing Stop: {'✅' if mm_summary.get('trailing_stop_enabled') else '❌'}
• Profit Taking: {'✅' if mm_summary.get('profit_taking_enabled') else '❌'}
• Volatility Adjustment: {'✅' if mm_summary.get('volatility_adjustment_enabled') else '❌'}
"""
                
            keyboard = [
                [InlineKeyboardButton("🔄 Refresh", callback_data="balance")],
                [InlineKeyboardButton("📊 Status", callback_data="status")],
                [InlineKeyboardButton("📈 Risk Analysis", callback_data="risk_analysis")],
                [InlineKeyboardButton("💰 PnL History", callback_data="pnl_history")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                balance_message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            await update.message.reply_text(f"❌ Error saat get balance: {e}")
            
    async def _positions_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /positions command"""
        try:
            positions = self.trading_bot.active_positions
            
            if not positions:
                positions_message = "📈 **Posisi Aktif**\n\nTidak ada posisi yang sedang dibuka."
            else:
                positions_message = "📈 **Posisi Aktif**\n\n"
                for pair, size in positions.items():
                    current_price = self.trading_bot._get_current_price(pair)
                    if current_price:
                        positions_message += f"• **{pair}**\n"
                        positions_message += f"  └ Size: {size:.4f}\n"
                        positions_message += f"  └ Current Price: ${current_price:.2f}\n\n"
                    else:
                        positions_message += f"• **{pair}**: {size:.4f}\n\n"
                        
            keyboard = [
                [InlineKeyboardButton("🔄 Refresh", callback_data="positions")],
                [InlineKeyboardButton("📊 Status", callback_data="status")],
                [InlineKeyboardButton("💰 Balance", callback_data="balance")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                positions_message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            await update.message.reply_text(f"❌ Error saat get positions: {e}")
            
    async def _trades_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /trades command"""
        try:
            trades = self.trading_bot.trade_history
            
            if not trades:
                trades_message = "📊 **History Trading**\n\nBelum ada trade yang dilakukan."
            else:
                trades_message = "📊 **History Trading**\n\n"
                
                # Show last 10 trades
                recent_trades = trades[-10:]
                for trade in reversed(recent_trades):
                    trades_message += f"• **{trade['pair']}** - {trade['side']}\n"
                    trades_message += f"  └ Size: {trade['size']:.4f}\n"
                    trades_message += f"  └ Price: ${trade['price']:.2f}\n"
                    trades_message += f"  └ Time: {trade['timestamp'].strftime('%H:%M:%S')}\n"
                    trades_message += f"  └ Confidence: {trade['confidence']:.2f}\n\n"
                    
            keyboard = [
                [InlineKeyboardButton("🔄 Refresh", callback_data="trades")],
                [InlineKeyboardButton("📊 Status", callback_data="status")],
                [InlineKeyboardButton("📈 Positions", callback_data="positions")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                trades_message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            await update.message.reply_text(f"❌ Error saat get trades: {e}")
            
    async def _pairs_info_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /pairs_info command - Show detailed trading pairs info"""
        try:
            pairs_info = self.trading_bot.get_trading_pairs_info()
            
            if not pairs_info:
                await update.message.reply_text("📊 **Trading Pairs Info**\n\nTidak ada pairs yang aktif.")
                return
                
            # Create detailed message
            message = "📊 **Trading Pairs Info**\n\n"
            
            # Group by status
            active_pairs = []
            inactive_pairs = []
            
            for pair, info in pairs_info.items():
                if info.get('has_position', False):
                    active_pairs.append((pair, info))
                else:
                    inactive_pairs.append((pair, info))
                    
            # Show active pairs first
            if active_pairs:
                message += "🟢 **Pairs dengan Posisi Aktif:**\n"
                for pair, info in active_pairs[:10]:  # Limit to 10
                    current_price = info.get('current_price', 0)
                    position_size = info.get('position_size', 0)
                    if current_price:
                        message += f"• **{pair}**\n"
                        message += f"  └ Price: ${current_price:,.2f}\n"
                        message += f"  └ Position: {position_size:.4f}\n\n"
                    else:
                        message += f"• **{pair}** - Position: {position_size:.4f}\n\n"
                        
            # Show inactive pairs
            if inactive_pairs:
                message += "⚪ **Pairs Tanpa Posisi:**\n"
                for pair, info in inactive_pairs[:15]:  # Limit to 15
                    current_price = info.get('current_price', 0)
                    if current_price:
                        message += f"• {pair}: ${current_price:,.2f}\n"
                    else:
                        message += f"• {pair}\n"
                        
                if len(inactive_pairs) > 15:
                    message += f"\n... dan {len(inactive_pairs) - 15} pairs lainnya"
                    
            # Add summary
            total_pairs = len(pairs_info)
            active_count = len(active_pairs)
            message += f"\n\n📊 **Summary:** {active_count}/{total_pairs} pairs memiliki posisi aktif"
            
            keyboard = [
                [InlineKeyboardButton("🔄 Refresh", callback_data="pairs_info")],
                [InlineKeyboardButton("📊 Status", callback_data="status")],
                [InlineKeyboardButton("💰 Balance", callback_data="balance")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            await update.message.reply_text(f"❌ Error saat get pairs info: {e}")
            
    async def _risk_analysis_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /risk_analysis command - Show detailed risk analysis"""
        try:
            mm_info = self.trading_bot.get_money_management_info()
            
            risk_message = "📊 **Risk Analysis Report**\n\n"
            
            # Portfolio Risk Analysis
            portfolio_risk = mm_info.get('portfolio_risk', {})
            if portfolio_risk:
                risk_message += f"🛡️ **Portfolio Risk Analysis:**\n"
                risk_message += f"• Risk Level: {portfolio_risk.get('risk_level', 'Unknown')}\n"
                risk_message += f"• Total Risk: ${portfolio_risk.get('total_risk', 0):,.2f}\n"
                risk_message += f"• Risk Percentage: {portfolio_risk.get('risk_percentage', 0):.1f}%\n"
                risk_message += f"• Max Risk Allowed: ${portfolio_risk.get('max_risk_allowed', 0):,.2f}\n\n"
                
                if portfolio_risk.get('warnings'):
                    risk_message += "🚨 **Risk Warnings:**\n"
                    for warning in portfolio_risk['warnings']:
                        risk_message += f"• {warning}\n"
                    risk_message += "\n"
                    
                if portfolio_risk.get('recommendations'):
                    risk_message += "💡 **Risk Recommendations:**\n"
                    for rec in portfolio_risk['recommendations']:
                        risk_message += f"• {rec}\n"
                    risk_message += "\n"
                    
            # Correlation Risk Analysis
            correlation_risk = mm_info.get('correlation_risk', {})
            if correlation_risk:
                risk_message += f"🔗 **Correlation Risk Analysis:**\n"
                
                sector_exposure = correlation_risk.get('sector_exposure', {})
                if sector_exposure:
                    risk_message += "• **Sector Exposure:**\n"
                    for sector, count in sector_exposure.items():
                        risk_message += f"  └ {sector.title()}: {count} positions\n"
                    risk_message += "\n"
                    
                if correlation_risk.get('high_correlation_pairs'):
                    risk_message += "⚠️ **High Correlation Warnings:**\n"
                    for pair in correlation_risk['high_correlation_pairs']:
                        risk_message += f"• {pair}\n"
                    risk_message += "\n"
                    
                if correlation_risk.get('recommendations'):
                    risk_message += "💡 **Diversification Recommendations:**\n"
                    for rec in correlation_risk['recommendations']:
                        risk_message += f"• {rec}\n"
                    risk_message += "\n"
                    
            # Portfolio Metrics
            portfolio_metrics = mm_info.get('portfolio_metrics')
            if portfolio_metrics:
                risk_message += f"📈 **Portfolio Performance Metrics:**\n"
                risk_message += f"• Total PnL: ${portfolio_metrics.total_pnl:,.2f}\n"
                risk_message += f"• PnL Percentage: {portfolio_metrics.total_pnl_percentage:.2f}%\n"
                risk_message += f"• Daily PnL: ${portfolio_metrics.daily_pnl:,.2f}\n"
                risk_message += f"• Weekly PnL: ${portfolio_metrics.weekly_pnl:,.2f}\n"
                risk_message += f"• Monthly PnL: ${portfolio_metrics.monthly_pnl:,.2f}\n"
                risk_message += f"• Max Drawdown: ${portfolio_metrics.max_drawdown:,.2f} ({portfolio_metrics.max_drawdown_percentage:.1f}%)\n"
                risk_message += f"• Sharpe Ratio: {portfolio_metrics.sharpe_ratio:.2f}\n"
                risk_message += f"• Win Rate: {portfolio_metrics.win_rate:.1f}%\n"
                risk_message += f"• Profit Factor: {portfolio_metrics.profit_factor:.2f}\n"
                risk_message += f"• Risk/Reward Ratio: {portfolio_metrics.risk_reward_ratio:.2f}\n\n"
                
            # Money Management Summary
            mm_summary = mm_info.get('money_management_summary', {})
            if mm_summary:
                risk_message += f"⚙️ **Money Management Configuration:**\n"
                risk_message += f"• Position Sizing Method: {mm_summary.get('position_sizing_method', 'Unknown')}\n"
                risk_message += f"• Risk Per Trade: {mm_summary.get('risk_per_trade_percentage', 0)}%\n"
                risk_message += f"• Max Portfolio Risk: {mm_summary.get('max_portfolio_risk', 0)}%\n"
                risk_message += f"• Max Drawdown: {mm_summary.get('max_drawdown', 0)}%\n"
                risk_message += f"• Trailing Stop: {'Enabled' if mm_summary.get('trailing_stop_enabled') else 'Disabled'}\n"
                risk_message += f"• Profit Taking: {'Enabled' if mm_summary.get('profit_taking_enabled') else 'Disabled'}\n"
                risk_message += f"• Volatility Adjustment: {'Enabled' if mm_summary.get('volatility_adjustment_enabled') else 'Disabled'}\n"
                risk_message += f"• Market Condition Filters: {'Enabled' if mm_summary.get('market_condition_filters') else 'Disabled'}\n"
                
            keyboard = [
                [InlineKeyboardButton("🔄 Refresh", callback_data="risk_analysis")],
                [InlineKeyboardButton("💰 Balance", callback_data="balance")],
                [InlineKeyboardButton("📊 Status", callback_data="status")],
                [InlineKeyboardButton("📈 PnL History", callback_data="pnl_history")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                risk_message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            await update.message.reply_text(f"❌ Error saat get risk analysis: {e}")
            
    async def _pnl_history_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /pnl_history command - Show PnL history and analysis"""
        try:
            mm_info = self.trading_bot.get_money_management_info()
            portfolio_metrics = mm_info.get('portfolio_metrics')
            
            if not portfolio_metrics:
                await update.message.reply_text("📈 **PnL History**\n\nBelum ada data trading untuk analisis.")
                return
                
            pnl_message = f"""
📈 **PnL History & Analysis**

💰 **Overall Performance:**
• Initial Balance: ${self.trading_bot.initial_balance:,.2f}
• Current Balance: ${self.trading_bot.current_balance:,.2f}
• Total PnL: ${portfolio_metrics.total_pnl:,.2f}
• PnL Percentage: {portfolio_metrics.total_pnl_percentage:.2f}%

📊 **Time-based PnL:**
• Daily PnL: ${portfolio_metrics.daily_pnl:,.2f}
• Weekly PnL: ${portfolio_metrics.weekly_pnl:,.2f}
• Monthly PnL: ${portfolio_metrics.monthly_pnl:,.2f}

📈 **Performance Metrics:**
• Win Rate: {portfolio_metrics.win_rate:.1f}%
• Profit Factor: {portfolio_metrics.profit_factor:.2f}
• Sharpe Ratio: {portfolio_metrics.sharpe_ratio:.2f}
• Risk/Reward Ratio: {portfolio_metrics.risk_reward_ratio:.2f}

📉 **Risk Metrics:**
• Max Drawdown: ${portfolio_metrics.max_drawdown:,.2f} ({portfolio_metrics.max_drawdown_percentage:.1f}%)
• Average Win: ${portfolio_metrics.average_win:,.2f}
• Average Loss: ${portfolio_metrics.average_loss:,.2f}

🎯 **Trading Statistics:**
• Total Trades: {len(self.trading_bot.trade_history)}
• Daily Trades: {self.trading_bot.daily_trades}
• Portfolio Risk Level: {self.trading_bot.portfolio_risk_level}
"""
            
            # Add recent trades if available
            if self.trading_bot.trade_history:
                recent_trades = self.trading_bot.trade_history[-5:]  # Last 5 trades
                pnl_message += "\n📝 **Recent Trades:**\n"
                
                for trade in recent_trades:
                    timestamp = trade['timestamp'].strftime('%m/%d %H:%M')
                    side = trade['side']
                    pair = trade['pair']
                    pnl = trade.get('pnl', 0)
                    pnl_icon = "🟢" if pnl > 0 else "🔴" if pnl < 0 else "⚪"
                    
                    pnl_message += f"• {timestamp} {side} {pair}: {pnl_icon} ${pnl:,.2f}\n"
                    
            keyboard = [
                [InlineKeyboardButton("🔄 Refresh", callback_data="pnl_history")],
                [InlineKeyboardButton("📊 Risk Analysis", callback_data="risk_analysis")],
                [InlineKeyboardButton("💰 Balance", callback_data="balance")],
                [InlineKeyboardButton("📈 Status", callback_data="status")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                pnl_message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            await update.message.reply_text(f"❌ Error saat get PnL history: {e}")
            
    async def _help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_message = """
❓ **Bantuan Trading Bot**

**Commands Utama:**
• `/start` - Mulai bot dan lihat menu utama
• `/start_bot` - Mulai bot trading otomatis
• `/stop_bot` - Hentikan bot trading
• `/status` - Lihat status bot dan posisi aktif
• `/balance` - Lihat balance dan risk management
• `/positions` - Lihat posisi yang sedang dibuka
• `/trades` - Lihat history trading
• `/pairs_info` - Lihat info detail trading pairs
• `/risk_analysis` - Analisis risiko portfolio lengkap
• `/pnl_history` - History PnL dan performance metrics
• `/help` - Tampilkan bantuan ini

**Trading Modes:**
🤖 **Auto Mode** (Default):
- Auto-detect semua available symbols
- Update symbols setiap jam
- Support hingga 1000+ trading pairs

📈 **Trending Mode**:
- Fokus ke trending coins
- Update berdasarkan market sentiment
- Optimal untuk momentum trading

💰 **High Volume Mode**:
- Pilih pairs dengan volume tinggi
- Filter berdasarkan minimum volume
- Cocok untuk scalping

📊 **Manual Mode**:
- Set trading pairs manual
- Full control atas selection
- Custom trading strategy

**Money Management Features:**
🛡️ **Risk Management:**
- Position sizing dengan Kelly Criterion
- Risk per trade: 2% (configurable)
- Portfolio risk limit: 10% (configurable)
- Max drawdown protection: 15% (configurable)
- Daily/weekly/monthly loss limits

📏 **Position Sizing Methods:**
- **Kelly Criterion**: Optimal sizing berdasarkan win probability
- **Fixed Amount**: Fixed dollar amount per trade
- **Percentage**: Percentage of balance per trade
- **Volatility Adjusted**: Adjust berdasarkan market volatility
- **Market Condition**: Adjust berdasarkan bull/bear market

📊 **Portfolio Management:**
- Correlation risk monitoring
- Sector exposure limits
- Volatility adjustment
- Market condition filters
- Automatic stop loss & take profit

**Fitur Bot:**
🤖 **Trading Otomatis:**
- Analisis market menggunakan RSI, MACD, dan Bollinger Bands
- Signal generation berdasarkan sentiment analysis
- Risk management otomatis dengan stop loss dan take profit

📊 **Data Source:**
- Market data dari CoinGecko (gratis)
- Alternative: Binance API (lebih cepat)
- Real-time price monitoring

🛡️ **Risk Management:**
- Position sizing berdasarkan confidence level
- Daily trade limits
- Cooldown period antar trades
- Automatic stop loss dan take profit

**Cara Penggunaan:**
1. Pastikan semua private keys sudah dikonfigurasi
2. Pilih trading mode di file .env
3. Konfigurasi money management parameters
4. Gunakan `/start_bot` untuk memulai trading
5. Monitor progress dengan `/status`, `/balance`, `/risk_analysis`
6. Gunakan `/stop_bot` untuk menghentikan

**Konfigurasi Money Management:**
```bash
# Risk Management
RISK_PER_TRADE_PERCENTAGE=2.0
MAX_PORTFOLIO_RISK_PERCENTAGE=10.0
MAX_DRAWDOWN_PERCENTAGE=15.0

# Position Sizing
POSITION_SIZING_METHOD=kelly
KELLY_FRACTION=0.25

# Loss Limits
MAX_DAILY_LOSS=50
MAX_WEEKLY_LOSS=200
MAX_MONTHLY_LOSS=500

# Advanced Features
TRAILING_STOP_ENABLED=true
PROFIT_TAKING_ENABLED=true
VOLATILITY_ADJUSTMENT_ENABLED=true
MARKET_CONDITION_FILTERS=true
```

⚠️ **PENTING:**
- Jangan share file .env ke publik
- Test di sandbox mode terlebih dahulu
- Monitor bot secara berkala
- Gunakan dengan modal yang siap hilang
- Money management tidak menjamin profit, hanya mengelola risiko

📚 **Dokumentasi lengkap ada di README.md**
🤝 **Jika ada masalah, buat issue di GitHub**

Happy Trading! 🚀📈
        """
        
        keyboard = [
            [InlineKeyboardButton("🚀 Start Bot", callback_data="start_bot")],
            [InlineKeyboardButton("📊 Status", callback_data="status")],
            [InlineKeyboardButton("💰 Balance", callback_data="balance")],
            [InlineKeyboardButton("📈 Risk Analysis", callback_data="risk_analysis")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            help_message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
    async def _button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks"""
        query = update.callback_query
        await query.answer()
        
        try:
            if query.data == "start_bot":
                await self._start_trading_command(update, context)
            elif query.data == "status":
                await self._status_command(update, context)
            elif query.data == "balance":
                await self._balance_command(update, context)
            elif query.data == "positions":
                await self._positions_command(update, context)
            elif query.data == "trades":
                await self._trades_command(update, context)
            elif query.data == "pairs_info":
                await self._pairs_info_command(update, context)
            elif query.data == "risk_analysis":
                await self._risk_analysis_command(update, context)
            elif query.data == "pnl_history":
                await self._pnl_history_command(update, context)
                
        except Exception as e:
            await query.edit_message_text(f"❌ Error: {e}")
            
    async def send_notification(self, message: str):
        """Send notification to configured chat"""
        try:
            if self.application and TELEGRAM_CHAT_ID:
                await self.application.bot.send_message(
                    chat_id=TELEGRAM_CHAT_ID,
                    text=message,
                    parse_mode='Markdown'
                )
        except Exception as e:
            self.logger.error(f"❌ Error send notification: {e}")
            
    async def send_trade_notification(self, trade_info: Dict):
        """Send trade notification"""
        try:
            message = f"""
🔔 **Trade Notification**

📊 **Pair:** {trade_info['pair']}
📈 **Action:** {trade_info['side']}
💰 **Size:** {trade_info['size']:.4f}
💵 **Price:** ${trade_info['price']:.2f}
🎯 **Confidence:** {trade_info['confidence']:.2f}
⏰ **Time:** {trade_info['timestamp'].strftime('%H:%M:%S')}
            """
            
            await self.send_notification(message)
            
        except Exception as e:
            self.logger.error(f"❌ Error send trade notification: {e}")
            
    async def send_error_notification(self, error_message: str):
        """Send error notification"""
        try:
            message = f"""
⚠️ **Error Notification**

❌ **Error:** {error_message}
⏰ **Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Bot akan mencoba recovery otomatis.
            """
            
            await self.send_notification(message)
            
        except Exception as e:
            self.logger.error(f"❌ Error send error notification: {e}")

# Import datetime untuk error notification
from datetime import datetime