# src/market_orders.py
"""
Market order implementation for Binance Futures trading.
Handles validation and execution of market orders.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from binance.exceptions import BinanceAPIException
from src.binance_client import BinanceFuturesClient
from src.validators import validate_symbol, validate_side, validate_quantity
from src.logger import setup_logging


# Initialize logger for this module
logger = setup_logging(__name__)


def place_market_order(client: BinanceFuturesClient, symbol: str, side: str, quantity: float):
    """
    Place a market order on Binance Futures.
    
    Args:
        client (BinanceFuturesClient): Initialized Binance Futures client
        symbol (str): Trading pair symbol (e.g., 'BTCUSDT')
        side (str): Order side ('BUY' or 'SELL')
        quantity (float): Order quantity
        
    Returns:
        dict: Order response from Binance API on success, None on failure
        
    Example Response:
        {
            'orderId': 123456789,
            'symbol': 'BTCUSDT',
            'status': 'FILLED',
            'clientOrderId': 'xxx',
            'price': '0',
            'avgPrice': '50000.00',
            'origQty': '0.001',
            'executedQty': '0.001',
            'cumQty': '0.001',
            'cumQuote': '50.00000',
            'timeInForce': 'GTC',
            'type': 'MARKET',
            'reduceOnly': False,
            'closePosition': False,
            'side': 'BUY',
            'positionSide': 'BOTH',
            'stopPrice': '0',
            'workingType': 'CONTRACT_PRICE',
            'priceProtect': False,
            'origType': 'MARKET',
            'updateTime': 1699999999999
        }
    """
    # Validate inputs
    logger.debug(f"Validating order parameters: symbol={symbol}, side={side}, quantity={quantity}")
    
    if not validate_symbol(symbol):
        logger.error(f"Invalid symbol: {symbol}. Symbol must be uppercase, at least 6 characters, and end with USDT/BUSD/USD/BTC/ETH")
        return None
    
    if not validate_side(side):
        logger.error(f"Invalid side: {side}. Side must be 'BUY' or 'SELL'")
        return None
    
    if not validate_quantity(quantity):
        logger.error(f"Invalid quantity: {quantity}. Quantity must be a positive number greater than 0")
        return None
    
    logger.info(f"All validations passed for order: {side} {quantity} {symbol}")
    
    # Construct order parameters
    order_params = {
        'symbol': symbol.upper(),
        'side': side.upper(),
        'type': 'MARKET',
        'quantity': quantity,
        'recvWindow': client.recv_window  # Use client's recvWindow for timestamp tolerance
    }
    
    logger.debug(f"Order parameters: {order_params}")
    
    # Place the order
    try:
        logger.info(f"Placing MARKET order: {side} {quantity} {symbol}")
        
        # Call Binance API to create the order
        response = client.client.futures_create_order(**order_params)
        
        # Log successful order
        logger.info(f"✓ Order placed successfully!")
        logger.info(f"  Order ID: {response.get('orderId')}")
        logger.info(f"  Symbol: {response.get('symbol')}")
        logger.info(f"  Side: {response.get('side')}")
        logger.info(f"  Status: {response.get('status')}")
        logger.info(f"  Executed Qty: {response.get('executedQty')}")
        logger.info(f"  Avg Price: {response.get('avgPrice')}")
        logger.debug(f"Full order response: {response}")
        
        return response
        
    except BinanceAPIException as e:
        logger.error(f"Binance API Error (Code: {e.code}): {e.message}")
        return None
        
    except Exception as e:
        logger.error(f"Unexpected error while placing order: {type(e).__name__}: {e}")
        return None


def get_order_status(client: BinanceFuturesClient, symbol: str, order_id: int):
    """
    Query the status of an existing order.
    
    Args:
        client (BinanceFuturesClient): Initialized Binance Futures client
        symbol (str): Trading pair symbol
        order_id (int): Order ID to query
        
    Returns:
        dict: Order status information, None on failure
    """
    try:
        logger.debug(f"Querying order status: symbol={symbol}, orderId={order_id}")
        
        response = client.client.futures_get_order(
            symbol=symbol.upper(),
            orderId=order_id
        )
        
        logger.info(f"Order status retrieved: {response.get('status')}")
        logger.debug(f"Full order status: {response}")
        
        return response
        
    except BinanceAPIException as e:
        logger.error(f"Failed to get order status: {e}")
        return None
        
    except Exception as e:
        logger.error(f"Unexpected error getting order status: {e}")
        return None


def cancel_order(client: BinanceFuturesClient, symbol: str, order_id: int):
    """
    Cancel an existing order.
    
    Args:
        client (BinanceFuturesClient): Initialized Binance Futures client
        symbol (str): Trading pair symbol
        order_id (int): Order ID to cancel
        
    Returns:
        dict: Cancellation response, None on failure
    """
    try:
        logger.info(f"Canceling order: symbol={symbol}, orderId={order_id}")
        
        response = client.client.futures_cancel_order(
            symbol=symbol.upper(),
            orderId=order_id
        )
        
        logger.info(f"✓ Order canceled successfully: {order_id}")
        logger.debug(f"Cancellation response: {response}")
        
        return response
        
    except BinanceAPIException as e:
        logger.error(f"Failed to cancel order: {e}")
        return None
        
    except Exception as e:
        logger.error(f"Unexpected error canceling order: {e}")
        return None
