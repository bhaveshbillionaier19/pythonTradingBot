# src/advanced/oco.py
"""
OCO (One-Cancels-the-Other) order implementation for Binance Futures trading.
Places simultaneous take-profit and stop-loss orders for existing positions.

An OCO order places two orders: a take-profit order and a stop-loss order.
When one executes, the other is automatically canceled.
"""

from binance.exceptions import BinanceAPIException
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.binance_client import BinanceFuturesClient
from src.validators import validate_symbol, validate_side, validate_quantity, validate_price
from src.logger import setup_logging


# Initialize logger for this module
logger = setup_logging(__name__)


def place_oco_for_position(client: BinanceFuturesClient, symbol: str, position_side: str, 
                           position_quantity: float, take_profit_price: float, stop_price: float):
    """
    Place OCO (One-Cancels-the-Other) orders for an existing position.
    
    This function places two contingent orders:
    1. TAKE_PROFIT_MARKET: Closes position at profit when price reaches take_profit_price
    2. STOP_MARKET: Closes position at loss when price reaches stop_price
    
    When one order executes, the other is automatically canceled by Binance.
    
    Args:
        client (BinanceFuturesClient): Initialized Binance Futures client
        symbol (str): Trading pair symbol (e.g., 'BTCUSDT')
        position_side (str): Current position side ('LONG' or 'SHORT')
        position_quantity (float): Position quantity to close
        take_profit_price (float): Price to take profit
        stop_price (float): Price to stop loss
        
    Returns:
        dict: Dictionary containing both order responses
              {'take_profit': {...}, 'stop_loss': {...}}
              Returns None if any order fails
    
    Position Logic:
        - LONG Position: Places SELL orders (take_profit above, stop below current price)
        - SHORT Position: Places BUY orders (take_profit below, stop above current price)
    
    Example Usage:
        # After opening a LONG position with market order
        result = place_oco_for_position(
            client=client,
            symbol='BTCUSDT',
            position_side='LONG',
            position_quantity=0.001,
            take_profit_price=26000.00,  # Above current price
            stop_price=24000.00          # Below current price
        )
    """
    # Validate inputs
    logger.debug(f"Validating OCO order parameters: symbol={symbol}, position_side={position_side}, "
                 f"quantity={position_quantity}, take_profit={take_profit_price}, stop={stop_price}")
    
    if not validate_symbol(symbol):
        logger.error(f"Invalid symbol: {symbol}")
        return None
    
    # Validate position side
    position_side_upper = position_side.upper()
    if position_side_upper not in ['LONG', 'SHORT']:
        logger.error(f"Invalid position_side: {position_side}. Must be 'LONG' or 'SHORT'")
        return None
    
    if not validate_quantity(position_quantity):
        logger.error(f"Invalid position_quantity: {position_quantity}")
        return None
    
    if not validate_price(take_profit_price):
        logger.error(f"Invalid take_profit_price: {take_profit_price}")
        return None
    
    if not validate_price(stop_price):
        logger.error(f"Invalid stop_price: {stop_price}")
        return None
    
    # Validate price logic based on position side
    if position_side_upper == 'LONG':
        # For LONG: take_profit should be above stop_price
        if take_profit_price <= stop_price:
            logger.error(f"LONG position: take_profit_price ({take_profit_price}) must be greater than "
                        f"stop_price ({stop_price})")
            return None
        logger.info(f"LONG position: TP at {take_profit_price} (profit), SL at {stop_price} (loss)")
    else:  # SHORT
        # For SHORT: take_profit should be below stop_price
        if take_profit_price >= stop_price:
            logger.error(f"SHORT position: take_profit_price ({take_profit_price}) must be less than "
                        f"stop_price ({stop_price})")
            return None
        logger.info(f"SHORT position: TP at {take_profit_price} (profit), SL at {stop_price} (loss)")
    
    # Determine order side (opposite of position side)
    if position_side_upper == 'LONG':
        order_side = 'SELL'  # Close long position by selling
    else:
        order_side = 'BUY'   # Close short position by buying
    
    logger.info(f"Placing OCO orders for {position_side_upper} position: {position_quantity} {symbol}")
    logger.info(f"  Closing orders will be {order_side}")
    logger.info(f"  Take Profit: {take_profit_price}")
    logger.info(f"  Stop Loss: {stop_price}")
    
    # Place TAKE_PROFIT_MARKET order
    take_profit_params = {
        'symbol': symbol.upper(),
        'side': order_side,
        'type': 'TAKE_PROFIT_MARKET',
        'stopPrice': take_profit_price,
        'closePosition': True,  # Automatically close the entire position
        'workingType': 'CONTRACT_PRICE',
        'recvWindow': client.recv_window  # Use client's recvWindow for timestamp tolerance
    }
    
    # Place STOP_MARKET order
    stop_loss_params = {
        'symbol': symbol.upper(),
        'side': order_side,
        'type': 'STOP_MARKET',
        'stopPrice': stop_price,
        'closePosition': True,  # Automatically close the entire position
        'workingType': 'CONTRACT_PRICE',
        'recvWindow': client.recv_window  # Use client's recvWindow for timestamp tolerance
    }
    
    logger.debug(f"Take-profit parameters: {take_profit_params}")
    logger.debug(f"Stop-loss parameters: {stop_loss_params}")
    
    try:
        # Place Take-Profit order
        logger.info(f"Placing TAKE_PROFIT_MARKET order at {take_profit_price}")
        take_profit_response = client.client.futures_create_order(**take_profit_params)
        
        logger.info(f"✓ Take-profit order placed successfully!")
        logger.info(f"  Order ID: {take_profit_response.get('orderId')}")
        logger.info(f"  Stop Price: {take_profit_response.get('stopPrice')}")
        logger.debug(f"Full take-profit response: {take_profit_response}")
        
        # Place Stop-Loss order
        logger.info(f"Placing STOP_MARKET order at {stop_price}")
        stop_loss_response = client.client.futures_create_order(**stop_loss_params)
        
        logger.info(f"✓ Stop-loss order placed successfully!")
        logger.info(f"  Order ID: {stop_loss_response.get('orderId')}")
        logger.info(f"  Stop Price: {stop_loss_response.get('stopPrice')}")
        logger.debug(f"Full stop-loss response: {stop_loss_response}")
        
        # Return both responses
        result = {
            'take_profit': take_profit_response,
            'stop_loss': stop_loss_response
        }
        
        logger.info(f"✓ OCO orders placed successfully for {position_side_upper} position")
        return result
        
    except BinanceAPIException as e:
        logger.error(f"Binance API Error (Code: {e.code}): {e.message}")
        
        # If take-profit succeeded but stop-loss failed, log warning
        if 'take_profit_response' in locals():
            logger.warning(f"Take-profit order was placed (ID: {take_profit_response.get('orderId')}), "
                          f"but stop-loss order failed. You may need to manually place stop-loss.")
        
        return None
        
    except Exception as e:
        logger.error(f"Unexpected error while placing OCO orders: {type(e).__name__}: {e}")
        
        # If take-profit succeeded but stop-loss failed, log warning
        if 'take_profit_response' in locals():
            logger.warning(f"Take-profit order was placed (ID: {take_profit_response.get('orderId')}), "
                          f"but stop-loss order failed. You may need to manually place stop-loss.")
        
        return None


