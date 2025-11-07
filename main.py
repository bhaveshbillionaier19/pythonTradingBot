# main.py - Test Script for Milestones 1 & 2
"""
This script tests:
- Milestone 1: Binance Futures client initialization and connection
- Milestone 2: Logging system and input validation

Before running, update src/config.py with your actual Binance Testnet API credentials.
"""

from src.binance_client import BinanceFuturesClient
from src.config import API_KEY, API_SECRET
from src.logger import setup_logging
from src.validators import validate_symbol, validate_quantity, validate_price, validate_side
from binance.exceptions import BinanceAPIException


def test_validation():
    """
    Test input validation functions with user input.
    """
    logger = setup_logging(__name__)
    
    print("\n" + "=" * 60)
    print("MILESTONE 2: INPUT VALIDATION TEST")
    print("=" * 60)
    
    # Test Symbol Validation
    print("\n[Test 1: Symbol Validation]")
    symbol = input("Enter a trading symbol (e.g., BTCUSDT): ").strip()
    
    if validate_symbol(symbol):
        logger.debug(f"Symbol validated: {symbol}")
        print(f"✓ Valid symbol: {symbol}")
    else:
        logger.warning(f"Invalid symbol provided: {symbol}")
        print(f"✗ Invalid symbol: {symbol}")
        print("  Symbol must be uppercase, at least 6 characters, and end with USDT/BUSD/USD/BTC/ETH")
    
    # Test Quantity Validation
    print("\n[Test 2: Quantity Validation]")
    quantity_input = input("Enter a quantity (e.g., 0.5): ").strip()
    
    try:
        quantity = float(quantity_input)
        if validate_quantity(quantity):
            logger.debug(f"Quantity validated: {quantity}")
            print(f"✓ Valid quantity: {quantity}")
        else:
            logger.warning(f"Invalid quantity provided: {quantity}")
            print(f"✗ Invalid quantity: {quantity}")
            print("  Quantity must be a positive number greater than 0")
    except ValueError:
        logger.warning(f"Invalid quantity format: {quantity_input}")
        print(f"✗ Invalid quantity format: {quantity_input}")
        print("  Quantity must be a valid number")
    
    # Test Price Validation
    print("\n[Test 3: Price Validation]")
    price_input = input("Enter a price (e.g., 50000.00): ").strip()
    
    try:
        price = float(price_input)
        if validate_price(price):
            logger.debug(f"Price validated: {price}")
            print(f"✓ Valid price: {price}")
        else:
            logger.warning(f"Invalid price provided: {price}")
            print(f"✗ Invalid price: {price}")
            print("  Price must be a positive number greater than 0")
    except ValueError:
        logger.warning(f"Invalid price format: {price_input}")
        print(f"✗ Invalid price format: {price_input}")
        print("  Price must be a valid number")
    
    # Test Side Validation
    print("\n[Test 4: Side Validation]")
    side = input("Enter order side (BUY or SELL): ").strip()
    
    if validate_side(side):
        logger.debug(f"Side validated: {side.upper()}")
        print(f"✓ Valid side: {side.upper()}")
    else:
        logger.warning(f"Invalid side provided: {side}")
        print(f"✗ Invalid side: {side}")
        print("  Side must be either 'BUY' or 'SELL'")
    
    print("\n" + "=" * 60)
    logger.info("Validation tests completed")


def test_client_connection():
    """
    Test the Binance Futures client by retrieving account information.
    """
    logger = setup_logging(__name__)
    
    print("\n" + "=" * 60)
    print("MILESTONE 1: CLIENT CONNECTION TEST")
    print("=" * 60)
    
    # Check if API credentials have been updated
    if API_KEY == "YOUR_API_KEY" or API_SECRET == "YOUR_API_SECRET":
        print("\n⚠️  WARNING: Please update your API credentials in src/config.py")
        print("   Replace 'YOUR_API_KEY' and 'YOUR_API_SECRET' with your actual")
        print("   Binance Testnet API credentials.\n")
        return
    
    try:
        # Initialize the Binance Futures client (testnet mode)
        print("\n[1] Initializing Binance Futures Client (Testnet)...")
        client = BinanceFuturesClient(
            api_key=API_KEY,
            api_secret=API_SECRET,
            testnet=True
        )
        print("✓ Client initialized successfully!")
        
        # Test connection by retrieving account information
        print("\n[2] Retrieving account information...")
        account_info = client.get_account_info()
        print("✓ Successfully connected to Binance Testnet!")
        
        # Display account information
        print("\n" + "=" * 60)
        print("ACCOUNT INFORMATION")
        print("=" * 60)
        
        # Display key account details
        if 'totalWalletBalance' in account_info:
            print(f"Total Wallet Balance: {account_info['totalWalletBalance']} USDT")
        
        if 'availableBalance' in account_info:
            print(f"Available Balance: {account_info['availableBalance']} USDT")
        
        if 'totalUnrealizedProfit' in account_info:
            print(f"Unrealized Profit: {account_info['totalUnrealizedProfit']} USDT")
        
        # Display assets with non-zero balance
        if 'assets' in account_info:
            print("\nAssets:")
            for asset in account_info['assets']:
                balance = float(asset.get('walletBalance', 0))
                if balance > 0:
                    print(f"  - {asset['asset']}: {balance}")
        
        # Display open positions
        if 'positions' in account_info:
            open_positions = [p for p in account_info['positions'] 
                            if float(p.get('positionAmt', 0)) != 0]
            if open_positions:
                print("\nOpen Positions:")
                for pos in open_positions:
                    print(f"  - {pos['symbol']}: {pos['positionAmt']} "
                          f"(Entry: {pos['entryPrice']})")
            else:
                print("\nOpen Positions: None")
        
        print("\n" + "=" * 60)
        print("✓ Milestone 1 Test Completed Successfully!")
        print("=" * 60)
        
    except BinanceAPIException as e:
        logger.error(f"Binance API Error: {e}")
        print(f"\n❌ Binance API Error: {e}")
        print("\nPossible causes:")
        print("  - Invalid API credentials")
        print("  - API keys not enabled for Futures trading")
        print("  - Network connectivity issues")
        print("  - Testnet service unavailable")
        
    except Exception as e:
        logger.error(f"Unexpected Error: {type(e).__name__}: {e}")
        print(f"\n❌ Unexpected Error: {e}")
        print(f"Error Type: {type(e).__name__}")


def main():
    """
    Main entry point - runs all tests.
    """
    # Initialize logging at the start
    logger = setup_logging(__name__)
    logger.info("=" * 60)
    logger.info("Binance Futures Bot - Test Suite Started")
    logger.info("=" * 60)
    
    print("=" * 60)
    print("BINANCE FUTURES BOT - TEST SUITE")
    print("=" * 60)
    print("\nThis test suite covers:")
    print("  • Milestone 1: Client initialization and connection")
    print("  • Milestone 2: Logging system and input validation")
    
    # Run validation tests
    test_validation()
    
    # Ask if user wants to test client connection
    print("\n" + "=" * 60)
    test_connection = input("\nDo you want to test client connection? (yes/no): ").strip().lower()
    
    if test_connection in ['yes', 'y']:
        test_client_connection()
    else:
        print("\nSkipping client connection test.")
        logger.info("Client connection test skipped by user")
    
    print("\n" + "=" * 60)
    print("✓ ALL TESTS COMPLETED")
    print("=" * 60)
    print("\nCheck bot.log for detailed DEBUG level logs.")
    logger.info("Test suite completed")


if __name__ == "__main__":
    main()
