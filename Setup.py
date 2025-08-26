#!/usr/bin/env python3
"""
Setup script untuk Trading Bot
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_banner():
    """Print banner setup"""
    print("""
🤖 ======================================== 🤖
    TRADING BOT SETUP WIZARD
🤖 ======================================== 🤖

Selamat datang di setup wizard untuk Trading Bot!
Bot ini akan membantu Anda setup semua yang diperlukan.
    """)

def check_python_version():
    """Check Python version"""
    print("🐍 Checking Python version...")
    
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ diperlukan!")
        print(f"   Versi saat ini: {sys.version}")
        return False
        
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} terdeteksi")
    return True

def install_dependencies():
    """Install dependencies"""
    print("\n📦 Installing dependencies...")
    
    try:
        # Check if pip is available
        subprocess.run([sys.executable, "-m", "pip", "--version"], 
                      check=True, capture_output=True)
        
        # Install requirements
        print("   Installing from requirements.txt...")
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Dependencies berhasil diinstall!")
            return True
        else:
            print("❌ Gagal install dependencies:")
            print(result.stderr)
            return False
            
    except subprocess.CalledProcessError:
        print("❌ pip tidak tersedia!")
        return False
    except Exception as e:
        print(f"❌ Error saat install dependencies: {e}")
        return False

def setup_environment():
    """Setup environment file"""
    print("\n🔧 Setting up environment...")
    
    env_example = Path(".env.example")
    env_file = Path(".env")
    
    if not env_example.exists():
        print("❌ File .env.example tidak ditemukan!")
        return False
        
    if env_file.exists():
        print("⚠️ File .env sudah ada")
        overwrite = input("   Overwrite? (y/N): ").lower().strip()
        if overwrite != 'y':
            print("   Skipping environment setup")
            return True
            
    try:
        # Copy .env.example to .env
        shutil.copy(env_example, env_file)
        print("✅ File .env berhasil dibuat")
        
        print("\n📝 **PENTING: Edit file .env dengan API keys yang sesuai!**")
        print("   File .env berisi informasi sensitif, jangan share ke publik!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error saat setup environment: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating directories...")
    
    try:
        # Create logs directory
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        print("✅ Directory logs berhasil dibuat")
        
        # Create data directory
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        print("✅ Directory data berhasil dibuat")
        
        return True
        
    except Exception as e:
        print(f"❌ Error saat create directories: {e}")
        return False

def test_installation():
    """Test installation"""
    print("\n🧪 Testing installation...")
    
    try:
        # Test imports
        print("   Testing imports...")
        
        # Test config
        from config import *
        print("   ✅ Config imported successfully")
        
        # Test strategy
        from TradingStrategy import TradingStrategy
        strategy = TradingStrategy()
        print("   ✅ Trading strategy imported successfully")
        
        # Test clients
        from OKXWalletClient import OKXWalletClient
        from HyperliquidClient import HyperliquidClient
        print("   ✅ Clients imported successfully")
        
        print("✅ Semua imports berhasil!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error saat testing: {e}")
        return False

def print_next_steps():
    """Print next steps"""
    print("""
🎉 **Setup selesai! Berikut langkah selanjutnya:**

1. 📝 **Edit file .env:**
   - Isi TELEGRAM_TOKEN dari @BotFather
   - Isi OKX API keys dari OKX exchange
   - Isi Hyperliquid private key

2. 🧪 **Test bot:**
   python TestBot.py

3. 🚀 **Jalankan bot:**
   python RunBot.py

4. 📱 **Gunakan Telegram:**
   - Chat dengan bot Anda
   - Gunakan /start untuk memulai
   - Gunakan /help untuk bantuan

⚠️ **PENTING:**
- Jangan share file .env ke publik
- Test di sandbox mode terlebih dahulu
- Monitor bot secara berkala
- Gunakan dengan modal yang siap hilang

📚 **Dokumentasi lengkap ada di README.md**
🤝 **Jika ada masalah, buat issue di GitHub**

Happy Trading! 🚀📈
    """)

def main():
    """Main setup function"""
    print_banner()
    
    # Check Python version
    if not check_python_version():
        print("\n❌ Setup dibatalkan karena Python version tidak sesuai")
        return False
        
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Setup dibatalkan karena gagal install dependencies")
        return False
        
    # Setup environment
    if not setup_environment():
        print("\n❌ Setup dibatalkan karena gagal setup environment")
        return False
        
    # Create directories
    if not create_directories():
        print("\n❌ Setup dibatalkan karena gagal create directories")
        return False
        
    # Test installation
    if not test_installation():
        print("\n❌ Setup dibatalkan karena gagal test installation")
        return False
        
    # Print next steps
    print_next_steps()
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            sys.exit(0)
        else:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Setup dihentikan oleh user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)