def calculate_oco_prices(current_price: float, position_side: str, 
                        take_profit_percent: float = 2.0, stop_loss_percent: float = 1.0):
    """
    Calculate take-profit and stop-loss prices based on percentages.
    
    Args:
        current_price (float): Current market price
        position_side (str): Position side ('LONG' or 'SHORT')
        take_profit_percent (float): Take profit percentage (default 2%)
        stop_loss_percent (float): Stop loss percentage (default 1%)
        
    Returns:
        tuple: (take_profit_price, stop_price)
    
    Example:
        # For LONG at $25,000 with 2% TP and 1% SL
        tp, sl = calculate_oco_prices(25000, 'LONG', 2.0, 1.0)
        # Returns: (25500.0, 24750.0)
    """
    position_side_upper = position_side.upper()
    
    if position_side_upper == 'LONG':
        # LONG: TP above, SL below
        take_profit_price = current_price * (1 + take_profit_percent / 100)
        stop_price = current_price * (1 - stop_loss_percent / 100)
    else:  # SHORT
        # SHORT: TP below, SL above
        take_profit_price = current_price * (1 - take_profit_percent / 100)
        stop_price = current_price * (1 + stop_loss_percent / 100)
    
    logger.info(f"Calculated OCO prices for {position_side_upper} at {current_price}:")
    logger.info(f"  Take Profit: {take_profit_price:.2f} ({take_profit_percent}%)")
    logger.info(f"  Stop Loss: {stop_price:.2f} ({stop_loss_percent}%)")
    
    return take_profit_price, stop_price
