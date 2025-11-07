# src/advanced/twap.py
"""
TWAP (Time-Weighted Average Price) order implementation for Binance Futures.
Splits large orders into smaller chunks executed at regular intervals.
"""

import sys
import os
import time

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from binance.exceptions import BinanceAPIException
from src.binance_client import BinanceFuturesClient
from src.validators import validate_symbol, validate_side, validate_quantity
from src.logger import setup_logging


# Initialize logger for this module
logger = setup_logging(__name__)


def execute_twap_order(client: BinanceFuturesClient, symbol: str, side: str, 
                       total_quantity: float, num_orders: int, interval_seconds: int):
    """
    Execute a TWAP (Time-Weighted Average Price) order strategy.
    
    Splits a large order into smaller equal-sized chunks and executes them
    at regular intervals to achieve an average execution price close to the
    time-weighted average price.
    
    Args:
        client (BinanceFuturesClient): Initialized Binance Futures client
        symbol (str): Trading pair symbol (e.g., 'BTCUSDT')
        side (str): Order side ('BUY' or 'SELL')
        total_quantity (float): Total quantity to trade across all chunks
        num_orders (int): Number of chunks to split the order into
        interval_seconds (int): Time interval in seconds between each chunk order
        
    Returns:
        dict: Summary of TWAP execution with results for each chunk, or None on failure
        
    Example:
        >>> client = BinanceFuturesClient(api_key, api_secret)
        >>> result = execute_twap_order(client, 'BTCUSDT', 'BUY', 0.005, 5, 5)
        >>> # Executes 5 orders of 0.001 BTC each, 5 seconds apart
    """
    logger.info("=" * 70)
    logger.info("TWAP Order Execution Started")
    logger.info("=" * 70)
    
    # ========================================
    # Input Validation
    # ========================================
    logger.debug(f"Validating TWAP parameters: symbol={symbol}, side={side}, "
                f"total_quantity={total_quantity}, num_orders={num_orders}, "
                f"interval_seconds={interval_seconds}")
    
    # Validate symbol
    if not validate_symbol(symbol):
        logger.error(f"Invalid symbol: {symbol}. Symbol must be uppercase, at least 6 characters, "
                    f"and end with USDT/BUSD/USD/BTC/ETH")
        return None
    
    # Validate side
    if not validate_side(side):
        logger.error(f"Invalid side: {side}. Side must be 'BUY' or 'SELL'")
        return None
    
    # Validate total quantity
    if not validate_quantity(total_quantity):
        logger.error(f"Invalid total_quantity: {total_quantity}. Quantity must be a positive number greater than 0")
        return None
    
    # Validate num_orders (must be positive integer)
    try:
        num_orders = int(num_orders)
        if num_orders <= 0:
            logger.error(f"Invalid num_orders: {num_orders}. Must be a positive integer greater than 0")
            return None
    except (ValueError, TypeError):
        logger.error(f"Invalid num_orders: {num_orders}. Must be a positive integer")
        return None
    
    # Validate interval_seconds (must be positive integer)
    try:
        interval_seconds = int(interval_seconds)
        if interval_seconds <= 0:
            logger.error(f"Invalid interval_seconds: {interval_seconds}. Must be a positive integer greater than 0")
            return None
    except (ValueError, TypeError):
        logger.error(f"Invalid interval_seconds: {interval_seconds}. Must be a positive integer")
        return None
    
    logger.info("✓ All TWAP parameters validated successfully")
    
    # ========================================
    # Calculate Chunk Quantity
    # ========================================
    chunk_quantity = total_quantity / num_orders
    logger.info(f"TWAP Configuration:")
    logger.info(f"  Symbol:           {symbol}")
    logger.info(f"  Side:             {side}")
    logger.info(f"  Total Quantity:   {total_quantity}")
    logger.info(f"  Number of Orders: {num_orders}")
    logger.info(f"  Chunk Quantity:   {chunk_quantity}")
    logger.info(f"  Interval:         {interval_seconds} seconds")
    logger.info(f"  Total Duration:   ~{(num_orders - 1) * interval_seconds} seconds")
    
    # ========================================
    # Execute Orders in Loop
    # ========================================
    executed_orders = []
    failed_orders = []
    total_executed_qty = 0.0
    
    logger.info("-" * 70)
    logger.info("Starting TWAP execution...")
    logger.info("-" * 70)
    
    for i in range(num_orders):
        chunk_number = i + 1
        
        logger.info(f"📊 Placing TWAP chunk {chunk_number} of {num_orders}...")
        logger.info(f"   Chunk Quantity: {chunk_quantity} {symbol}")
        
        # Construct order parameters
        order_params = {
            'symbol': symbol.upper(),
            'side': side.upper(),
            'type': 'MARKET',
            'quantity': chunk_quantity,
            'recvWindow': client.recv_window
        }
        
        try:
            # Place the market order
            logger.debug(f"Executing chunk {chunk_number} with params: {order_params}")
            response = client.client.futures_create_order(**order_params)
            
            # Log success
            executed_qty = float(response.get('executedQty', 0))
            avg_price = float(response.get('avgPrice', 0))
            
            logger.info(f"✓ Chunk {chunk_number} executed successfully!")
            logger.info(f"   Order ID:      {response.get('orderId')}")
            logger.info(f"   Executed Qty:  {executed_qty}")
            logger.info(f"   Avg Price:     {avg_price}")
            logger.info(f"   Status:        {response.get('status')}")
            
            # Store successful order
            executed_orders.append({
                'chunk_number': chunk_number,
                'order_id': response.get('orderId'),
                'executed_qty': executed_qty,
                'avg_price': avg_price,
                'status': response.get('status'),
                'response': response
            })
            
            total_executed_qty += executed_qty
            
        except BinanceAPIException as e:
            logger.error(f"✗ Chunk {chunk_number} failed!")
            logger.error(f"   Binance API Error (Code: {e.code}): {e.message}")
            
            # Store failed order
            failed_orders.append({
                'chunk_number': chunk_number,
                'error_code': e.code,
                'error_message': e.message
            })
            
            # Continue with remaining chunks despite failure
            logger.warning(f"Continuing with remaining TWAP chunks...")
            
        except Exception as e:
            logger.error(f"✗ Chunk {chunk_number} failed with unexpected error!")
            logger.error(f"   Error: {type(e).__name__}: {e}")
            
            # Store failed order
            failed_orders.append({
                'chunk_number': chunk_number,
                'error_code': 'UNKNOWN',
                'error_message': str(e)
            })
            
            # Continue with remaining chunks
            logger.warning(f"Continuing with remaining TWAP chunks...")
        
        # Sleep before next chunk (except after the last one)
        if chunk_number < num_orders:
            logger.info(f"⏳ Waiting {interval_seconds} seconds before next chunk...")
            time.sleep(interval_seconds)
            logger.info("")  # Empty line for readability
    
    # ========================================
    # TWAP Execution Summary
    # ========================================
    logger.info("=" * 70)
    logger.info("TWAP Order Execution Completed")
    logger.info("=" * 70)
    logger.info(f"Summary:")
    logger.info(f"  Total Chunks:        {num_orders}")
    logger.info(f"  Successful:          {len(executed_orders)}")
    logger.info(f"  Failed:              {len(failed_orders)}")
    logger.info(f"  Target Quantity:     {total_quantity}")
    logger.info(f"  Executed Quantity:   {total_executed_qty}")
    logger.info(f"  Execution Rate:      {(len(executed_orders) / num_orders * 100):.1f}%")
    
    if executed_orders:
        # Calculate average execution price
        total_value = sum(order['executed_qty'] * order['avg_price'] for order in executed_orders)
        avg_execution_price = total_value / total_executed_qty if total_executed_qty > 0 else 0
        logger.info(f"  Avg Execution Price: {avg_execution_price:.2f}")
    
    if failed_orders:
        logger.warning(f"⚠️  {len(failed_orders)} chunk(s) failed. Check logs for details.")
    
    logger.info("=" * 70)
    
    # Return summary
    return {
        'success': len(failed_orders) == 0,
        'total_chunks': num_orders,
        'executed_chunks': len(executed_orders),
        'failed_chunks': len(failed_orders),
        'target_quantity': total_quantity,
        'executed_quantity': total_executed_qty,
        'executed_orders': executed_orders,
        'failed_orders': failed_orders,
        'avg_execution_price': avg_execution_price if executed_orders else 0
    }
