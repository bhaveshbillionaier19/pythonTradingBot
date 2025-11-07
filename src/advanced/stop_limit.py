# src/advanced/stop_limit.py
"""
Stop-Limit order implementation for Binance Futures trading.
Handles validation and execution of stop-limit orders.

A Stop-Limit order is triggered when the stop price is reached,
then executes as a limit order at the specified limit price.
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


def place_stop_limit_order(client: BinanceFuturesClient, symbol: str, side: str, quantity: float, price: float, stop_price: float):
    """
    Place a stop-limit order on Binance Futures.
    
    A stop-limit order combines a stop order with a limit order:
    1. When the stop price is reached, the order is triggered
    2. The order then executes as a limit order at the specified price
    
    Args:
        client (BinanceFuturesClient): Initialized Binance Futures client
        symbol (str): Trading pair symbol (e.g., 'BTCUSDT')
        side (str): Order side ('BUY' or 'SELL')
        quantity (float): Order quantity
        price (float): Limit price for execution after trigger
        stop_price (float): Trigger price that activates the order
        
    Returns:
        dict: Order response from Binance API on success, None on failure
        
    Order Logic:
        - BUY Stop-Limit: Triggers when market price >= stop_price, executes at limit price
          Use case: Enter long position when price breaks above resistance
          
        - SELL Stop-Limit: Triggers when market price <= stop_price, executes at limit price
          Use case: Exit position or enter short when price breaks below support
    
    Example Response:
        {
            'orderId': 123456789,
            'symbol': 'BTCUSDT',
            'status': 'NEW',
            'clientOrderId': 'xxx',
            'price': '26000.00',
            'avgPrice': '0.00',
            'origQty': '0.001',
            'executedQty': '0.000',
            'cumQty': '0.000',
            'cumQuote': '0.00000',
            'timeInForce': 'GTC',
            'type': 'STOP',
            'reduceOnly': False,
            'closePosition': False,
            'side': 'BUY',
            'positionSide': 'BOTH',
            'stopPrice': '25500.00',
            'workingType': 'CONTRACT_PRICE',
            'priceProtect': False,
            'origType': 'STOP',
            'updateTime': 1699999999999
        }
    """
    # Validate inputs
    logger.debug(f"Validating stop-limit order parameters: symbol={symbol}, side={side}, "
                 f"quantity={quantity}, price={price}, stop_price={stop_price}")
    
    if not validate_symbol(symbol):
        logger.error(f"Invalid symbol: {symbol}. Symbol must be uppercase, at least 6 characters, "
                     "and end with USDT/BUSD/USD/BTC/ETH")
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
    
    if not validate_price(stop_price):
        logger.error(f"Invalid stop_price: {stop_price}. Stop price must be a positive number greater than 0")
        return None
    
    # Validate price logic based on side
    side_upper = side.upper()
    if side_upper == 'BUY':
        # For BUY stop-limit: stop_price should typically be above current market
        # and price should be at or above stop_price (or slightly below for slippage)
        if price > stop_price * 1.1:  # Allow some flexibility
            logger.warning(f"BUY stop-limit: limit price ({price}) is significantly higher than stop price ({stop_price}). "
                          "This may result in unexpected execution.")
    elif side_upper == 'SELL':
        # For SELL stop-limit: stop_price should typically be below current market
        # and price should be at or below stop_price (or slightly above for slippage)
        if price < stop_price * 0.9:  # Allow some flexibility
            logger.warning(f"SELL stop-limit: limit price ({price}) is significantly lower than stop price ({stop_price}). "
                          "This may result in unexpected execution.")
    
    logger.info(f"All validations passed for stop-limit order: {side} {quantity} {symbol} "
                f"@ stop:{stop_price}, limit:{price}")
    
    # Construct order parameters
    # Using 'STOP' type for stop-limit orders
    # STOP: A stop-limit order that will be placed as a limit order when the stop price is triggered
    order_params = {
        'symbol': symbol.upper(),
        'side': side.upper(),
        'type': 'STOP',  # Stop-limit order type
        'quantity': quantity,
        'price': price,  # Limit price after trigger
        'stopPrice': stop_price,  # Trigger price
        'timeInForce': 'GTC',  # Good-Till-Canceled
        'workingType': 'CONTRACT_PRICE',  # Use contract price for trigger
        'recvWindow': client.recv_window  # Use client's recvWindow for timestamp tolerance
    }
    
    logger.debug(f"Stop-limit order parameters: {order_params}")
    
    # Place the order
    try:
        logger.info(f"Placing STOP-LIMIT order: {side} {quantity} {symbol} "
                   f"@ stop:{stop_price}, limit:{price}")
        
        # Call Binance API to create the order
        response = client.client.futures_create_order(**order_params)
        
        # Log successful order
        logger.info(f"✓ Stop-limit order placed successfully!")
        logger.info(f"  Order ID: {response.get('orderId')}")
        logger.info(f"  Symbol: {response.get('symbol')}")
        logger.info(f"  Side: {response.get('side')}")
        logger.info(f"  Type: {response.get('type')}")
        logger.info(f"  Status: {response.get('status')}")
        logger.info(f"  Quantity: {response.get('origQty')}")
        logger.info(f"  Stop Price: {response.get('stopPrice')}")
        logger.info(f"  Limit Price: {response.get('price')}")
        logger.info(f"  Time In Force: {response.get('timeInForce')}")
        logger.debug(f"Full order response: {response}")
        
        return response
        
    except BinanceAPIException as e:
        logger.error(f"Binance API Error (Code: {e.code}): {e.message}")
        return None
        
    except Exception as e:
        logger.error(f"Unexpected error while placing stop-limit order: {type(e).__name__}: {e}")
        return None


def place_stop_market_order(client: BinanceFuturesClient, symbol: str, side: str, quantity: float, stop_price: float):
    """
    Place a stop-market order on Binance Futures.
    
    A stop-market order triggers a market order when the stop price is reached.
    This executes immediately at the best available price once triggered.
    
    Args:
        client (BinanceFuturesClient): Initialized Binance Futures client
        symbol (str): Trading pair symbol
        side (str): Order side ('BUY' or 'SELL')
        quantity (float): Order quantity
        stop_price (float): Trigger price
        
    Returns:
        dict: Order response on success, None on failure
    """
    # Validate inputs
    logger.debug(f"Validating stop-market order parameters: symbol={symbol}, side={side}, "
                 f"quantity={quantity}, stop_price={stop_price}")
    
    if not validate_symbol(symbol):
        logger.error(f"Invalid symbol: {symbol}")
        return None
    
    if not validate_side(side):
        logger.error(f"Invalid side: {side}")
        return None
    
    if not validate_quantity(quantity):
        logger.error(f"Invalid quantity: {quantity}")
        return None
    
    if not validate_price(stop_price):
        logger.error(f"Invalid stop_price: {stop_price}")
        return None
    
    logger.info(f"All validations passed for stop-market order: {side} {quantity} {symbol} @ stop:{stop_price}")
    
    # Construct order parameters
    order_params = {
        'symbol': symbol.upper(),
        'side': side.upper(),
        'type': 'STOP_MARKET',  # Stop-market order type
        'quantity': quantity,
        'stopPrice': stop_price,
        'workingType': 'CONTRACT_PRICE'
    }
    
    logger.debug(f"Stop-market order parameters: {order_params}")
    
    try:
        logger.info(f"Placing STOP-MARKET order: {side} {quantity} {symbol} @ stop:{stop_price}")
        
        response = client.client.futures_create_order(**order_params)
        
        logger.info(f"✓ Stop-market order placed successfully!")
        logger.info(f"  Order ID: {response.get('orderId')}")
        logger.info(f"  Stop Price: {response.get('stopPrice')}")
        logger.debug(f"Full order response: {response}")
        
        return response
        
    except BinanceAPIException as e:
        logger.error(f"Binance API Error while placing stop-market order: {e}")
        return None
        
    except Exception as e:
        logger.error(f"Unexpected error while placing stop-market order: {e}")
        return None
