# 📁 Project Structure

## 🏗️ **Folder Organization**

```
📁 Trading Bot Project
├── 🚀 **Root Directory**
│   ├── main.py                    # Main entry point
│   ├── run.py                     # Run bot script
│   ├── test.py                    # Test bot script
│   ├── setup.py                   # Setup wizard script
│   ├── requirements.txt            # Python dependencies
│   └── PROJECT_STRUCTURE.md       # This file
│
├── 🔧 **Source Code (src/)**
│   ├── __init__.py                # Package initialization
│   ├── config.py                  # Configuration settings
│   │
│   ├── 🧠 **Core Components (core/)**
│   │   ├── __init__.py
│   │   ├── TradingBot.py          # Main trading bot logic
│   │   ├── TelegramBot.py         # Telegram interface
│   │   └── Main.py                # Main orchestrator
│   │
│   ├── 🔌 **Clients (clients/)**
│   │   ├── __init__.py
│   │   ├── MarketDataClient.py    # Market data provider
│   │   ├── OKXWalletClient.py     # OKX wallet integration
│   │   └── HyperliquidClient.py   # Hyperliquid trading
│   │
│   ├── 📊 **Strategies (strategies/)**
│   │   ├── __init__.py
│   │   └── TradingStrategy.py     # Trading strategy logic
│   │
│   ├── 💰 **Management (management/)**
│   │   ├── __init__.py
│   │   └── MoneyManagement.py     # Money management system
│   │
│   ├── 🛠️ **Utilities (utils/)**
│   │   └── __init__.py            # Utility functions (future)
│   │
│   ├── 🚀 **Execution (execution/)**
│   │   ├── __init__.py
│   │   └── RunBot.py              # Bot execution script
│   │
│   └── ⚙️ **Setup (setup/)**
│       ├── __init__.py
│       └── Setup.py                # Setup wizard
│
├── 🧪 **Testing (tests/)**
│   ├── __init__.py
│   └── TestBot.py                  # Component testing
│
├── 📚 **Documentation (docs/)**
│   ├── README.md                   # Main documentation
│   └── QUICKSTART.md               # Quick start guide
│
├── ⚙️ **Configuration (config/)**
│   └── .env.example                # Environment template
│
├── 📊 **Data & Logs**
│   ├── logs/                       # Log files
│   └── data/                       # Data storage
│
└── 🐳 **Docker & Deployment**
    ├── Dockerfile                  # Docker configuration
    └── docker-compose.yml          # Docker compose
```

## 🚀 **How to Run**

### **1. Setup & Installation**
```bash
# Install dependencies
pip install -r requirements.txt

# Setup environment
python setup.py
```

### **2. Testing**
```bash
# Test all components
python test.py

# Test specific component
python -m tests.TestBot
```

### **3. Running Bot**
```bash
# Main entry point
python main.py

# Run bot directly
python run.py

# Run from source
python src/core/RunBot.py
```

### **4. Development**
```bash
# Import in your code
from src import TradingBot, TelegramBot
from src.strategies import TradingStrategy
from src.management import MoneyManagement
```

## 📦 **Package Structure**

### **Main Package (src/)**
- **`__init__.py`**: Exports all main components
- **`config.py`**: Centralized configuration

### **Core Package (src/core/)**
- **`TradingBot.py`**: Main trading logic
- **`TelegramBot.py`**: Telegram interface
- **`Main.py`**: System orchestrator

### **Clients Package (src/clients/)**
- **`MarketDataClient.py`**: Market data providers
- **`OKXWalletClient.py`**: OKX wallet integration
- **`HyperliquidClient.py`**: Trading execution

### **Strategies Package (src/strategies/)**
- **`TradingStrategy.py`**: Trading algorithms

### **Management Package (src/management/)**
- **`MoneyManagement.py`**: Risk & money management

## 🔧 **Import Examples**

### **Basic Usage**
```python
# Import main components
from src import TradingBot, TelegramBot

# Import specific modules
from src.strategies import TradingStrategy
from src.management import MoneyManagement
from src.clients import MarketDataClient
```

### **Advanced Usage**
```python
# Import specific classes
from src.core.TradingBot import TradingBot
from src.strategies.TradingStrategy import TradingStrategy
from src.management.MoneyManagement import MoneyManagement, MarketCondition
```

## 📁 **File Naming Convention**

### **Python Files**
- **PascalCase**: `TradingBot.py`, `MoneyManagement.py`
- **snake_case**: `market_data_client.py` (internal functions)

### **Directories**
- **lowercase**: `src/`, `core/`, `clients/`
- **PascalCase**: `strategies/`, `management/`

## 🚀 **Benefits of This Structure**

1. **Modular Design**: Each component is separate and reusable
2. **Easy Testing**: Test individual components independently
3. **Clear Dependencies**: Import paths are explicit and clear
4. **Scalable**: Easy to add new features and modules
5. **Professional**: Follows Python best practices
6. **Maintainable**: Clear separation of concerns

## 🔄 **Migration from Old Structure**

### **Old Import Style**
```python
from trading_bot import TradingBot
from money_management import MoneyManagement
```

### **New Import Style**
```python
from src import TradingBot, MoneyManagement
# or
from src.core import TradingBot
from src.management import MoneyManagement
```

## 📋 **Next Steps**

1. **Update your imports** to use new structure
2. **Test all components** with `python test.py`
3. **Run the bot** with `python main.py`
4. **Customize configuration** in `src/config.py`
5. **Add new features** in appropriate packages