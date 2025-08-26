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
📈 **Total Trades Hari Ini:** {status['daily_trades']}
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
                
            status_message += "\nGunakan /start_bot atau /stop_bot untuk kontrol bot."
            
            keyboard = [
                [InlineKeyboardButton("🔄 Refresh", callback_data="status")],
                [InlineKeyboardButton("💰 Balance", callback_data="balance")],
                [InlineKeyboardButton("📈 Positions", callback_data="positions")]
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
            # Get balance from Hyperliquid
            balance = await self.trading_bot._get_available_balance()
            
            balance_message = f"""
💰 **Balance Information**

💵 **Available USDC:** ${balance:.2f}
🏦 **Initial Balance:** ${INITIAL_BALANCE:.2f}
📊 **Daily PnL:** ${self.trading_bot.daily_pnl:.2f}

**Risk Management:**
• Max Position Size: {MAX_POSITION_SIZE * 100}%
• Stop Loss: {STOP_LOSS_PERCENTAGE}%
• Take Profit: {TAKE_PROFIT_PERCENTAGE}%
• Max Daily Trades: {MAX_DAILY_TRADES}
• Max Daily Loss: ${MAX_DAILY_LOSS}
            """
            
            keyboard = [
                [InlineKeyboardButton("🔄 Refresh", callback_data="balance")],
                [InlineKeyboardButton("📊 Status", callback_data="status")],
                [InlineKeyboardButton("📈 Positions", callback_data="positions")]
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
• `/help` - Tampilkan bantuan ini

**Fitur Bot:**
🤖 **Trading Otomatis:**
- Analisis market menggunakan RSI, MACD, dan Bollinger Bands
- Signal generation berdasarkan sentiment analysis
- Risk management otomatis dengan stop loss dan take profit

📊 **Data Source:**
- Market data dari OKX exchange
- Trading execution di Hyperliquid
- Real-time price monitoring

🛡️ **Risk Management:**
- Position sizing berdasarkan confidence level
- Daily trade limits
- Cooldown period antar trades
- Automatic stop loss dan take profit

**Cara Penggunaan:**
1. Pastikan semua API keys sudah dikonfigurasi
2. Gunakan `/start_bot` untuk memulai trading
3. Monitor progress dengan `/status`
4. Gunakan `/stop_bot` untuk menghentikan

**Support:** Jika ada masalah, cek log file `trading_bot.log`
        """
        
        keyboard = [
            [InlineKeyboardButton("🚀 Start Bot", callback_data="start_bot")],
            [InlineKeyboardButton("📊 Status", callback_data="status")],
            [InlineKeyboardButton("💰 Balance", callback_data="balance")]
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