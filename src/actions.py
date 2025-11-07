# src/actions.py
"""
Action functions for the trading bot CLI.
Each function handles a specific trading action with user input and feedback.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from binance.exceptions import BinanceAPIException
from src.binance_client import BinanceFuturesClient
from src.market_orders import place_market_order
from src.limit_orders import place_limit_order
from src.advanced.stop_limit import place_stop_limit_order
from src.advanced.oco import place_oco_for_position
from src.advanced.twap import execute_twap_order
from src.advanced.grid import start_grid_trading
from src.logger import setup_logging


# Initialize logger
logger = setup_logging(__name__)


def print_header(title):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_success(message):
    """Print a success message."""
    print(f"\n✓ {message}")


def print_error(message):
    """Print an error message."""
    print(f"\n X {message}")


def print_info(message):
    """Print an info message."""
    print(f"\n {message}")


def action_market_order(client: BinanceFuturesClient):
    """
    Handle market order placement with user input.
    
    Args:
        client: Initialized Binance Futures client
    """
    print_header("PLACE MARKET ORDER")
    
    try:
        # Get user input
        symbol = input("\nEnter symbol (e.g., BTCUSDT): ").strip().upper()
        side = input("Enter side (BUY/SELL): ").strip().upper()
        quantity = float(input("Enter quantity: ").strip())
        
        # Confirm order
        print(f"\n Order Summary:")
        print(f"   Symbol:   {symbol}")
        print(f"   Side:     {side}")
        print(f"   Quantity: {quantity}")
        print(f"   Type:     MARKET")
        
        confirm = input("\nConfirm order? (yes/no): ").strip().lower()
        if confirm not in ['yes', 'y']:
            print_info("Order canceled.")
            return
        
        # Place order
        logger.info(f"Placing market order: {side} {quantity} {symbol}")
        result = place_market_order(client, symbol, side, quantity)
        
        if result:
            print_success("Market order placed successfully!")
            print(f"\n   Order ID:      {result.get('orderId')}")
            print(f"   Symbol:        {result.get('symbol')}")
            print(f"   Side:          {result.get('side')}")
            print(f"   Status:        {result.get('status')}")
            print(f"   Executed Qty:  {result.get('executedQty')}")
            print(f"   Avg Price:     {result.get('avgPrice')}")
        else:
            print_error("Failed to place market order. Check logs for details.")
            
    except ValueError as e:
        print_error(f"Invalid input: {e}")
    except Exception as e:
        logger.error(f"Error in market order action: {e}")
        print_error(f"An error occurred: {e}")


def action_limit_order(client: BinanceFuturesClient):
    """
    Handle limit order placement with user input.
    
    Args:
        client: Initialized Binance Futures client
    """
    print_header("PLACE LIMIT ORDER")
    
    try:
        # Get user input
        symbol = input("\nEnter symbol (e.g., BTCUSDT): ").strip().upper()
        side = input("Enter side (BUY/SELL): ").strip().upper()
        quantity = float(input("Enter quantity: ").strip())
        price = float(input("Enter limit price: ").strip())
        
        # Confirm order
        print(f"\n Order Summary:")
        print(f"   Symbol:   {symbol}")
        print(f"   Side:     {side}")
        print(f"   Quantity: {quantity}")
        print(f"   Price:    {price}")
        print(f"   Type:     LIMIT")
        
        confirm = input("\nConfirm order? (yes/no): ").strip().lower()
        if confirm not in ['yes', 'y']:
            print_info("Order canceled.")
            return
        
        # Place order
        logger.info(f"Placing limit order: {side} {quantity} {symbol} @ {price}")
        result = place_limit_order(client, symbol, side, quantity, price)
        
        if result:
            print_success("Limit order placed successfully!")
            print(f"\n   Order ID:      {result.get('orderId')}")
            print(f"   Symbol:        {result.get('symbol')}")
            print(f"   Side:          {result.get('side')}")
            print(f"   Status:        {result.get('status')}")
            print(f"   Quantity:      {result.get('origQty')}")
            print(f"   Price:         {result.get('price')}")
            print_info("Order is active and waiting to be filled.")
        else:
            print_error("Failed to place limit order. Check logs for details.")
            
    except ValueError as e:
        print_error(f"Invalid input: {e}")
    except Exception as e:
        logger.error(f"Error in limit order action: {e}")
        print_error(f"An error occurred: {e}")


def action_stop_limit_order(client: BinanceFuturesClient):
    """
    Handle stop-limit order placement with user input.
    
    Args:
        client: Initialized Binance Futures client
    """
    print_header("PLACE STOP-LIMIT ORDER")
    
    try:
        # Get user input
        symbol = input("\nEnter symbol (e.g., BTCUSDT): ").strip().upper()
        side = input("Enter side (BUY/SELL): ").strip().upper()
        quantity = float(input("Enter quantity: ").strip())
        stop_price = float(input("Enter stop price (trigger): ").strip())
        price = float(input("Enter limit price (execution): ").strip())
        
        # Confirm order
        print(f"\n Order Summary:")
        print(f"   Symbol:      {symbol}")
        print(f"   Side:        {side}")
        print(f"   Quantity:    {quantity}")
        print(f"   Stop Price:  {stop_price} (trigger)")
        print(f"   Limit Price: {price} (execution)")
        print(f"   Type:        STOP-LIMIT")
        
        confirm = input("\nConfirm order? (yes/no): ").strip().lower()
        if confirm not in ['yes', 'y']:
            print_info("Order canceled.")
            return
        
        # Place order
        logger.info(f"Placing stop-limit order: {side} {quantity} {symbol} @ stop:{stop_price}, limit:{price}")
        result = place_stop_limit_order(client, symbol, side, quantity, price, stop_price)
        
        if result:
            print_success("Stop-limit order placed successfully!")
            print(f"\n   Order ID:      {result.get('orderId')}")
            print(f"   Symbol:        {result.get('symbol')}")
            print(f"   Side:          {result.get('side')}")
            print(f"   Status:        {result.get('status')}")
            print(f"   Stop Price:    {result.get('stopPrice')}")
            print(f"   Limit Price:   {result.get('price')}")
            print_info(f"Order will trigger at {stop_price} and execute at {price}.")
        else:
            print_error("Failed to place stop-limit order. Check logs for details.")
            
    except ValueError as e:
        print_error(f"Invalid input: {e}")
    except Exception as e:
        logger.error(f"Error in stop-limit order action: {e}")
        print_error(f"An error occurred: {e}")


def action_oco_position_exit(client: BinanceFuturesClient):
    """
    Handle OCO position exit with user input.
    
    Args:
        client: Initialized Binance Futures client
    """
    print_header("PLACE OCO ORDERS (Position Exit)")
    
    print_info("This places take-profit and stop-loss orders for an EXISTING position.")
    print("      Make sure you have an open position before proceeding!")
    
    try:
        # Get user input
        symbol = input("\nEnter symbol (e.g., BTCUSDT): ").strip().upper()
        position_side = input("Enter position side (LONG/SHORT): ").strip().upper()
        position_quantity = float(input("Enter position quantity: ").strip())
        take_profit_price = float(input("Enter take-profit price: ").strip())
        stop_price = float(input("Enter stop-loss price: ").strip())
        
        # Confirm order
        print(f"\n OCO Order Summary:")
        print(f"   Symbol:           {symbol}")
        print(f"   Position Side:    {position_side}")
        print(f"   Position Qty:     {position_quantity}")
        print(f"   Take Profit:      {take_profit_price}")
        print(f"   Stop Loss:        {stop_price}")
        
        if position_side == 'LONG':
            print(f"\n   Closing orders will be SELL")
            if take_profit_price <= stop_price:
                print_error("For LONG: Take-profit must be ABOVE stop-loss!")
                return
        else:
            print(f"\n   Closing orders will be BUY")
            if take_profit_price >= stop_price:
                print_error("For SHORT: Take-profit must be BELOW stop-loss!")
                return
        
        confirm = input("\nConfirm you have an existing position? (yes/no): ").strip().lower()
        if confirm not in ['yes', 'y']:
            print_info("OCO orders canceled.")
            return
        
        # Place OCO orders
        logger.info(f"Placing OCO orders for {position_side} position: {symbol}")
        result = place_oco_for_position(client, symbol, position_side, position_quantity, 
                                       take_profit_price, stop_price)
        
        if result:
            print_success("OCO orders placed successfully!")
            
            tp_order = result.get('take_profit', {})
            print(f"\n    Take-Profit Order ID: {tp_order.get('orderId')}")
            print(f"      Stop Price: {tp_order.get('stopPrice')}")
            
            sl_order = result.get('stop_loss', {})
            print(f"\n    Stop-Loss Order ID: {sl_order.get('orderId')}")
            print(f"      Stop Price: {sl_order.get('stopPrice')}")
            
            print_info("When one order executes, the other will be automatically canceled.")
        else:
            print_error("Failed to place OCO orders. Check logs for details.")
            
    except ValueError as e:
        print_error(f"Invalid input: {e}")
    except Exception as e:
        logger.error(f"Error in OCO action: {e}")
        print_error(f"An error occurred: {e}")


def action_view_account_info(client: BinanceFuturesClient):
    """
    Display account information.
    
    Args:
        client: Initialized Binance Futures client
    """
    print_header("ACCOUNT INFORMATION")
    
    try:
        account_info = client.get_account_info()
        
        # Display account summary
        print(f"\n Account Summary:")
        print(f"   Total Wallet Balance:    {account_info.get('totalWalletBalance', 'N/A')} USDT")
        print(f"   Available Balance:       {account_info.get('availableBalance', 'N/A')} USDT")
        print(f"   Total Unrealized PnL:    {account_info.get('totalUnrealizedProfit', 'N/A')} USDT")
        print(f"   Total Margin Balance:    {account_info.get('totalMarginBalance', 'N/A')} USDT")
        
        # Display assets
        if 'assets' in account_info:
            assets_with_balance = [a for a in account_info['assets'] 
                                  if float(a.get('walletBalance', 0)) > 0]
            if assets_with_balance:
                print(f"\n Assets:")
                for asset in assets_with_balance:
                    print(f"   {asset['asset']:8} - Balance: {asset['walletBalance']:>15}")
        
        # Display positions
        if 'positions' in account_info:
            open_positions = [p for p in account_info['positions'] 
                            if float(p.get('positionAmt', 0)) != 0]
            if open_positions:
                print(f"\n Open Positions ({len(open_positions)}):")
                for pos in open_positions:
                    pnl = float(pos.get('unRealizedProfit', 0))
                    pnl_symbol = "📈" if pnl >= 0 else "📉"
                    print(f"   {pnl_symbol} {pos['symbol']:10} | Amt: {pos['positionAmt']:>10} | "
                          f"Entry: {pos['entryPrice']:>10} | PnL: {pnl:>10.2f} USDT")
            else:
                print(f"\n📈 Open Positions: None")
        
        logger.info("Account information retrieved successfully")
        
    except BinanceAPIException as e:
        logger.error(f"Binance API Error (Code: {e.code}): {e.message}")
        print_error(f"Failed to retrieve account information.")
        print(f"   Error Code: {e.code}")
        print(f"   Error Message: {e.message}")
        print("\n   Check bot.log for detailed error information.")
    except Exception as e:
        logger.error(f"Error in account info action: {e}")
        print_error(f"An error occurred: {e}")


def action_view_open_orders(client: BinanceFuturesClient):
    """
    Display open orders.
    
    Args:
        client: Initialized Binance Futures client
    """
    print_header("OPEN ORDERS")
    
    try:
        symbol = input("\nEnter symbol (leave empty for all): ").strip().upper()
        symbol = symbol if symbol else None
        
        open_orders = client.get_open_orders(symbol)
        
        if not open_orders:
            print_info("No open orders found.")
        else:
            print(f"\n Found {len(open_orders)} open order(s):\n")
            
            for i, order in enumerate(open_orders, 1):
                print(f"[{i}] Order ID: {order.get('orderId')}")
                print(f"    Symbol:    {order.get('symbol')}")
                print(f"    Type:      {order.get('type')}")
                print(f"    Side:      {order.get('side')}")
                print(f"    Quantity:  {order.get('origQty')}")
                print(f"    Status:    {order.get('status')}")
                
                if order.get('price') and order.get('price') != '0':
                    print(f"    Price:     {order.get('price')}")
                if order.get('stopPrice') and order.get('stopPrice') != '0':
                    print(f"    Stop Price: {order.get('stopPrice')}")
                
                print()
        
        logger.info(f"Retrieved {len(open_orders)} open order(s)")
        
    except BinanceAPIException as e:
        logger.error(f"Binance API Error (Code: {e.code}): {e.message}")
        print_error(f"Failed to retrieve open orders.")
        print(f"   Error Code: {e.code}")
        print(f"   Error Message: {e.message}")
        print("\n   Check bot.log for detailed error information.")
    except Exception as e:
        logger.error(f"Error in open orders action: {e}")
        print_error(f"An error occurred: {e}")


def action_cancel_order(client: BinanceFuturesClient):
    """
    Cancel an order.
    
    Args:
        client: Initialized Binance Futures client
    """
    print_header("CANCEL ORDER")
    
    try:
        symbol = input("\nEnter symbol (e.g., BTCUSDT): ").strip().upper()
        order_id = int(input("Enter order ID: ").strip())
        
        # Confirm cancellation
        print(f"\n You are about to cancel:")
        print(f"   Symbol:   {symbol}")
        print(f"   Order ID: {order_id}")
        
        confirm = input("\nConfirm cancellation? (yes/no): ").strip().lower()
        if confirm not in ['yes', 'y']:
            print_info("Cancellation aborted.")
            return
        
        # Cancel order
        logger.info(f"Canceling order: {symbol} - {order_id}")
        result = client.cancel_order(symbol, order_id)
        
        if result:
            print_success("Order canceled successfully!")
            print(f"\n   Order ID:  {result.get('orderId')}")
            print(f"   Symbol:    {result.get('symbol')}")
            print(f"   Status:    {result.get('status')}")
        else:
            print_error("Failed to cancel order. Check logs for details.")
            
    except ValueError as e:
        print_error(f"Invalid input: {e}")
    except BinanceAPIException as e:
        logger.error(f"Binance API Error (Code: {e.code}): {e.message}")
        print_error(f"Failed to cancel order.")
        print(f"   Error Code: {e.code}")
        print(f"   Error Message: {e.message}")
        print("\n   Check bot.log for detailed error information.")
    except Exception as e:
        logger.error(f"Error in cancel order action: {e}")
        print_error(f"An error occurred: {e}")


def action_twap_order(client: BinanceFuturesClient):
    """
    Execute a TWAP (Time-Weighted Average Price) order.
    
    Args:
        client: Initialized Binance Futures client
    """
    print_header("TWAP ORDER (Time-Weighted Average Price)")
    
    print("\n TWAP Strategy:")
    print("   Splits a large order into smaller chunks executed at regular intervals")
    print("   to achieve an average execution price close to the time-weighted average.")
    print()
    
    try:
        # Get user inputs
        symbol = input("Enter symbol (e.g., BTCUSDT): ").strip()
        side = input("Enter side (BUY/SELL): ").strip()
        
        total_quantity_input = input("Enter total quantity: ").strip()
        total_quantity = float(total_quantity_input)
        
        num_orders_input = input("Enter number of chunks (orders): ").strip()
        num_orders = int(num_orders_input)
        
        interval_seconds_input = input("Enter interval between chunks (seconds): ").strip()
        interval_seconds = int(interval_seconds_input)
        
        # Calculate and display TWAP details
        chunk_quantity = total_quantity / num_orders
        total_duration = (num_orders - 1) * interval_seconds
        
        print("\n" + "─" * 70)
        print("  TWAP Order Summary:")
        print(f"   Symbol:           {symbol}")
        print(f"   Side:             {side}")
        print(f"   Total Quantity:   {total_quantity}")
        print(f"   Number of Chunks: {num_orders}")
        print(f"   Chunk Size:       {chunk_quantity}")
        print(f"   Interval:         {interval_seconds} seconds")
        print(f"   Total Duration:   ~{total_duration} seconds (~{total_duration/60:.1f} minutes)")
        print("─" * 70)
        
        # Confirmation
        confirm = input("\n  Execute TWAP order? (yes/no): ").strip().lower()
        
        if confirm != 'yes':
            print_error("TWAP order cancelled by user.")
            logger.info("TWAP order cancelled by user")
            return
        
        print("\n Starting TWAP execution...")
        print("   This may take several minutes. Please wait...\n")
        
        logger.info(f"Executing TWAP order: {side} {total_quantity} {symbol} "
                   f"in {num_orders} chunks over {total_duration}s")
        
        # Execute TWAP order
        result = execute_twap_order(
            client=client,
            symbol=symbol,
            side=side,
            total_quantity=total_quantity,
            num_orders=num_orders,
            interval_seconds=interval_seconds
        )
        
        if result:
            # Display results
            print("\n" + "=" * 70)
            print("✓ TWAP EXECUTION COMPLETED")
            print("=" * 70)
            print(f"\n Execution Summary:")
            print(f"   Total Chunks:        {result['total_chunks']}")
            print(f"   Successful:          {result['executed_chunks']} ✓")
            print(f"   Failed:              {result['failed_chunks']} ✗")
            print(f"   Target Quantity:     {result['target_quantity']}")
            print(f"   Executed Quantity:   {result['executed_quantity']}")
            print(f"   Execution Rate:      {(result['executed_chunks'] / result['total_chunks'] * 100):.1f}%")
            
            if result['executed_chunks'] > 0:
                print(f"   Avg Execution Price: {result['avg_execution_price']:.2f}")
            
            # Show individual chunk details
            if result['executed_orders']:
                print(f"\n✓ Successful Chunks:")
                for order in result['executed_orders']:
                    print(f"   Chunk {order['chunk_number']}: "
                          f"Order ID {order['order_id']} | "
                          f"Qty: {order['executed_qty']} | "
                          f"Price: {order['avg_price']}")
            
            # Show failed chunks
            if result['failed_orders']:
                print(f"\n✗ Failed Chunks:")
                for order in result['failed_orders']:
                    print(f"   Chunk {order['chunk_number']}: "
                          f"Error {order['error_code']} - {order['error_message']}")
            
            print("=" * 70)
            
            if result['success']:
                print_success("All TWAP chunks executed successfully!")
            else:
                print_error(f"{result['failed_chunks']} chunk(s) failed. Check logs for details.")
        else:
            print_error("TWAP execution failed. Check logs for details.")
            
    except ValueError as e:
        print_error(f"Invalid input: {e}")
        logger.error(f"Invalid input in TWAP action: {e}")
    except Exception as e:
        logger.error(f"Error in TWAP action: {e}")
        print_error(f"An error occurred: {e}")


def action_grid_trading(client: BinanceFuturesClient):
    """
    Start Grid Trading strategy.
    
    Args:
        client: Initialized Binance Futures client
    """
    print_header("GRID TRADING STRATEGY")
    
    print("\n Grid Trading:")
    print("   Places buy limit orders below current price and sell limit orders above.")
    print("   When orders fill, opposite orders are automatically placed.")
    print("   This creates a 'grid' that profits from price oscillations.")
    print()
    print("  WARNING: Grid trading runs continuously until you stop it.")
    print("   Press Ctrl+C to stop the grid gracefully.")
    print()
    
    try:
        # Get user inputs
        symbol = input("Enter symbol (e.g., BTCUSDT): ").strip()
        
        quantity_input = input("Enter quantity per grid level: ").strip()
        quantity_per_grid = float(quantity_input)
        
        lower_input = input("Enter lower price bound: ").strip()
        lower_bound = float(lower_input)
        
        upper_input = input("Enter upper price bound: ").strip()
        upper_bound = float(upper_input)
        
        grids_input = input("Enter number of grid levels: ").strip()
        num_grids = int(grids_input)
        
        interval_input = input("Enter monitoring interval (seconds, recommended: 60): ").strip()
        monitor_interval = int(interval_input)
        
        # Calculate grid details
        price_range = upper_bound - lower_bound
        grid_step = price_range / num_grids
        total_quantity = quantity_per_grid * num_grids * 2  # Buy + Sell orders
        
        print("\n" + "─" * 70)
        print("  Grid Trading Configuration:")
        print(f"   Symbol:              {symbol}")
        print(f"   Quantity per Grid:   {quantity_per_grid}")
        print(f"   Lower Bound:         {lower_bound}")
        print(f"   Upper Bound:         {upper_bound}")
        print(f"   Price Range:         {price_range}")
        print(f"   Number of Grids:     {num_grids}")
        print(f"   Grid Step:           {grid_step:.2f}")
        print(f"   Total Initial Qty:   {total_quantity} ({num_grids} BUY + {num_grids} SELL)")
        print(f"   Monitor Interval:    {monitor_interval}s")
        print("─" * 70)
        
        print("\n Grid Levels:")
        print(f"\n   BUY Orders (Lower Half):")
        for i in range(num_grids):
            price = lower_bound + (i * grid_step)
            print(f"      Level {i}: BUY {quantity_per_grid} @ {price:.2f}")
        
        print(f"\n   SELL Orders (Upper Half):")
        for i in range(num_grids):
            price = upper_bound - (i * grid_step)
            print(f"      Level {num_grids + i}: SELL {quantity_per_grid} @ {price:.2f}")
        
        print("\n" + "─" * 70)
        
        # Confirmation
        print("\n  IMPORTANT:")
        print("   • Grid will run continuously until you press Ctrl+C")
        print("   • Ensure you have sufficient margin for all orders")
        print("   • Monitor the bot.log file for detailed activity")
        print("   • The grid will automatically replace filled orders")
        
        confirm = input("\n  Start grid trading? (yes/no): ").strip().lower()
        
        if confirm != 'yes':
            print_error("Grid trading cancelled by user.")
            logger.info("Grid trading cancelled by user")
            return
        
        print("\n Starting Grid Trading...")
        print("   Press Ctrl+C at any time to stop gracefully.\n")
        
        logger.info(f"Starting grid trading: {symbol} | "
                   f"Range: {lower_bound}-{upper_bound} | "
                   f"Grids: {num_grids} | Qty: {quantity_per_grid}")
        
        # Start grid trading
        result = start_grid_trading(
            client=client,
            symbol=symbol,
            quantity_per_grid=quantity_per_grid,
            lower_bound=lower_bound,
            upper_bound=upper_bound,
            num_grids=num_grids,
            monitor_interval_seconds=monitor_interval
        )
        
        if result:
            # Display results
            print("\n" + "=" * 70)
            print("✓ GRID TRADING SESSION COMPLETED")
            print("=" * 70)
            print(f"\n Session Summary:")
            print(f"   Monitoring Cycles:      {result['cycles']}")
            print(f"   Total BUY Orders:       {result['total_buy_orders']}")
            print(f"   Total SELL Orders:      {result['total_sell_orders']}")
            print(f"   BUY Orders Filled:      {result['buy_fills']}")
            print(f"   SELL Orders Filled:     {result['sell_fills']}")
            print(f"   Orders Cancelled:       {result['orders_cancelled']}")
            print(f"   Total Trades Executed:  {result['total_trades']}")
            print("=" * 70)
            
            if result['total_trades'] > 0:
                print_success(f"Grid executed {result['total_trades']} trades successfully!")
            else:
                print("\n   No trades were executed during this session.")
        else:
            print_error("Grid trading failed to start. Check logs for details.")
            
    except ValueError as e:
        print_error(f"Invalid input: {e}")
        logger.error(f"Invalid input in grid trading action: {e}")
    except KeyboardInterrupt:
        print("\n\n  Grid trading interrupted by user.")
        logger.info("Grid trading interrupted by user")
    except Exception as e:
        logger.error(f"Error in grid trading action: {e}")
        print_error(f"An error occurred: {e}")
