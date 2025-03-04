# FractradeExecutor

A Python client for executing trades on HyperLiquid through the Fractrade platform.

## Overview

The FractradeExecutor is a client that connects to the Fractrade WebSocket server and executes trades on HyperLiquid. It supports:

- Real-time trade execution
- Server-side and client-side execution modes
- Automatic reconnection handling
- Graceful shutdown

## Installation

```bash
pip install fractrade-executor
```

## Quick Start

1. Create a `.env` file with your credentials:

```env
# Fractrade WebSocket connection
FRAC_WS_URL=https://your-fractrade-server.com
FRAC_USER_TOKEN=your-user-token

# HyperLiquid credentials (optional, for client-side execution)
HYPERLIQUID_PRIVATE_KEY=your-private-key
HYPERLIQUID_PUBLIC_ADDRESS=your-public-address
```

2. Create a simple executor:

```python
from fractrade_executor.executor import FractradeExecutor
import asyncio
import os
from dotenv import load_dotenv

class SimpleExecutor(FractradeExecutor):
    def __init__(self):
        super().__init__()
        
    async def handle_hyperliquid_perp_trade(self, config):
        return await super().handle_hyperliquid_perp_trade(config)

async def main():
    # Load environment variables
    load_dotenv()
    
    # Create and start executor
    executor = SimpleExecutor()
    await executor.start()
    
    # Wait for shutdown
    await executor._shutdown_event.wait()
    
    # Stop executor
    await executor.stop()

if __name__ == "__main__":
    asyncio.run(main())
```

## Configuration

### Environment Variables

- `FRAC_WS_URL`: The WebSocket URL of your Fractrade server
- `FRAC_USER_TOKEN`: Your Fractrade user token for authentication
- `HYPERLIQUID_PRIVATE_KEY`: Your HyperLiquid private key (optional)
- `HYPERLIQUID_PUBLIC_ADDRESS`: Your HyperLiquid public address (optional)

### Execution Modes

The executor supports two execution modes:

1. **Server-side Execution** (Default)
   - Trades are executed by the Fractrade server
   - No HyperLiquid credentials required
   - Set `server_execution=True` in trade metadata

2. **Client-side Execution**
   - Trades are executed directly on HyperLiquid
   - Requires HyperLiquid credentials
   - Set `server_execution=False` in trade metadata

## Action Types

The executor handles the following action types:

- `EXECUTE_HYPERLIQUID_PERP_TRADE`: Execute a perpetual futures trade
- `SET_HYPERLIQUID_PERP_STOP_LOSS`: Set a stop loss order
- `SET_HYPERLIQUID_PERP_TAKE_PROFIT`: Set a take profit order

## Trade Configuration

Trades are configured using a JSON structure:

```json
{
    "position": {
        "symbol": "BTC",
        "size": "0.0001",
        "side": "BUY",
        "reduce_only": false
    },
    "metadata": {
        "event_id": "uuid",
        "agent_id": "uuid",
        "strategy_id": "strategy_name",
        "timestamp": 1234567890,
        "price": 50000.0,
        "leverage": 50.0,
        "server_execution": true
    }
}
```

## Logging

The executor uses Python's built-in logging module. Configure logging level using:

```python
import logging
logging.basicConfig(
    level=logging.INFO,  # or logging.DEBUG for more details
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

## Error Handling

The executor includes automatic reconnection handling and graceful shutdown. It will:

- Automatically reconnect if the WebSocket connection is lost
- Handle SIGINT and SIGTERM signals for graceful shutdown
- Log all errors and important events

## Development

To run the example executor:

```bash
python examples/simple_executor.py
```

## License

MIT License
