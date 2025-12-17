#!/usr/bin/env python3
"""
GUI version of the Bale to Telegram Forwarder
"""

import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import and run the GUI application
try:
    from gui_forwarder import main
    main()
except ImportError as e:
    print(f"Error importing GUI modules: {e}")
    print("Please make sure all dependencies are installed:")
    print("pip install -r requirements.txt")
    sys.exit(1)