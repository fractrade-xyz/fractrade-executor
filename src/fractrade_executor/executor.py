"""
Main executor class for handling trading actions
"""

import asyncio
import json
import logging
import os
import signal
import traceback
from abc import ABC, abstractmethod
from typing import Dict, Any

import websockets
from dotenv import load_dotenv
from fractrade_hl_simple import HyperliquidClient, HyperliquidAccount

# Configure logging
logging.basicConfig(
    level=os.getenv('LOGLEVEL', 'INFO'),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

class FractradeExecutor(ABC):
    """
    Abstract base class for executing trading actions.
    
    This class provides the core functionality for connecting to a WebSocket server
    and executing actions. Subclasses must implement the action handling methods.
    """

    def __init__(self):
        """Initialize the executor."""
        self.logger = logger
        self.running = False
        self.websocket = None
        self.hl_client = None
        self._shutdown_event = asyncio.Event()
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)
        
        # Initialize HyperLiquid client
        self._init_hyperliquid_client()

    def _handle_signal(self, sig, frame):
        """Handle signals for graceful shutdown."""
        self.logger.info(f"Received signal {sig}, shutting down...")
        self.running = False
        # Set the shutdown event in the event loop
        if self._shutdown_event:
            try:
                loop = asyncio.get_event_loop()
                loop.call_soon_threadsafe(self._shutdown_event.set)
            except Exception as e:
                self.logger.error(f"Error setting shutdown event: {str(e)}")

    def _init_hyperliquid_client(self):
        """Initialize the HyperLiquid client."""
        try:
            # Get private key and public address from environment variables
            private_key = os.environ.get("HYPERLIQUID_PRIVATE_KEY")
            public_address = os.environ.get("HYPERLIQUID_PUBLIC_ADDRESS")
            
            if private_key and public_address:
                # Initialize authenticated client
                account = HyperliquidAccount.from_key(
                    private_key, 
                    public_address=public_address
                )
                self.hl_client = HyperliquidClient(account=account)
                self.logger.info("Initialized authenticated HyperLiquid client")
            else:
                # Initialize unauthenticated client
                self.hl_client = HyperliquidClient()
                self.logger.warning("Initialized unauthenticated HyperLiquid client")
        except Exception as e:
            self.logger.error(f"Error initializing HyperLiquid client: {str(e)}")
            self.hl_client = HyperliquidClient()
            self.logger.warning("Falling back to unauthenticated HyperLiquid client")

    async def _connect(self):
        """Connect to the WebSocket server."""
        ws_url = os.environ.get("FRAC_WS_URL")
        user_token = os.environ.get("FRAC_USER_TOKEN")
        
        if not ws_url:
            raise ValueError("FRAC_WS_URL environment variable not set")
            
        if not user_token:
            raise ValueError("FRAC_USER_TOKEN environment variable not set")
            
        # Remove trailing slashes from base URL and append executor path
        ws_url = ws_url.rstrip('/')
        # The path should match the ASGI routing configuration
        full_url = f"{ws_url}/ws/executor/"
        
        # Set up headers with authentication token
        headers = {
            "Authorization": f"Token {user_token}"
        }
        
        self.logger.info(f"Connecting to WebSocket server at {full_url}")
        
        while self.running:
            try:
                async with websockets.connect(
                    full_url,
                    additional_headers=headers,
                    ping_interval=20,  # Keep connection alive
                    ping_timeout=20,   # Detect disconnects faster
                ) as websocket:
                    self.websocket = websocket
                    self.logger.info("Connected to WebSocket server")
                    
                    try:
                        while self.running:
                            message = await websocket.recv()
                            self.logger.debug(f"Received message: {message}")
                            
                            # Parse message
                            try:
                                data = json.loads(message)
                                await self.handle_action(data)
                            except json.JSONDecodeError:
                                self.logger.error(f"Invalid JSON message: {message}")
                            except Exception as e:
                                self.logger.error(f"Error handling message: {str(e)}")
                                self.logger.error(traceback.format_exc())
                    except websockets.exceptions.ConnectionClosed:
                        self.logger.warning("Connection closed, attempting to reconnect...")
                        await asyncio.sleep(5)  # Wait before reconnecting
                        continue
                    
            except Exception as e:
                if self.running:
                    self.logger.error(f"WebSocket connection error: {str(e)}")
                    self.logger.error(traceback.format_exc())
                    await asyncio.sleep(5)  # Wait before retrying
                else:
                    break
            
        self.websocket = None
        self.logger.info("Disconnected from WebSocket server")

    async def handle_action(self, data: Dict[str, Any]) -> None:
        """
        Handle an action message received from the WebSocket server.
        
        Args:
            data: The message to handle.
        """
        try:
            # Log the full received data for debugging
            self.logger.debug(f"Received data: {json.dumps(data, indent=2)}")
            
            # Only handle ACTION type messages
            message_type = data.get("type", "").upper()
            
            if message_type == "ACTION":
                action_data = data.get("data", {})
                action_id = action_data.get("action_id", "").lower()
                config = action_data.get("config", {})
                
                self.logger.info(f"Handling action: {action_id}")
                self.logger.debug(f"Action data: {json.dumps(action_data, indent=2)}")
                self.logger.debug(f"Config: {json.dumps(config, indent=2)}")
                
                if action_id == "execute_hyperliquid_perp_trade":
                    await self.handle_hyperliquid_perp_trade(config)
                elif action_id == "set_hyperliquid_perp_stop_loss":
                    await self.handle_set_hyperliquid_perp_stop_loss(config)
                elif action_id == "set_hyperliquid_perp_take_profit":
                    await self.handle_set_hyperliquid_perp_take_profit(config)
                else:
                    self.logger.warning(f"Unsupported action: {action_id}")
            else:
                self.logger.warning(f"Unsupported message type: {message_type}")
        except Exception as e:
            self.logger.error(f"Error handling action: {str(e)}")
            self.logger.error(traceback.format_exc())

    async def handle_hyperliquid_perp_trade(self, config: Dict[str, Any]) -> bool:
        """
        Execute a trade on HyperLiquid.
        
        Args:
            config: The configuration for the trade.
        """
        if not self.hl_client:
            self.logger.error("No HyperLiquid client available")
            return False
            
        try:
            # Log the full config for debugging
            self.logger.debug(f"Received trade config: {json.dumps(config, indent=2)}")
            
            position = config.get("position", {})
            metadata = config.get("metadata", {})
            
            # Log position and metadata for debugging
            self.logger.debug(f"Position data: {json.dumps(position, indent=2)}")
            self.logger.debug(f"Metadata: {json.dumps(metadata, indent=2)}")
            
            # Log raw symbol value before any processing
            self.logger.debug(f"Raw symbol value from position: {position.get('symbol')}")
            
            symbol = position.get("symbol")
            size = float(position.get("size", 0))
            side = position.get("side", "").upper()
            reduce_only = position.get("reduce_only", False)
            server_execution = metadata.get("server_execution", False)
            
            # Log processed values
            self.logger.debug(f"Processed values:\n"
                            f"Symbol: {symbol}\n"
                            f"Size: {size}\n"
                            f"Side: {side}\n"
                            f"Reduce only: {reduce_only}\n"
                            f"Server execution: {server_execution}")
            
            # Validate required fields with detailed error messages
            if not symbol:
                self.logger.error(f"Missing symbol in position data: {position}")
                return False
                
            if not size:
                self.logger.error(f"Missing or invalid size in position data: {position}")
                return False
                
            if not side:
                self.logger.error(f"Missing or invalid side in position data: {position}")
                return False
                
            # Log trade details
            self.logger.info(
                f"Received trade:\n"
                f"Symbol: {symbol}\n"
                f"Size: {size}\n"
                f"Side: {side}\n"
                f"Reduce only: {reduce_only}\n"
                f"Price: {metadata.get('price')}\n"
                f"Leverage: {metadata.get('leverage')}\n"
                f"Source: {metadata.get('source_wallet')}\n"
                f"Server execution: {server_execution}"
            )
            
            # Only execute if server is not executing
            if not server_execution and self.hl_client.is_authenticated():
                self.logger.info("Executing trade on client side since server execution is disabled")
                try:
                    # Log pre-execution values
                    self.logger.debug(f"Pre-execution values:\n"
                                    f"Symbol: {symbol}\n"
                                    f"Size: {size}\n"
                                    f"Side: {side}\n"
                                    f"Reduce only: {reduce_only}")
                    
                    # Execute trade
                    await self.hl_client.execute_perp_trade(
                        symbol=symbol,
                        size=size,
                        side=side,
                        reduce_only=reduce_only
                    )
                    self.logger.info(f"Trade executed: {side} {size} {symbol}")
                    return True
                except Exception as e:
                    self.logger.error(f"Error during trade execution: {str(e)}")
                    self.logger.error(traceback.format_exc())
                    return False
            else:
                self.logger.info(
                    f"Not executing trade: server_execution={server_execution}, "
                    f"has_client={bool(self.hl_client)}, "
                    f"is_authenticated={self.hl_client.is_authenticated() if self.hl_client else False}"
                )
                return False
            
        except Exception as e:
            self.logger.error(f"Error handling trade: {str(e)}")
            self.logger.error(traceback.format_exc())
            return False

    async def handle_set_hyperliquid_perp_stop_loss(self, config: Dict[str, Any]) -> bool:
        """
        Set a stop loss for a position on HyperLiquid.
        
        Args:
            config: The configuration for the stop loss.
        """
        if not self.hl_client:
            self.logger.error("No HyperLiquid client available")
            return False
            
        try:
            position = config.get("position", {})
            symbol = position.get("symbol")
            size = float(position.get("size", 0))
            trigger_price = float(position.get("trigger_price", 0))
            side = position.get("side", "").upper()
            
            if not symbol or not size or not trigger_price or not side:
                self.logger.error(f"Invalid stop loss data: {position}")
                return False
                
            # Set stop loss
            await self.hl_client.set_stop_loss(
                symbol=symbol,
                size=size,
                trigger_price=trigger_price,
                side=side
            )
            
            self.logger.info(f"Stop loss set: {symbol} @ {trigger_price}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error setting stop loss: {str(e)}")
            return False

    async def handle_set_hyperliquid_perp_take_profit(self, config: Dict[str, Any]) -> bool:
        """
        Set a take profit for a position on HyperLiquid.
        
        Args:
            config: The configuration for the take profit.
        """
        if not self.hl_client:
            self.logger.error("No HyperLiquid client available")
            return False
            
        try:
            position = config.get("position", {})
            symbol = position.get("symbol")
            size = float(position.get("size", 0))
            trigger_price = float(position.get("trigger_price", 0))
            side = position.get("side", "").upper()
            
            if not symbol or not size or not trigger_price or not side:
                self.logger.error(f"Invalid take profit data: {position}")
                return False
                
            # Set take profit
            await self.hl_client.set_take_profit(
                symbol=symbol,
                size=size,
                trigger_price=trigger_price,
                side=side
            )
            
            self.logger.info(f"Take profit set: {symbol} @ {trigger_price}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error setting take profit: {str(e)}")
            return False

    async def start(self):
        """Start the executor and connect to WebSocket."""
        self.logger.info("Starting executor")
        self.running = True
        self._shutdown_event.clear()
        
        # Start connection in background
        self._connect_task = asyncio.create_task(self._connect())

    async def stop(self):
        """Stop the executor and close connections."""
        self.logger.info("Stopping executor")
        self.running = False
        
        # Set shutdown event
        self._shutdown_event.set()
        
        # Cancel the connection task if running
        if hasattr(self, '_connect_task') and not self._connect_task.done():
            self._connect_task.cancel()
            try:
                await self._connect_task
            except asyncio.CancelledError:
                pass
        
        # Close WebSocket connection if open
        if self.websocket:
            await self.websocket.close()
            self.websocket = None
        
        # Close HyperLiquid client if exists
        if self.hl_client:
            await self.hl_client.close()
            self.hl_client = None
        
        self.logger.info("Executor stopped")

    def run(self):
        """Run the executor."""
        self.logger.info("Starting executor")
        self.running = True
        
        # Run event loop
        loop = asyncio.get_event_loop()
        
        try:
            # Start the executor
            loop.run_until_complete(self.start())
            
            # Wait for shutdown event
            loop.run_until_complete(self._shutdown_event.wait())
        except KeyboardInterrupt:
            self.logger.info("Keyboard interrupt received, shutting down...")
        except Exception as e:
            self.logger.error(f"Error in event loop: {str(e)}")
            self.logger.error(traceback.format_exc())
        finally:
            # Stop the executor
            loop.run_until_complete(self.stop())
            self.logger.info("Executor stopped") 