# src/binance_client.py
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from binance.client import Client
from binance.exceptions import BinanceAPIException
from src.config import API_KEY, API_SECRET, TESTNET_BASE_URL
from src.logger import setup_logging


class BinanceFuturesClient:
    """
    A client for interacting with Binance Futures API.
    Supports both testnet and production environments.
    """
    
    def __init__(self, api_key, api_secret, testnet=True):
        """
        Initialize the Binance Futures client.
        
        Args:
            api_key (str): Binance API key
            api_secret (str): Binance API secret
            testnet (bool): If True, use testnet; otherwise use production
        """
        # Initialize logger
        self.logger = setup_logging(__name__)
        
        # recvWindow: Time window in milliseconds that the request is valid for
        # Default is 5000ms (5 seconds). We increase to 60000ms (60 seconds) to handle
        # minor clock synchronization issues between client and server.
        # Note: Users should still sync their system clock for best results.
        recv_window = 60000
        
        if testnet:
            self.client = Client(api_key, api_secret, testnet=True)
            self.client.API_URL = TESTNET_BASE_URL
            self.logger.info("Binance Futures client initialized in TESTNET mode")
        else:
            self.client = Client(api_key, api_secret)
            self.logger.info("Binance Futures client initialized in PRODUCTION mode")
        
        # Set recvWindow for all requests to handle clock sync issues
        self.recv_window = recv_window
        self.logger.debug(f"recvWindow set to {recv_window}ms for timestamp tolerance")
        
        self.testnet = testnet
    
    def get_account_info(self):
        """
        Retrieve account information from Binance Futures.
        
        Returns:
            dict: Account information including balances and positions
        
        Raises:
            BinanceAPIException: If the API request fails
        """
        try:
            self.logger.debug("Requesting account information from Binance Futures API")
            account_info = self.client.futures_account(recvWindow=self.recv_window)
            self.logger.info("Successfully retrieved account information")
            self.logger.debug(f"Account balance: {account_info.get('totalWalletBalance', 'N/A')} USDT")
            return account_info
        except BinanceAPIException as e:
            self.logger.error(f"Binance API Error (Code: {e.code}): {e.message}")
            raise
    
    def get_open_orders(self, symbol: str = None):
        """
        Retrieve all open orders for a symbol or all symbols.
        
        Args:
            symbol (str, optional): Trading pair symbol. If None, returns all open orders.
        
        Returns:
            list: List of open orders
        
        Raises:
            BinanceAPIException: If the API request fails
        """
        try:
            if symbol:
                self.logger.debug(f"Requesting open orders for symbol: {symbol}")
                open_orders = self.client.futures_get_open_orders(
                    symbol=symbol.upper(),
                    recvWindow=self.recv_window
                )
                self.logger.info(f"Retrieved {len(open_orders)} open order(s) for {symbol}")
            else:
                self.logger.debug("Requesting all open orders")
                open_orders = self.client.futures_get_open_orders(recvWindow=self.recv_window)
                self.logger.info(f"Retrieved {len(open_orders)} total open order(s)")
            
            self.logger.debug(f"Open orders: {open_orders}")
            return open_orders
            
        except BinanceAPIException as e:
            self.logger.error(f"Binance API Error (Code: {e.code}): {e.message}")
            raise
    
    def cancel_order(self, symbol: str, order_id: int):
        """
        Cancel an existing order.
        
        Args:
            symbol (str): Trading pair symbol
            order_id (int): Order ID to cancel
        
        Returns:
            dict: Cancellation response from Binance API
        
        Raises:
            BinanceAPIException: If the API request fails
        """
        try:
            self.logger.debug(f"Requesting order cancellation: symbol={symbol}, orderId={order_id}")
            cancel_response = self.client.futures_cancel_order(
                symbol=symbol.upper(),
                orderId=order_id,
                recvWindow=self.recv_window
            )
            self.logger.info(f"Successfully canceled order {order_id} for {symbol}")
            self.logger.debug(f"Cancellation response: {cancel_response}")
            return cancel_response
            
        except BinanceAPIException as e:
            self.logger.error(f"Binance API Error (Code: {e.code}): {e.message}")
            raise
