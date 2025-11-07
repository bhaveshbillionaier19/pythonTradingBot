# src/validators.py
"""
Input validation utilities for trading bot operations.
Provides validation functions for common trading parameters.
"""


def validate_symbol(symbol: str) -> bool:
    """
    Validate a trading symbol format.
    
    Args:
        symbol (str): Trading pair symbol (e.g., 'BTCUSDT', 'ETHUSDT')
        
    Returns:
        bool: True if symbol is valid, False otherwise
        
    Validation Rules:
        - Must be a non-empty string
        - Must be at least 6 characters long
        - Must be uppercase
        - Should end with common quote currencies (USDT, BUSD, USD)
    """
    if not isinstance(symbol, str):
        return False
    
    if not symbol or len(symbol) < 6:
        return False
    
    if not symbol.isupper():
        return False
    
    # Check if it ends with common quote currencies
    valid_quotes = ['USDT', 'BUSD', 'USD', 'BTC', 'ETH']
    if not any(symbol.endswith(quote) for quote in valid_quotes):
        return False
    
    return True


def validate_quantity(quantity: float) -> bool:
    """
    Validate a trade quantity.
    
    Args:
        quantity (float): Order quantity
        
    Returns:
        bool: True if quantity is valid, False otherwise
        
    Validation Rules:
        - Must be a positive number
        - Must be greater than 0
    """
    try:
        quantity_float = float(quantity)
        return quantity_float > 0
    except (ValueError, TypeError):
        return False


def validate_price(price: float) -> bool:
    """
    Validate a price value.
    
    Args:
        price (float): Order price
        
    Returns:
        bool: True if price is valid, False otherwise
        
    Validation Rules:
        - Must be a positive number
        - Must be greater than 0
    """
    try:
        price_float = float(price)
        return price_float > 0
    except (ValueError, TypeError):
        return False


def validate_side(side: str) -> bool:
    """
    Validate an order side.
    
    Args:
        side (str): Order side ('BUY' or 'SELL')
        
    Returns:
        bool: True if side is valid, False otherwise
        
    Validation Rules:
        - Must be either 'BUY' or 'SELL' (case-insensitive)
    """
    if not isinstance(side, str):
        return False
    
    return side.upper() in ['BUY', 'SELL']


def validate_order_type(order_type: str) -> bool:
    """
    Validate an order type.
    
    Args:
        order_type (str): Order type (e.g., 'MARKET', 'LIMIT', 'STOP')
        
    Returns:
        bool: True if order type is valid, False otherwise
    """
    if not isinstance(order_type, str):
        return False
    
    valid_types = ['MARKET', 'LIMIT', 'STOP', 'STOP_MARKET', 'TAKE_PROFIT', 'TAKE_PROFIT_MARKET']
    return order_type.upper() in valid_types


def validate_leverage(leverage: int) -> bool:
    """
    Validate leverage value for futures trading.
    
    Args:
        leverage (int): Leverage multiplier
        
    Returns:
        bool: True if leverage is valid, False otherwise
        
    Validation Rules:
        - Must be between 1 and 125 (Binance Futures max)
    """
    try:
        leverage_int = int(leverage)
        return 1 <= leverage_int <= 125
    except (ValueError, TypeError):
        return False
