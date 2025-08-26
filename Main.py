#!/usr/bin/env python3
"""
Main entry point untuk Trading Bot
"""

import asyncio
import logging
import signal
import sys
from typing import Optional

from TelegramBot import TelegramTradingBot
from TradingBot import TradingBot

class TradingBotRunner:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.telegram_bot: Optional[TelegramTradingBot] = None
        self.trading_bot: Optional[TradingBot] = None
        self.is_running = False
        
    async def start(self):
        """Start semua bot"""
        try:
            self.logger.info("🚀 Memulai Trading Bot System...")
            
            # Start Telegram bot
            self.telegram_bot = TelegramTradingBot()
            await self.telegram_bot.start()
            
            # Start Trading bot
            self.trading_bot = TradingBot()
            
            self.is_running = True
            self.logger.info("✅ Trading Bot System berhasil dimulai!")
            
            # Keep running
            while self.is_running:
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            self.logger.info("🛑 Received interrupt signal, shutting down...")
        except Exception as e:
            self.logger.error(f"❌ Error dalam main loop: {e}")
        finally:
            await self.shutdown()
            
    async def shutdown(self):
        """Shutdown semua bot"""
        try:
            self.logger.info("🛑 Mematikan Trading Bot System...")
            
            self.is_running = False
            
            # Stop trading bot
            if self.trading_bot and self.trading_bot.is_running:
                await self.trading_bot.stop()
                
            # Stop Telegram bot
            if self.telegram_bot:
                await self.telegram_bot.stop()
                
            self.logger.info("✅ Trading Bot System berhasil dimatikan!")
            
        except Exception as e:
            self.logger.error(f"❌ Error saat shutdown: {e}")
            
    def signal_handler(self, signum, frame):
        """Handle system signals"""
        self.logger.info(f"📡 Received signal {signum}, initiating shutdown...")
        self.is_running = False

async def main():
    """Main function"""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('trading_bot_system.log'),
            logging.StreamHandler()
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info("🎯 Starting Trading Bot System...")
    
    # Create and start runner
    runner = TradingBotRunner()
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, runner.signal_handler)
    signal.signal(signal.SIGTERM, runner.signal_handler)
    
    try:
        await runner.start()
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Bot dihentikan oleh user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)