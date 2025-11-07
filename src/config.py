# src/config.py
"""
Configuration file for Binance Futures Trading Bot.
Loads API credentials from environment variables or .env file.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()


API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")


if not API_KEY:
    API_KEY = "YOUR_BINANCE_API_KEY_HERE"
    print("  Warning: BINANCE_API_KEY not found in environment variables.")
    print("   Please set it in .env file or as environment variable.")
    print("   See .env.example for template.")

if not API_SECRET:
    API_SECRET = "YOUR_BINANCE_API_SECRET_HERE"
    print("  Warning: BINANCE_API_SECRET not found in environment variables.")
    print("   Please set it in .env file or as environment variable.")
    print("   See .env.example for template.")


TESTNET_BASE_URL = "https://testnet.binancefuture.com"
