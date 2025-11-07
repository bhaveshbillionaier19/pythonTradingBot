# src/advanced/grid.py
"""
Grid Trading strategy implementation for Binance Futures.
Places buy and sell limit orders in a grid pattern and monitors/replaces filled orders.
"""

import sys
import os
import time
import math
from typing import Dict, List, Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from binance.exceptions import BinanceAPIException
from src.binance_client import BinanceFuturesClient
from src.validators import validate_symbol, validate_quantity, validate_price
from src.logger import setup_logging


# Initialize logger for this module
logger = setup_logging(__name__)

# Global flag for graceful shutdown
grid_running = True


def stop_grid():
    """Signal the grid to stop gracefully."""
    global grid_running
    grid_running = False
    logger.info("Grid stop signal received")


def start_grid_trading(client: BinanceFuturesClient, symbol: str, quantity_per_grid: float,
                       lower_bound: float, upper_bound: float, num_grids: int,
                       monitor_interval_seconds: int = 60):
    """
    Start a Grid Trading strategy.
    
    Places a series of buy limit orders below current price and sell limit orders
    above current price. Monitors filled orders and replaces them with opposite orders.
    
    Args:
        client (BinanceFuturesClient): Initialized Binance Futures client
        symbol (str): Trading pair symbol (e.g., 'BTCUSDT')
        quantity_per_grid (float): Quantity for each grid order
        lower_bound (float): Lower price boundary for the grid
        upper_bound (float): Upper price boundary for the grid
        num_grids (int): Number of grid levels (buy and sell orders each)
        monitor_interval_seconds (int): Seconds to wait between monitoring cycles
        
    Returns:
        dict: Summary of grid trading session, or None on failure
        
    Example:
        >>> client = BinanceFuturesClient(api_key, api_secret)
        >>> result = start_grid_trading(client, 'BTCUSDT', 0.001, 40000, 50000, 5, 60)
        >>> # Creates 5 buy orders from 40000-45000 and 5 sell orders from 45000-50000
    """
    global grid_running
    grid_running = True
    
    logger.info("=" * 70)
    logger.info("GRID TRADING STRATEGY STARTED")
    logger.info("=" * 70)
    
    # ========================================
    # Input Validation
    # ========================================
    logger.debug(f"Validating grid parameters: symbol={symbol}, quantity={quantity_per_grid}, "
                f"lower={lower_bound}, upper={upper_bound}, grids={num_grids}")
    
    # Validate symbol
    if not validate_symbol(symbol):
        logger.error(f"Invalid symbol: {symbol}")
        return None
    
    # Validate quantity per grid
    if not validate_quantity(quantity_per_grid):
        logger.error(f"Invalid quantity_per_grid: {quantity_per_grid}. Must be positive.")
        return None
    
    # Validate lower bound
    if not validate_price(lower_bound):
        logger.error(f"Invalid lower_bound: {lower_bound}. Must be positive.")
        return None
    
    # Validate upper bound
    if not validate_price(upper_bound):
        logger.error(f"Invalid upper_bound: {upper_bound}. Must be positive.")
        return None
    
    # Validate bounds relationship
    if upper_bound <= lower_bound:
        logger.error(f"Invalid bounds: upper_bound ({upper_bound}) must be greater than "
                    f"lower_bound ({lower_bound})")
        return None
    
    # Validate num_grids
    try:
        num_grids = int(num_grids)
        if num_grids <= 0:
            logger.error(f"Invalid num_grids: {num_grids}. Must be positive integer.")
            return None
    except (ValueError, TypeError):
        logger.error(f"Invalid num_grids: {num_grids}. Must be an integer.")
        return None
    
    # Validate monitor interval
    try:
        monitor_interval_seconds = int(monitor_interval_seconds)
        if monitor_interval_seconds <= 0:
            logger.error(f"Invalid monitor_interval: {monitor_interval_seconds}. Must be positive.")
            return None
    except (ValueError, TypeError):
        logger.error(f"Invalid monitor_interval: {monitor_interval_seconds}. Must be an integer.")
        return None
    
    logger.info("✓ All grid parameters validated successfully")
    
    # ========================================
    # Calculate Grid Spacing
    # ========================================
    price_range = upper_bound - lower_bound
    grid_step = price_range / num_grids
    
    logger.info(f"Grid Configuration:")
    logger.info(f"  Symbol:           {symbol}")
    logger.info(f"  Quantity/Grid:    {quantity_per_grid}")
    logger.info(f"  Lower Bound:      {lower_bound}")
    logger.info(f"  Upper Bound:      {upper_bound}")
    logger.info(f"  Price Range:      {price_range}")
    logger.info(f"  Number of Grids:  {num_grids}")
    logger.info(f"  Grid Step:        {grid_step}")
    logger.info(f"  Monitor Interval: {monitor_interval_seconds}s")
    
    # ========================================
    # Grid State Tracking
    # ========================================
    # Dictionary to track grid orders: {order_id: {'side': 'BUY/SELL', 'price': float, 'grid_level': int}}
    grid_orders = {}
    
    # Statistics
    total_buy_orders_placed = 0
    total_sell_orders_placed = 0
    total_buy_fills = 0
    total_sell_fills = 0
    
    # ========================================
    # Place Initial Grid Orders
    # ========================================
    logger.info("-" * 70)
    logger.info("Placing Initial Grid Orders...")
    logger.info("-" * 70)
    
    # Place BUY limit orders (from lower_bound upwards)
    logger.info(f"\n📉 Placing {num_grids} BUY limit orders:")
    for i in range(num_grids):
        grid_level = i
        price = lower_bound + (i * grid_step)
        
        # Round price to appropriate decimal places
        price = round(price, 2)
        
        try:
            logger.info(f"   Grid Level {grid_level}: BUY {quantity_per_grid} @ {price}")
            
            order_params = {
                'symbol': symbol.upper(),
                'side': 'BUY',
                'type': 'LIMIT',
                'quantity': quantity_per_grid,
                'price': price,
                'timeInForce': 'GTC',
                'recvWindow': client.recv_window
            }
            
            response = client.client.futures_create_order(**order_params)
            order_id = response.get('orderId')
            
            # Track this order
            grid_orders[order_id] = {
                'side': 'BUY',
                'price': price,
                'grid_level': grid_level,
                'quantity': quantity_per_grid
            }
            
            total_buy_orders_placed += 1
            logger.info(f"   ✓ Order ID: {order_id}")
            
        except BinanceAPIException as e:
            logger.error(f"   ✗ Failed to place BUY order at {price}: "
                        f"Code {e.code} - {e.message}")
        except Exception as e:
            logger.error(f"   ✗ Unexpected error placing BUY order: {e}")
    
    # Place SELL limit orders (from upper_bound downwards)
    logger.info(f"\n📈 Placing {num_grids} SELL limit orders:")
    for i in range(num_grids):
        grid_level = num_grids + i  # Offset to distinguish from buy levels
        price = upper_bound - (i * grid_step)
        
        # Round price to appropriate decimal places
        price = round(price, 2)
        
        try:
            logger.info(f"   Grid Level {grid_level}: SELL {quantity_per_grid} @ {price}")
            
            order_params = {
                'symbol': symbol.upper(),
                'side': 'SELL',
                'type': 'LIMIT',
                'quantity': quantity_per_grid,
                'price': price,
                'timeInForce': 'GTC',
                'recvWindow': client.recv_window
            }
            
            response = client.client.futures_create_order(**order_params)
            order_id = response.get('orderId')
            
            # Track this order
            grid_orders[order_id] = {
                'side': 'SELL',
                'price': price,
                'grid_level': grid_level,
                'quantity': quantity_per_grid
            }
            
            total_sell_orders_placed += 1
            logger.info(f"   ✓ Order ID: {order_id}")
            
        except BinanceAPIException as e:
            logger.error(f"   ✗ Failed to place SELL order at {price}: "
                        f"Code {e.code} - {e.message}")
        except Exception as e:
            logger.error(f"   ✗ Unexpected error placing SELL order: {e}")
    
    logger.info("-" * 70)
    logger.info(f"Initial Grid Setup Complete:")
    logger.info(f"  BUY orders placed:  {total_buy_orders_placed}")
    logger.info(f"  SELL orders placed: {total_sell_orders_placed}")
    logger.info(f"  Total orders:       {len(grid_orders)}")
    logger.info("-" * 70)
    
    if len(grid_orders) == 0:
        logger.error("No grid orders were placed successfully. Exiting.")
        return None
    
    # ========================================
    # Monitoring and Replacement Loop
    # ========================================
    logger.info("\n🔄 Starting Grid Monitoring Loop...")
    logger.info("   Press Ctrl+C to stop the grid gracefully.\n")
    
    cycle_count = 0
    
    try:
        while grid_running:
            cycle_count += 1
            logger.info(f"--- Monitoring Cycle {cycle_count} ---")
            
            try:
                # Fetch all open orders for this symbol
                open_orders = client.get_open_orders(symbol=symbol)
                open_order_ids = {order['orderId'] for order in open_orders}
                
                logger.debug(f"Found {len(open_orders)} open orders for {symbol}")
                
                # Check which grid orders are no longer open (filled or cancelled)
                filled_order_ids = []
                for order_id in list(grid_orders.keys()):
                    if order_id not in open_order_ids:
                        filled_order_ids.append(order_id)
                
                # Process filled orders
                if filled_order_ids:
                    logger.info(f"🎯 Detected {len(filled_order_ids)} filled order(s)!")
                    
                    for order_id in filled_order_ids:
                        order_info = grid_orders[order_id]
                        side = order_info['side']
                        price = order_info['price']
                        grid_level = order_info['grid_level']
                        quantity = order_info['quantity']
                        
                        logger.info(f"\n   Order {order_id} filled:")
                        logger.info(f"   Side:  {side}")
                        logger.info(f"   Price: {price}")
                        logger.info(f"   Level: {grid_level}")
                        
                        # Update statistics
                        if side == 'BUY':
                            total_buy_fills += 1
                        else:
                            total_sell_fills += 1
                        
                        # Remove from tracking
                        del grid_orders[order_id]
                        
                        # Place opposite order
                        try:
                            if side == 'BUY':
                                # BUY filled, place SELL at next grid level up
                                new_price = price + grid_step
                                new_side = 'SELL'
                                logger.info(f"   → Placing SELL order at {new_price}")
                            else:
                                # SELL filled, place BUY at next grid level down
                                new_price = price - grid_step
                                new_side = 'BUY'
                                logger.info(f"   → Placing BUY order at {new_price}")
                            
                            # Round price
                            new_price = round(new_price, 2)
                            
                            # Check if new price is within bounds
                            if new_price < lower_bound or new_price > upper_bound:
                                logger.warning(f"   ⚠️  New price {new_price} outside grid bounds. "
                                             f"Skipping replacement.")
                                continue
                            
                            # Place replacement order
                            order_params = {
                                'symbol': symbol.upper(),
                                'side': new_side,
                                'type': 'LIMIT',
                                'quantity': quantity,
                                'price': new_price,
                                'timeInForce': 'GTC',
                                'recvWindow': client.recv_window
                            }
                            
                            response = client.client.futures_create_order(**order_params)
                            new_order_id = response.get('orderId')
                            
                            # Track new order
                            grid_orders[new_order_id] = {
                                'side': new_side,
                                'price': new_price,
                                'grid_level': grid_level,  # Reuse grid level
                                'quantity': quantity
                            }
                            
                            if new_side == 'BUY':
                                total_buy_orders_placed += 1
                            else:
                                total_sell_orders_placed += 1
                            
                            logger.info(f"   ✓ Replacement order placed: {new_order_id}")
                            
                        except BinanceAPIException as e:
                            logger.error(f"   ✗ Failed to place replacement order: "
                                       f"Code {e.code} - {e.message}")
                        except Exception as e:
                            logger.error(f"   ✗ Unexpected error placing replacement: {e}")
                
                else:
                    logger.info(f"   No filled orders detected. Grid stable.")
                
                # Show current grid status
                buy_count = sum(1 for o in grid_orders.values() if o['side'] == 'BUY')
                sell_count = sum(1 for o in grid_orders.values() if o['side'] == 'SELL')
                logger.info(f"   Active orders: {len(grid_orders)} "
                          f"(BUY: {buy_count}, SELL: {sell_count})")
                
            except BinanceAPIException as e:
                logger.error(f"API error in monitoring cycle: Code {e.code} - {e.message}")
            except Exception as e:
                logger.error(f"Unexpected error in monitoring cycle: {e}")
            
            # Sleep before next cycle
            if grid_running:
                logger.info(f"   ⏳ Sleeping for {monitor_interval_seconds}s...\n")
                time.sleep(monitor_interval_seconds)
    
    except KeyboardInterrupt:
        logger.info("\n⚠️  Keyboard interrupt received. Stopping grid...")
        grid_running = False
    
    # ========================================
    # Cleanup and Summary
    # ========================================
    logger.info("\n" + "=" * 70)
    logger.info("GRID TRADING STOPPED")
    logger.info("=" * 70)
    
    # Cancel all remaining grid orders
    logger.info("Cancelling remaining grid orders...")
    cancelled_count = 0
    for order_id in list(grid_orders.keys()):
        try:
            client.cancel_order(symbol, order_id)
            cancelled_count += 1
            logger.info(f"   ✓ Cancelled order {order_id}")
        except Exception as e:
            logger.error(f"   ✗ Failed to cancel order {order_id}: {e}")
    
    # Final statistics
    logger.info("\n" + "=" * 70)
    logger.info("GRID TRADING SUMMARY")
    logger.info("=" * 70)
    logger.info(f"Session Statistics:")
    logger.info(f"  Monitoring Cycles:      {cycle_count}")
    logger.info(f"  Total BUY Orders:       {total_buy_orders_placed}")
    logger.info(f"  Total SELL Orders:      {total_sell_orders_placed}")
    logger.info(f"  BUY Orders Filled:      {total_buy_fills}")
    logger.info(f"  SELL Orders Filled:     {total_sell_fills}")
    logger.info(f"  Orders Cancelled:       {cancelled_count}")
    logger.info(f"  Total Trades:           {total_buy_fills + total_sell_fills}")
    logger.info("=" * 70)
    
    return {
        'success': True,
        'cycles': cycle_count,
        'total_buy_orders': total_buy_orders_placed,
        'total_sell_orders': total_sell_orders_placed,
        'buy_fills': total_buy_fills,
        'sell_fills': total_sell_fills,
        'orders_cancelled': cancelled_count,
        'total_trades': total_buy_fills + total_sell_fills
    }
