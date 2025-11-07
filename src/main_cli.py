# src/main_cli.py
"""
Interactive Menu-Driven CLI for Binance Futures Trading Bot.
Provides a user-friendly interface for trading operations.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.logger import setup_logging
from src.binance_client import BinanceFuturesClient
from src.config import API_KEY, API_SECRET
from src.actions import (
    action_market_order,
    action_limit_order,
    action_stop_limit_order,
    action_twap_order,
    action_grid_trading,
    action_oco_position_exit,
    action_view_account_info,
    action_view_open_orders,
    action_cancel_order
)


# Initialize logger
logger = setup_logging(__name__)


def print_banner():
    """Print the application banner."""
    print("\n" + "=" * 70)
    print("   BINANCE FUTURES TRADING BOT")
    print("   Interactive Trading Interface")
    print("=" * 70)


def print_menu():
    """Print the main menu options."""
    print("\n" + "─" * 70)
    print("  MAIN MENU")
    print("─" * 70)
    print("\n   TRADING OPERATIONS:")
    print("     1. Place Market Order")
    print("     2. Place Limit Order")
    print("     3. Place Stop-Limit Order")
    print("     4. Place TWAP Order (Time-Weighted Average Price)")
    print("     5. Start Grid Trading (Automated Grid Strategy)")
    print("     6. Place OCO Orders (Position Exit)")
    print("\n   ACCOUNT & ORDERS:")
    print("     7. View Account Information")
    print("     8. View Open Orders")
    print("     9. Cancel Order")
    print("\n    SYSTEM:")
    print("     10. Switch Environment (Testnet/Production)")
    print("     11. Exit")
    print("\n" + "─" * 70)


def confirm_production_mode():
    """Confirm user wants to use production mode."""
    print("\n" + "!" * 70)
    print("    WARNING: PRODUCTION MODE")
    print("!" * 70)
    print("\n  You are about to use REAL FUNDS on Binance Production!")
    print("  All orders will use actual money.")
    print("\n  Are you absolutely sure you want to continue?")
    
    confirm = input("\n  Type 'I UNDERSTAND THE RISKS' to proceed: ").strip()
    
    if confirm == 'I UNDERSTAND THE RISKS':
        print("\n  ✓ Production mode activated.")
        return True
    else:
        print("\n  ✗ Production mode canceled. Staying in testnet mode.")
        return False


def main_menu():
    """
    Main menu loop for the trading bot.
    Provides interactive interface for all trading operations.
    """
    # Check API credentials
    if API_KEY == "YOUR_API_KEY" or API_SECRET == "YOUR_API_SECRET":
        print("\n" + "=" * 70)
        print("    ERROR: API Credentials Not Configured")
        print("=" * 70)
        print("\n  Please update your API credentials in src/config.py")
        print("  Replace 'YOUR_API_KEY' and 'YOUR_API_SECRET' with your actual")
        print("  Binance Testnet API credentials.")
        print("\n  Get your testnet credentials at: https://testnet.binancefuture.com")
        print("=" * 70)
        sys.exit(1)
    
    # Initialize client (default to testnet)
    testnet = True
    
    try:
        client = BinanceFuturesClient(
            api_key=API_KEY,
            api_secret=API_SECRET,
            testnet=testnet
        )
        logger.info("Binance Futures client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize client: {e}")
        print(f"\n Error: Failed to initialize Binance client: {e}")
        sys.exit(1)
    
    # Print banner
    print_banner()
    print(f"\n  Environment: {' TESTNET' if testnet else '  PRODUCTION'}")
    print(f"  Status: ✓ Connected")
    
    # Main menu loop
    while True:
        try:
            print_menu()
            choice = input("\n  Enter your choice (1-11): ").strip()
            
            if choice == '1':
                action_market_order(client)
                
            elif choice == '2':
                action_limit_order(client)
                
            elif choice == '3':
                action_stop_limit_order(client)
                
            elif choice == '4':
                action_twap_order(client)
                
            elif choice == '5':
                action_grid_trading(client)
                
            elif choice == '6':
                action_oco_position_exit(client)
                
            elif choice == '7':
                action_view_account_info(client)
                
            elif choice == '8':
                action_view_open_orders(client)
                
            elif choice == '9':
                action_cancel_order(client)
                
            elif choice == '10':
                # Switch environment
                print("\n" + "─" * 70)
                print("  SWITCH ENVIRONMENT")
                print("─" * 70)
                print(f"\n  Current: {'Testnet' if testnet else 'Production'}")
                print("\n  1. Testnet (Safe - No real money)")
                print("  2. Production (  Real money!)")
                
                env_choice = input("\n  Enter choice (1-2): ").strip()
                
                if env_choice == '1':
                    if not testnet:
                        testnet = True
                        client = BinanceFuturesClient(API_KEY, API_SECRET, testnet=True)
                        print("\n  ✓ Switched to Testnet mode.")
                        logger.info("Switched to testnet mode")
                    else:
                        print("\n  Already in Testnet mode.")
                        
                elif env_choice == '2':
                    if testnet:
                        if confirm_production_mode():
                            testnet = False
                            client = BinanceFuturesClient(API_KEY, API_SECRET, testnet=False)
                            logger.warning("Switched to PRODUCTION mode")
                    else:
                        print("\n  Already in Production mode.")
                else:
                    print("\n  ✗ Invalid choice.")
                    
            elif choice == '11':
                # Exit
                print("\n" + "=" * 70)
                
                print(" APPLICATION ENDED  Happy Trading!")
                print("=" * 70 + "\n")
                logger.info("Application exited by user")
                sys.exit(0)
                
            else:
                print("\n  ✗ Invalid choice. Please enter a number between 1 and 11.")
            
            # Pause before showing menu again
            input("\n  Press Enter to continue...")
            
        except KeyboardInterrupt:
            print("\n\n" + "=" * 70)
            print("    Interrupted by user")
            print("=" * 70)
            confirm_exit = input("\n  Do you want to exit? (yes/no): ").strip().lower()
            if confirm_exit in ['yes', 'y']:
                print("\n   Goodbye!")
                logger.info("Application interrupted by user")
                sys.exit(0)
            else:
                continue
                
        except Exception as e:
            logger.error(f"Unexpected error in main menu: {e}")
            print(f"\n   An unexpected error occurred: {e}")
            print("  Check bot.log for details.")
            input("\n  Press Enter to continue...")


def main():
    """Entry point for the interactive CLI."""
    logger.info("=" * 60)
    logger.info("Binance Futures Trading Bot - Interactive CLI Started")
    logger.info("=" * 60)
    
    try:
        main_menu()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"\n Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
