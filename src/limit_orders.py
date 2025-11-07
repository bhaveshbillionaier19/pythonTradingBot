# src/limit_orders.py
"""
Limit order implementation for Binance Futures trading.
Handles validation and execution of limit orders.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from binance.exceptions import BinanceAPIException
from src.binance_client import BinanceFuturesClient
from src.validators import validate_symbol, validate_side, validate_quantity, validate_price
from src.logger import setup_logging


# Initialize logger for this module
logger = setup_logging(__name__)


def place_limit_order(client: BinanceFuturesClient, symbol: str, side: str, quantity: float, price: float):
    """
    Place a limit order on Binance Futures.
    
    Args:
        client (BinanceFuturesClient): Initialized Binance Futures client
        symbol (str): Trading pair symbol (e.g., 'BTCUSDT')
        side (str): Order side ('BUY' or 'SELL')
        quantity (float): Order quantity
        price (float): Limit price for the order
        
    Returns:
        dict: Order response from Binance API on success, None on failure
        
    Example Response:
        {
            'orderId': 123456789,
            'symbol': 'BTCUSDT',
            'status': 'NEW',
            'clientOrderId': 'xxx',
            'price': '25000.00',
            'avgPrice': '0.00',
            'origQty': '0.001',
            'executedQty': '0.000',
            'cumQty': '0.000',
            'cumQuote': '0.00000',
            'timeInForce': 'GTC',
            'type': 'LIMIT',
            'reduceOnly': False,
            'closePosition': False,
            'side': 'BUY',
            'positionSide': 'BOTH',
            'stopPrice': '0',
            'workingType': 'CONTRACT_PRICE',
            'priceProtect': False,
            'origType': 'LIMIT',
            'updateTime': 1699999999999
        }
    """
    # Validate inputs
    logger.debug(f"Validating order parameters: symbol={symbol}, side={side}, quantity={quantity}, price={price}")
    
    if not validate_symbol(symbol):
        logger.error(f"Invalid symbol: {symbol}. Symbol must be uppercase, at least 6 characters, and end with USDT/BUSD/USD/BTC/ETH")
        return None
    
    if not validate_side(side):
        logger.error(f"Invalid side: {side}. Side must be 'BUY' or 'SELL'")
        return None
    
    if not validate_quantity(quantity):
        logger.error(f"Invalid quantity: {quantity}. Quantity must be a positive number greater than 0")
        return None
    
    if not validate_price(price):
        logger.error(f"Invalid price: {price}. Price must be a positive number greater than 0")
        return None
    
    logger.info(f"All validations passed for order: {side} {quantity} {symbol} @ {price}")
    
    # Construct order parameters
    order_params = {
        'symbol': symbol.upper(),
        'side': side.upper(),
        'type': 'LIMIT',
        'quantity': quantity,
        'price': price,
        'timeInForce': 'GTC',  # Good-Till-Canceled
        'recvWindow': client.recv_window  # Use client's recvWindow for timestamp tolerance
    }
    
    logger.debug(f"Order parameters: {order_params}")
    
    # Place the order
    try:
        logger.info(f"Placing LIMIT order: {side} {quantity} {symbol} @ {price}")
        
        # Call Binance API to create the order
        response = client.client.futures_create_order(**order_params)
        
        # Log successful order
        logger.info(f"✓ Limit order placed successfully!")
        logger.info(f"  Order ID: {response.get('orderId')}")
        logger.info(f"  Symbol: {response.get('symbol')}")
        logger.info(f"  Side: {response.get('side')}")
        logger.info(f"  Type: {response.get('type')}")
        logger.info(f"  Status: {response.get('status')}")
        logger.info(f"  Quantity: {response.get('origQty')}")
        logger.info(f"  Price: {response.get('price')}")
        logger.info(f"  Time In Force: {response.get('timeInForce')}")
        logger.debug(f"Full order response: {response}")
        
        return response
        
    except BinanceAPIException as e:
        logger.error(f"Binance API Error (Code: {e.code}): {e.message}")
        return None
        
    except Exception as e:
        logger.error(f"Unexpected error while placing limit order: {type(e).__name__}: {e}")
        return None


def modify_limit_order(client: BinanceFuturesClient, symbol: str, order_id: int, quantity: float = None, price: float = None):
    """
    Modify an existing limit order by canceling and replacing it.
    
    Args:
        client (BinanceFuturesClient): Initialized Binance Futures client
        symbol (str): Trading pair symbol
        order_id (int): Order ID to modify
        quantity (float): New quantity (optional)
        price (float): New price (optional)
        
    Returns:
        dict: New order response on success, None on failure
        
    Note:
        Binance doesn't support direct order modification. This function cancels
        the existing order and places a new one with updated parameters.
    """
    try:
        logger.info(f"Modifying limit order: orderId={order_id}, symbol={symbol}")
        
        # First, get the current order details
        current_order = client.client.futures_get_order(
            symbol=symbol.upper(),
            orderId=order_id
        )
        
        if current_order.get('status') not in ['NEW', 'PARTIALLY_FILLED']:
            logger.error(f"Cannot modify order {order_id}: status is {current_order.get('status')}")
            return None
        
        # Cancel the existing order
        logger.debug(f"Canceling order {order_id}")
        cancel_response = client.client.futures_cancel_order(
            symbol=symbol.upper(),
            orderId=order_id
        )
        
        logger.info(f"Order {order_id} canceled successfully")
        
        # Place new order with updated parameters
        new_quantity = quantity if quantity is not None else float(current_order.get('origQty'))
        new_price = price if price is not None else float(current_order.get('price'))
        
        logger.info(f"Placing replacement order: quantity={new_quantity}, price={new_price}")
        
        new_order = place_limit_order(
            client=client,
            symbol=symbol,
            side=current_order.get('side'),
            quantity=new_quantity,
            price=new_price
        )
        
        if new_order:
            logger.info(f"Order modified successfully. New order ID: {new_order.get('orderId')}")
        
        return new_order
        
    except BinanceAPIException as e:
        logger.error(f"Failed to modify order: {e}")
        return None
        
    except Exception as e:
        logger.error(f"Unexpected error modifying order: {e}")
        return None


def get_open_limit_orders(client: BinanceFuturesClient, symbol: str = None):
    """
    Get all open limit orders for a symbol or all symbols.
    
    Args:
        client (BinanceFuturesClient): Initialized Binance Futures client
        symbol (str): Trading pair symbol (optional, if None returns all open orders)
        
    Returns:
        list: List of open orders, empty list on failure
    """
    try:
        logger.debug(f"Fetching open limit orders for symbol: {symbol if symbol else 'ALL'}")
        
        if symbol:
            orders = client.client.futures_get_open_orders(symbol=symbol.upper())
        else:
            orders = client.client.futures_get_open_orders()
        
        # Filter for limit orders only
        limit_orders = [order for order in orders if order.get('type') == 'LIMIT']
        
        logger.info(f"Found {len(limit_orders)} open limit orders")
        logger.debug(f"Open limit orders: {limit_orders}")
        
        return limit_orders
        
    except BinanceAPIException as e:
        logger.error(f"Failed to get open orders: {e}")
        return []
        
    except Exception as e:
        logger.error(f"Unexpected error getting open orders: {e}")
        return []
