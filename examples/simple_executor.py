#!/usr/bin/env python3
"""
Example implementation of FractradeExecutor showing basic usage.
This is a minimal example that demonstrates how to:
1. Connect to the Fractrade WebSocket server
2. Handle incoming trade actions
3. Execute trades on HyperLiquid
"""

import asyncio
import os
import logging
import signal
from dotenv import load_dotenv
from fractrade_executor.executor import FractradeExecutor

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Set to INFO for production use
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SimpleExecutor(FractradeExecutor):
    """
    Simple example executor that demonstrates basic usage of the FractradeExecutor.
    This executor will:
    1. Connect to the Fractrade WebSocket server
    2. Handle incoming trade actions
    3. Execute trades on HyperLiquid if server_execution is False
    """
    
    def __init__(self):
        super().__init__()
        logger.info("SimpleExecutor initialized")

    async def handle_hyperliquid_perp_trade(self, config):
        """Handle incoming trade actions"""
        logger.info("Received trade request: %s", config)
        # TODO: Implement custom trade execution logic here
        return await super().handle_hyperliquid_perp_trade(config)

async def main():
    """Run the simple executor"""
    # Load environment variables
    load_dotenv()
    
    # Create and start the executor
    executor = SimpleExecutor()
    
    try:
        logger.info("Starting executor...")
        await executor.start()
        logger.info("Executor started successfully")
        print("SimpleExecutor running. Press Ctrl+C to stop.")
        
        # Wait for shutdown event
        await executor._shutdown_event.wait()
        
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error("Unexpected error: %s", str(e), exc_info=True)
    finally:
        logger.info("Stopping executor...")
        await executor.stop()
        logger.info("Executor stopped")

if __name__ == "__main__":
    try:
        # Set up event loop with signal handlers
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        signals = (signal.SIGTERM, signal.SIGINT)
        for s in signals:
            loop.add_signal_handler(
                s, lambda s=s: asyncio.create_task(loop.stop())
            )
            
        # Run the main function
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("\nShutdown complete.")
    finally:
        loop.close() 