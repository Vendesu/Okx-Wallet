#!/usr/bin/env python3
"""
Script sederhana untuk menjalankan Trading Bot
"""

import asyncio
import logging
import sys
import os
from pathlib import Path

# Add current directory to Python path
sys.path.append(str(Path(__file__).parent))

from TelegramBot import TelegramTradingBot

async def main():
    """Main function untuk menjalankan bot"""
    print("🤖 Starting Trading Bot...")
    
    # Setup basic logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    try:
        # Check if .env file exists
        if not os.path.exists('.env'):
            print("❌ File .env tidak ditemukan!")
            print("📝 Silakan copy .env.example ke .env dan isi dengan API keys yang sesuai")
            return
            
        # Create and start bot
        bot = TelegramTradingBot()
        print("✅ Bot berhasil dibuat")
        
        # Start bot
        print("🚀 Memulai bot...")
        await bot.start()
        
        print("✅ Bot berhasil dimulai! Bot akan berjalan terus...")
        print("📱 Gunakan Telegram untuk mengontrol bot")
        print("🛑 Tekan Ctrl+C untuk menghentikan")
        
        # Keep running
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Bot dihentikan oleh user")
    except FileNotFoundError as e:
        print(f"❌ File tidak ditemukan: {e}")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Pastikan semua dependencies sudah diinstall dengan: pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ Error tidak terduga: {e}")
        print("🔍 Cek log file untuk detail error")
    finally:
        try:
            if 'bot' in locals():
                print("🛑 Mematikan bot...")
                await bot.stop()
                print("✅ Bot berhasil dimatikan")
        except Exception as e:
            print(f"⚠️ Error saat mematikan bot: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Bot dihentikan")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)