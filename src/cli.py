# src/cli.py
"""
Command-Line Interface for Binance Futures Trading Bot.
Provides CLI commands for placing orders and managing positions.
"""

import argparse
import sys
from .logger import setup_logging
from .binance_client import BinanceFuturesClient
from .market_orders import place_market_order
from .limit_orders import place_limit_order
from .advanced.stop_limit import place_stop_limit_order
from .advanced.oco import place_oco_for_position
from .config import API_KEY, API_SECRET


def main():
    """
    Main entry point for the CLI application.
    Handles command-line argument parsing and order execution.
    """
    # Initialize logging
    logger = setup_logging(__name__)
    logger.info("=" * 60)
    logger.info("Binance Futures Trading Bot - CLI Started")
    logger.info("=" * 60)
    
    # Create main parser
    parser = argparse.ArgumentParser(
        description='Binance Futures Trading Bot - Command Line Interface',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Place a market BUY order
  python src/cli.py market_order --symbol BTCUSDT --side BUY --quantity 0.001
  
  # Place a limit BUY order
  python src/cli.py limit_order --symbol BTCUSDT --side BUY --quantity 0.001 --price 25000.00
  
  # Place a stop-limit BUY order (triggers at stop price, executes at limit price)
  python src/cli.py stop_limit_order --symbol BTCUSDT --side BUY --quantity 0.001 --stop_price 26000.00 --price 26100.00
  
  # Place OCO orders for existing LONG position (take-profit and stop-loss)
  python src/cli.py oco_position_exit --symbol BTCUSDT --position_side LONG --position_quantity 0.001 --take_profit_price 26000.00 --stop_price 24000.00
  
  # View account information
  python src/cli.py account_info
  
  # List all open orders
  python src/cli.py open_orders
  
  # Cancel an order
  python src/cli.py cancel_order --symbol BTCUSDT --order_id 123456789
  
  # Use production environment (default is testnet)
  python src/cli.py market_order --symbol BTCUSDT --side BUY --quantity 0.001 --no-testnet
        """
    )
    
    # Add global arguments
    parser.add_argument(
        '--testnet',
        action='store_true',
        default=True,
        help='Use Binance Testnet (default: True)'
    )
    
    parser.add_argument(
        '--no-testnet',
        action='store_false',
        dest='testnet',
        help='Use Binance Production environment'
    )
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(
        dest='command',
        help='Available commands',
        required=True
    )
    
    # Market Order subcommand
    market_parser = subparsers.add_parser(
        'market_order',
        help='Place a market order',
        description='Place a market order on Binance Futures'
    )
    
    market_parser.add_argument(
        '--symbol',
        type=str,
        required=True,
        help='Trading pair symbol (e.g., BTCUSDT, ETHUSDT)'
    )
    
    market_parser.add_argument(
        '--side',
        type=str,
        required=True,
        choices=['BUY', 'SELL', 'buy', 'sell'],
        help='Order side: BUY or SELL'
    )
    
    market_parser.add_argument(
        '--quantity',
        type=float,
        required=True,
        help='Order quantity (must be positive)'
    )
    
    # Limit Order subcommand
    limit_parser = subparsers.add_parser(
        'limit_order',
        help='Place a limit order',
        description='Place a limit order on Binance Futures'
    )
    
    limit_parser.add_argument(
        '--symbol',
        type=str,
        required=True,
        help='Trading pair symbol (e.g., BTCUSDT, ETHUSDT)'
    )
    
    limit_parser.add_argument(
        '--side',
        type=str,
        required=True,
        choices=['BUY', 'SELL', 'buy', 'sell'],
        help='Order side: BUY or SELL'
    )
    
    limit_parser.add_argument(
        '--quantity',
        type=float,
        required=True,
        help='Order quantity (must be positive)'
    )
    
    limit_parser.add_argument(
        '--price',
        type=float,
        required=True,
        help='Limit price for the order (must be positive)'
    )
    
    # Account Info subcommand
    account_parser = subparsers.add_parser(
        'account_info',
        help='Display account information',
        description='Retrieve and display Binance Futures account information'
    )
    
    # Open Orders subcommand
    open_orders_parser = subparsers.add_parser(
        'open_orders',
        help='List open orders',
        description='Retrieve and display all open orders or orders for a specific symbol'
    )
    
    open_orders_parser.add_argument(
        '--symbol',
        type=str,
        required=False,
        help='Trading pair symbol (optional, if not provided shows all open orders)'
    )
    
    # Cancel Order subcommand
    cancel_parser = subparsers.add_parser(
        'cancel_order',
        help='Cancel an open order',
        description='Cancel a specific order by order ID'
    )
    
    cancel_parser.add_argument(
        '--symbol',
        type=str,
        required=True,
        help='Trading pair symbol (e.g., BTCUSDT, ETHUSDT)'
    )
    
    cancel_parser.add_argument(
        '--order_id',
        type=int,
        required=True,
        help='Order ID to cancel'
    )
    
    # Stop-Limit Order subcommand
    stop_limit_parser = subparsers.add_parser(
        'stop_limit_order',
        help='Place a stop-limit order',
        description='Place a stop-limit order on Binance Futures. '
                    'The order triggers when stop_price is reached, then executes as a limit order at price.'
    )
    
    stop_limit_parser.add_argument(
        '--symbol',
        type=str,
        required=True,
        help='Trading pair symbol (e.g., BTCUSDT, ETHUSDT)'
    )
    
    stop_limit_parser.add_argument(
        '--side',
        type=str,
        required=True,
        choices=['BUY', 'SELL', 'buy', 'sell'],
        help='Order side: BUY or SELL'
    )
    
    stop_limit_parser.add_argument(
        '--quantity',
        type=float,
        required=True,
        help='Order quantity (must be positive)'
    )
    
    stop_limit_parser.add_argument(
        '--stop_price',
        type=float,
        required=True,
        help='Stop price (trigger price) - order activates when market reaches this price'
    )
    
    stop_limit_parser.add_argument(
        '--price',
        type=float,
        required=True,
        help='Limit price (execution price) - order executes at this price after trigger'
    )
    
    # OCO Position Exit subcommand
    oco_parser = subparsers.add_parser(
        'oco_position_exit',
        help='Place OCO (One-Cancels-the-Other) orders for an existing position',
        description='Place simultaneous take-profit and stop-loss orders for an existing position. '
                    'When one order executes, the other is automatically canceled.'
    )
    
    oco_parser.add_argument(
        '--symbol',
        type=str,
        required=True,
        help='Trading pair symbol (e.g., BTCUSDT, ETHUSDT)'
    )
    
    oco_parser.add_argument(
        '--position_side',
        type=str,
        required=True,
        choices=['LONG', 'SHORT', 'long', 'short'],
        help='Current position side: LONG or SHORT'
    )
    
    oco_parser.add_argument(
        '--position_quantity',
        type=float,
        required=True,
        help='Position quantity to close (must match your open position)'
    )
    
    oco_parser.add_argument(
        '--take_profit_price',
        type=float,
        required=True,
        help='Take profit price (LONG: above current, SHORT: below current)'
    )
    
    oco_parser.add_argument(
        '--stop_price',
        type=float,
        required=True,
        help='Stop loss price (LONG: below current, SHORT: above current)'
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Check if API credentials are configured
    if API_KEY == "YOUR_API_KEY" or API_SECRET == "YOUR_API_SECRET":
        logger.error("API credentials not configured")
        print("\n" + "=" * 60)
        print("  ERROR: API Credentials Not Configured")
        print("=" * 60)
        print("\nPlease update your API credentials in src/config.py")
        print("Replace 'YOUR_API_KEY' and 'YOUR_API_SECRET' with your actual")
        print("Binance Testnet API credentials.")
        print("\nGet your testnet credentials at: https://testnet.binancefuture.com")
        print("=" * 60)
        sys.exit(1)
    
    # Initialize Binance Futures client
    try:
        logger.info(f"Initializing Binance Futures client (testnet={args.testnet})")
        client = BinanceFuturesClient(
            api_key=API_KEY,
            api_secret=API_SECRET,
            testnet=args.testnet
        )
        logger.info("Client initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize client: {e}")
        print(f"\n Error: Failed to initialize Binance client: {e}")
        sys.exit(1)
    
    # Handle commands
    if args.command == 'market_order':
        logger.info(f"Processing market_order command")
        
        print("\n" + "=" * 60)
        print("PLACING MARKET ORDER")
        print("=" * 60)
        print(f"Symbol:   {args.symbol.upper()}")
        print(f"Side:     {args.side.upper()}")
        print(f"Quantity: {args.quantity}")
        print(f"Type:     MARKET")
        print(f"Testnet:  {args.testnet}")
        print("=" * 60)
        
        # Confirm order (safety check)
        if not args.testnet:
            print("\n  WARNING: You are about to place an order on PRODUCTION!")
            confirm = input("Type 'CONFIRM' to proceed: ").strip()
            if confirm != 'CONFIRM':
                logger.info("Order canceled by user")
                print("\n Order canceled.")
                sys.exit(0)
        
        # Place the market order
        result = place_market_order(
            client=client,
            symbol=args.symbol,
            side=args.side,
            quantity=args.quantity
        )
        
        # Display result
        if result:
            print("\n" + "=" * 60)
            print("✓ ORDER PLACED SUCCESSFULLY")
            print("=" * 60)
            print(f"Order ID:      {result.get('orderId')}")
            print(f"Symbol:        {result.get('symbol')}")
            print(f"Side:          {result.get('side')}")
            print(f"Type:          {result.get('type')}")
            print(f"Status:        {result.get('status')}")
            print(f"Quantity:      {result.get('origQty')}")
            print(f"Executed Qty:  {result.get('executedQty')}")
            print(f"Avg Price:     {result.get('avgPrice')}")
            
            if result.get('cumQuote'):
                print(f"Total Cost:    {result.get('cumQuote')} USDT")
            
            print("=" * 60)
            logger.info("Order execution completed successfully")
            
        else:
            print("\n" + "=" * 60)
            print(" ORDER FAILED")
            print("=" * 60)
            print("The order could not be placed. Check the logs for details.")
            print("Common issues:")
            print("  - Invalid symbol format")
            print("  - Invalid quantity (must be positive)")
            print("  - Insufficient balance")
            print("  - API permissions not enabled for Futures")
            print("  - Network connectivity issues")
            print("\nCheck bot.log for detailed error information.")
            print("=" * 60)
            logger.error("Order execution failed")
            sys.exit(1)
    
    elif args.command == 'limit_order':
        logger.info(f"Processing limit_order command")
        
        print("\n" + "=" * 60)
        print("PLACING LIMIT ORDER")
        print("=" * 60)
        print(f"Symbol:   {args.symbol.upper()}")
        print(f"Side:     {args.side.upper()}")
        print(f"Quantity: {args.quantity}")
        print(f"Price:    {args.price}")
        print(f"Type:     LIMIT")
        print(f"TIF:      GTC (Good-Till-Canceled)")
        print(f"Testnet:  {args.testnet}")
        print("=" * 60)
        
        # Confirm order (safety check)
        if not args.testnet:
            print("\n  WARNING: You are about to place an order on PRODUCTION!")
            confirm = input("Type 'CONFIRM' to proceed: ").strip()
            if confirm != 'CONFIRM':
                logger.info("Order canceled by user")
                print("\n Order canceled.")
                sys.exit(0)
        
        # Place the limit order
        result = place_limit_order(
            client=client,
            symbol=args.symbol,
            side=args.side,
            quantity=args.quantity,
            price=args.price
        )
        
        # Display result
        if result:
            print("\n" + "=" * 60)
            print("✓ LIMIT ORDER PLACED SUCCESSFULLY")
            print("=" * 60)
            print(f"Order ID:      {result.get('orderId')}")
            print(f"Symbol:        {result.get('symbol')}")
            print(f"Side:          {result.get('side')}")
            print(f"Type:          {result.get('type')}")
            print(f"Status:        {result.get('status')}")
            print(f"Quantity:      {result.get('origQty')}")
            print(f"Price:         {result.get('price')}")
            print(f"Time In Force: {result.get('timeInForce')}")
            print(f"Executed Qty:  {result.get('executedQty')}")
            
            if result.get('status') == 'NEW':
                print("\n Order is now active and waiting to be filled.")
                print(f"   It will execute when market price reaches {result.get('price')}")
            
            print("=" * 60)
            logger.info("Limit order placement completed successfully")
            
        else:
            print("\n" + "=" * 60)
            print(" LIMIT ORDER FAILED")
            print("=" * 60)
            print("The limit order could not be placed. Check the logs for details.")
            print("Common issues:")
            print("  - Invalid symbol format")
            print("  - Invalid quantity or price (must be positive)")
            print("  - Price too far from current market price")
            print("  - Insufficient balance")
            print("  - API permissions not enabled for Futures")
            print("  - Network connectivity issues")
            print("\nCheck bot.log for detailed error information.")
            print("=" * 60)
            logger.error("Limit order execution failed")
            sys.exit(1)
    
    elif args.command == 'account_info':
        logger.info("Processing account_info command")
        
        print("\n" + "=" * 60)
        print("ACCOUNT INFORMATION")
        print("=" * 60)
        
        try:
            account_info = client.get_account_info()
            
            # Display key account metrics
            print(f"\n Account Summary:")
            print(f"   Total Wallet Balance:    {account_info.get('totalWalletBalance', 'N/A')} USDT")
            print(f"   Available Balance:       {account_info.get('availableBalance', 'N/A')} USDT")
            print(f"   Total Unrealized PnL:    {account_info.get('totalUnrealizedProfit', 'N/A')} USDT")
            print(f"   Total Margin Balance:    {account_info.get('totalMarginBalance', 'N/A')} USDT")
            print(f"   Total Position Initial:  {account_info.get('totalPositionInitialMargin', 'N/A')} USDT")
            
            # Display assets with non-zero balance
            if 'assets' in account_info:
                assets_with_balance = [a for a in account_info['assets'] if float(a.get('walletBalance', 0)) > 0]
                if assets_with_balance:
                    print(f"\n Assets:")
                    for asset in assets_with_balance:
                        print(f"   {asset['asset']:8} - Balance: {asset['walletBalance']:>15} | "
                              f"Available: {asset.get('availableBalance', 'N/A'):>15}")
                else:
                    print(f"\n Assets: No assets with balance")
            
            # Display open positions
            if 'positions' in account_info:
                open_positions = [p for p in account_info['positions'] if float(p.get('positionAmt', 0)) != 0]
                if open_positions:
                    print(f"\n📈 Open Positions ({len(open_positions)}):")
                    for pos in open_positions:
                        pnl = float(pos.get('unRealizedProfit', 0))
                        pnl_symbol = "📈" if pnl >= 0 else "📉"
                        print(f"   {pnl_symbol} {pos['symbol']:10} | "
                              f"Amount: {pos['positionAmt']:>10} | "
                              f"Entry: {pos['entryPrice']:>10} | "
                              f"PnL: {pnl:>10.2f} USDT")
                else:
                    print(f"\n📈 Open Positions: None")
            
            print("\n" + "=" * 60)
            logger.info("Account information retrieved successfully")
            
        except BinanceAPIException as e:
            logger.error(f"Failed to retrieve account info: {e}")
            print(f"\n Error: Failed to retrieve account information")
            print(f"   {e}")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            print(f"\n Unexpected error: {e}")
            sys.exit(1)
    
    elif args.command == 'open_orders':
        logger.info(f"Processing open_orders command (symbol={args.symbol if args.symbol else 'ALL'})")
        
        print("\n" + "=" * 60)
        if args.symbol:
            print(f"OPEN ORDERS FOR {args.symbol.upper()}")
        else:
            print("ALL OPEN ORDERS")
        print("=" * 60)
        
        try:
            open_orders = client.get_open_orders(args.symbol)
            
            if not open_orders:
                print("\n No open orders found.")
                if args.symbol:
                    print(f"   Symbol: {args.symbol.upper()}")
                print("\n" + "=" * 60)
                logger.info("No open orders found")
            else:
                print(f"\n Found {len(open_orders)} open order(s):\n")
                
                for i, order in enumerate(open_orders, 1):
                    print(f"[{i}] Order ID: {order.get('orderId')}")
                    print(f"    Symbol:        {order.get('symbol')}")
                    print(f"    Type:          {order.get('type')}")
                    print(f"    Side:          {order.get('side')}")
                    print(f"    Price:         {order.get('price')}")
                    print(f"    Quantity:      {order.get('origQty')}")
                    print(f"    Executed:      {order.get('executedQty')}")
                    print(f"    Status:        {order.get('status')}")
                    print(f"    Time In Force: {order.get('timeInForce')}")
                    
                    # Calculate time since order was placed
                    if 'time' in order:
                        from datetime import datetime
                        order_time = datetime.fromtimestamp(order['time'] / 1000)
                        print(f"    Created:       {order_time.strftime('%Y-%m-%d %H:%M:%S')}")
                    
                    print()
                
                print("=" * 60)
                print(f"💡 Tip: To cancel an order, use:")
                print(f"   python src/cli.py cancel_order --symbol <SYMBOL> --order_id <ORDER_ID>")
                print("=" * 60)
                logger.info(f"Retrieved {len(open_orders)} open order(s)")
                
        except BinanceAPIException as e:
            logger.error(f"Failed to retrieve open orders: {e}")
            print(f"\n Error: Failed to retrieve open orders")
            print(f"   {e}")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            print(f"\n Unexpected error: {e}")
            sys.exit(1)
    
    elif args.command == 'cancel_order':
        logger.info(f"Processing cancel_order command (symbol={args.symbol}, orderId={args.order_id})")
        
        print("\n" + "=" * 60)
        print("CANCELING ORDER")
        print("=" * 60)
        print(f"Symbol:   {args.symbol.upper()}")
        print(f"Order ID: {args.order_id}")
        print("=" * 60)
        
        # Confirm cancellation (safety check)
        if not args.testnet:
            print("\n  WARNING: You are about to cancel an order on PRODUCTION!")
            confirm = input("Type 'CONFIRM' to proceed: ").strip()
            if confirm != 'CONFIRM':
                logger.info("Order cancellation canceled by user")
                print("\n Cancellation aborted.")
                sys.exit(0)
        
        try:
            result = client.cancel_order(args.symbol, args.order_id)
            
            print("\n" + "=" * 60)
            print("✓ ORDER CANCELED SUCCESSFULLY")
            print("=" * 60)
            print(f"Order ID:      {result.get('orderId')}")
            print(f"Symbol:        {result.get('symbol')}")
            print(f"Side:          {result.get('side')}")
            print(f"Type:          {result.get('type')}")
            print(f"Status:        {result.get('status')}")
            print(f"Original Qty:  {result.get('origQty')}")
            print(f"Executed Qty:  {result.get('executedQty')}")
            
            if result.get('price'):
                print(f"Price:         {result.get('price')}")
            
            print("=" * 60)
            logger.info(f"Order {args.order_id} canceled successfully")
            
        except BinanceAPIException as e:
            logger.error(f"Failed to cancel order: {e}")
            print(f"\n Error: Failed to cancel order")
            print(f"   {e}")
            print("\nPossible reasons:")
            print("  - Order ID does not exist")
            print("  - Order already filled or canceled")
            print("  - Symbol does not match order")
            print("\nCheck bot.log for detailed error information.")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            print(f"\n❌ Unexpected error: {e}")
            sys.exit(1)
    
    elif args.command == 'stop_limit_order':
        logger.info(f"Processing stop_limit_order command")
        
        print("\n" + "=" * 60)
        print("PLACING STOP-LIMIT ORDER")
        print("=" * 60)
        print(f"Symbol:      {args.symbol.upper()}")
        print(f"Side:        {args.side.upper()}")
        print(f"Quantity:    {args.quantity}")
        print(f"Stop Price:  {args.stop_price} (trigger)")
        print(f"Limit Price: {args.price} (execution)")
        print(f"Type:        STOP-LIMIT")
        print(f"TIF:         GTC (Good-Till-Canceled)")
        print(f"Testnet:     {args.testnet}")
        print("=" * 60)
        
        # Explain order logic
        if args.side.upper() == 'BUY':
            print("\n Order Logic:")
            print(f"   • Order triggers when market price reaches {args.stop_price}")
            print(f"   • Then executes as limit order at {args.price}")
            print(f"   • Use case: Enter long when price breaks above resistance")
        else:
            print("\n Order Logic:")
            print(f"   • Order triggers when market price reaches {args.stop_price}")
            print(f"   • Then executes as limit order at {args.price}")
            print(f"   • Use case: Exit position or enter short when price breaks support")
        
        # Confirm order (safety check)
        if not args.testnet:
            print("\n  WARNING: You are about to place an order on PRODUCTION!")
            confirm = input("Type 'CONFIRM' to proceed: ").strip()
            if confirm != 'CONFIRM':
                logger.info("Order canceled by user")
                print("\n Order canceled.")
                sys.exit(0)
        
        # Place the stop-limit order
        result = place_stop_limit_order(
            client=client,
            symbol=args.symbol,
            side=args.side,
            quantity=args.quantity,
            price=args.price,
            stop_price=args.stop_price
        )
        
        # Display result
        if result:
            print("\n" + "=" * 60)
            print("✓ STOP-LIMIT ORDER PLACED SUCCESSFULLY")
            print("=" * 60)
            print(f"Order ID:      {result.get('orderId')}")
            print(f"Symbol:        {result.get('symbol')}")
            print(f"Side:          {result.get('side')}")
            print(f"Type:          {result.get('type')}")
            print(f"Status:        {result.get('status')}")
            print(f"Quantity:      {result.get('origQty')}")
            print(f"Stop Price:    {result.get('stopPrice')}")
            print(f"Limit Price:   {result.get('price')}")
            print(f"Time In Force: {result.get('timeInForce')}")
            print(f"Working Type:  {result.get('workingType')}")
            
            if result.get('status') == 'NEW':
                print("\n Order is now active and waiting to be triggered.")
                print(f"   It will activate when market price reaches {result.get('stopPrice')}")
                print(f"   Then execute as a limit order at {result.get('price')}")
            
            print("=" * 60)
            logger.info("Stop-limit order placement completed successfully")
            
        else:
            print("\n" + "=" * 60)
            print(" STOP-LIMIT ORDER FAILED")
            print("=" * 60)
            print("The stop-limit order could not be placed. Check the logs for details.")
            print("Common issues:")
            print("  - Invalid symbol format")
            print("  - Invalid quantity, price, or stop_price (must be positive)")
            print("  - Stop price and limit price relationship issues")
            print("  - Insufficient balance")
            print("  - API permissions not enabled for Futures")
            print("  - Network connectivity issues")
            print("\nCheck bot.log for detailed error information.")
            print("=" * 60)
            logger.error("Stop-limit order execution failed")
            sys.exit(1)
    
    elif args.command == 'oco_position_exit':
        logger.info(f"Processing oco_position_exit command")
        
        print("\n" + "=" * 60)
        print("PLACING OCO ORDERS FOR POSITION EXIT")
        print("=" * 60)
        print(f"Symbol:           {args.symbol.upper()}")
        print(f"Position Side:    {args.position_side.upper()}")
        print(f"Position Qty:     {args.position_quantity}")
        print(f"Take Profit:      {args.take_profit_price}")
        print(f"Stop Loss:        {args.stop_price}")
        print(f"Order Type:       OCO (One-Cancels-the-Other)")
        print(f"Testnet:          {args.testnet}")
        print("=" * 60)
        
        # Explain OCO logic
        position_side_upper = args.position_side.upper()
        if position_side_upper == 'LONG':
            closing_side = 'SELL'
            print("\n OCO Logic for LONG Position:")
            print(f"   • Take Profit: SELL at {args.take_profit_price} (profit target)")
            print(f"   • Stop Loss: SELL at {args.stop_price} (loss limit)")
            print(f"   • When one executes, the other is automatically canceled")
        else:
            closing_side = 'BUY'
            print("\n OCO Logic for SHORT Position:")
            print(f"   • Take Profit: BUY at {args.take_profit_price} (profit target)")
            print(f"   • Stop Loss: BUY at {args.stop_price} (loss limit)")
            print(f"   • When one executes, the other is automatically canceled")
        
        print(f"\n  IMPORTANT:")
        print(f"   • This command is for EXISTING positions only")
        print(f"   • Make sure you have an open {position_side_upper} position")
        print(f"   • Both orders will close your entire position")
        print(f"   • Verify your position quantity matches: {args.position_quantity}")
        
        # Confirm order (safety check)
        if not args.testnet:
            print("\n  WARNING: You are about to place orders on PRODUCTION!")
            confirm = input("Type 'CONFIRM' to proceed: ").strip()
            if confirm != 'CONFIRM':
                logger.info("OCO orders canceled by user")
                print("\n Orders canceled.")
                sys.exit(0)
        else:
            # Even on testnet, confirm user understands this is for existing position
            print("\n" + "=" * 60)
            confirm = input("Confirm you have an existing position (yes/no): ").strip().lower()
            if confirm not in ['yes', 'y']:
                logger.info("OCO orders canceled - no existing position")
                print("\n❌ Orders canceled. Open a position first using market_order or limit_order.")
                sys.exit(0)
        
        # Place the OCO orders
        result = place_oco_for_position(
            client=client,
            symbol=args.symbol,
            position_side=args.position_side,
            position_quantity=args.position_quantity,
            take_profit_price=args.take_profit_price,
            stop_price=args.stop_price
        )
        
        # Display result
        if result:
            print("\n" + "=" * 60)
            print("✓ OCO ORDERS PLACED SUCCESSFULLY")
            print("=" * 60)
            
            # Display Take-Profit order details
            tp_order = result.get('take_profit', {})
            print(f"\n Take-Profit Order:")
            print(f"   Order ID:      {tp_order.get('orderId')}")
            print(f"   Symbol:        {tp_order.get('symbol')}")
            print(f"   Side:          {tp_order.get('side')}")
            print(f"   Type:          {tp_order.get('type')}")
            print(f"   Status:        {tp_order.get('status')}")
            print(f"   Stop Price:    {tp_order.get('stopPrice')}")
            print(f"   Close Position: {tp_order.get('closePosition')}")
            
            # Display Stop-Loss order details
            sl_order = result.get('stop_loss', {})
            print(f"\n Stop-Loss Order:")
            print(f"   Order ID:      {sl_order.get('orderId')}")
            print(f"   Symbol:        {sl_order.get('symbol')}")
            print(f"   Side:          {sl_order.get('side')}")
            print(f"   Type:          {sl_order.get('type')}")
            print(f"   Status:        {sl_order.get('status')}")
            print(f"   Stop Price:    {sl_order.get('stopPrice')}")
            print(f"   Close Position: {sl_order.get('closePosition')}")
            
            print("\n" + "=" * 60)
            print(" OCO Orders Active:")
            print(f"   • If price reaches {args.take_profit_price}, take-profit executes")
            print(f"     and stop-loss is automatically canceled")
            print(f"   • If price reaches {args.stop_price}, stop-loss executes")
            print(f"     and take-profit is automatically canceled")
            print(f"   • Both orders will close your entire {position_side_upper} position")
            print("=" * 60)
            
            print(f"\n💡 Tip: View your open orders with:")
            print(f"   python src/cli.py open_orders --symbol {args.symbol.upper()}")
            
            logger.info("OCO orders placement completed successfully")
            
        else:
            print("\n" + "=" * 60)
            print("X OCO ORDERS FAILED")
            print("=" * 60)
            print("The OCO orders could not be placed. Check the logs for details.")
            print("Common issues:")
            print("  - No existing position (open a position first)")
            print("  - Invalid symbol format")
            print("  - Invalid prices (TP and SL must be on correct sides)")
            print("  - Position quantity mismatch")
            print("  - Insufficient balance or margin")
            print("  - API permissions not enabled for Futures")
            print("  - Network connectivity issues")
            print("\nFor LONG positions:")
            print("  - Take profit price must be ABOVE stop loss price")
            print("For SHORT positions:")
            print("  - Take profit price must be BELOW stop loss price")
            print("\nCheck bot.log for detailed error information.")
            print("=" * 60)
            logger.error("OCO orders execution failed")
            sys.exit(1)


if __name__ == "__main__":
    main()
