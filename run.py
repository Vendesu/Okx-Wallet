#!/usr/bin/env python3
"""
Run Script untuk Trading Bot
"""

import sys
from pathlib import Path

# Add src directory to Python path
sys.path.append(str(Path(__file__).parent / 'src'))

from core.RunBot import main

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())