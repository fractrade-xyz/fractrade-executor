# Usage

This guide explains how to use the Fractrade Executor to execute trading signals and actions.

## Basic Usage

The Fractrade Executor is designed to be run as a standalone service that connects to a WebSocket server to receive trading signals and action messages. It then executes these signals and actions on the specified exchange.

### Running the Executor

Since `FractradeExecutor` is an abstract base class, you must use a concrete implementation like the provided `SimpleExecutor` or create your own custom executor.

You can run the SimpleExecutor using the command-line interface:

```bash
fractrade-executor
```

By default, this will start the SimpleExecutor, which includes concrete implementations for handling trades, stop losses, and take profits. If you've created your own custom executor, you'll need to run it directly from your code.

You can also set the logging level:

```bash
fractrade-executor --log-level DEBUG
```

### Environment Variables

The executor requires the following environment variables to be set:

- `FRAC_WS_URL`: The WebSocket URL to connect to for receiving trading signals and actions.
- `FRAC_USER_TOKEN`: Your authentication token for the Fractrade WebSocket service.
- `HYPERLIQUID_PRIVATE_KEY`: Your HyperLiquid private key for signing transactions.
- `HYPERLIQUID_PUBLIC_ADDRESS`: Your HyperLiquid wallet address.
- `HYPERLIQUID_ENV`: The HyperLiquid environment to use (`mainnet` or `testnet`).

You can set these variables in your environment or use a `.env` file in the current directory.

#### Using a .env File (Recommended)

For development and deployment, we recommend using a `.env` file to manage your environment variables. A `.env.example` file is provided as a template:

```bash
# Copy the example file and edit it with your values
cp .env.example .env
# Edit the .env file with your actual values
nano .env  # or use your preferred editor
```

The `.env.example` file includes placeholders for all required and optional environment variables:

```
# WebSocket connection settings
FRAC_WS_URL=wss://example.com/ws
FRAC_USER_TOKEN=your_user_token_here

# Hyperliquid API settings
HYPERLIQUID_API_URL=https://api.hyperliquid.xyz
HYPERLIQUID_PRIVATE_KEY=your_private_key_here
HYPERLIQUID_PUBLIC_ADDRESS=your_wallet_address_here
HYPERLIQUID_ENV=mainnet  # or testnet
```

**Security Best Practices:**

1. **Never commit your `.env` file to version control.** The project's `.gitignore` file is already configured to exclude `.env` files.
2. **Restrict access to your `.env` file** on production servers using appropriate file permissions.
3. **Regularly rotate your API keys and secrets** as a security measure.
4. **Use different API keys for development and production** environments.

## Message Format

The executor expects messages in the following formats:

### Action Message

```json
{
  "type": "ACTION",
  "data": {
    "action_id": "execute_hyperliquid_perp_trade",
    "config": {
      "position": {
        "symbol": "BTC",
        "size": 0.01,
        "side": "BUY"
      }
    }
  }
}
```

## Supported Actions

The executor supports the following actions:

- `execute_hyperliquid_perp_trade`: Execute a trade on HyperLiquid.
- `set_hyperliquid_perp_stop_loss`: Set a stop loss for a position on HyperLiquid.
- `set_hyperliquid_perp_take_profit`: Set a take profit for a position on HyperLiquid.

## Creating Your Own Executor

The `FractradeExecutor` is an abstract base class that requires you to implement the following methods:

- `handle_hyperliquid_perp_trade`: Execute a trade on HyperLiquid.
- `handle_set_hyperliquid_perp_stop_loss`: Set a stop loss for a position.
- `handle_set_hyperliquid_perp_take_profit`: Set a take profit for a position.

Here's an example of creating your own custom executor:

```python
from fractrade_executor import FractradeExecutor
import logging

logger = logging.getLogger(__name__)

class MyCustomExecutor(FractradeExecutor):
    async def handle_hyperliquid_perp_trade(self, config):
        """Implement your custom trade execution logic"""
        # Extract position details
        position = config.get("position", {})
        symbol = position.get("symbol")
        size = float(position.get("size", 0))
        side = position.get("side", "").upper()
        
        # Your custom validation logic
        if symbol == "BTC" and size > 0.1:
            logger.warning(f"Reducing BTC position size from {size} to 0.1")
            size = 0.1
        
        # Execute the trade
        if side == "BUY":
            order = self.hl_client.buy(symbol, size)
        else:
            order = self.hl_client.sell(symbol, size)
        
        logger.info(f"Trade executed: {symbol} {side} {size}")
        
    async def handle_set_hyperliquid_perp_stop_loss(self, config):
        """Implement your custom stop loss logic"""
        # Your implementation here
        pass
        
    async def handle_set_hyperliquid_perp_take_profit(self, config):
        """Implement your custom take profit logic"""
        # Your implementation here
        pass
```

You can then run your custom executor:

```python
import asyncio
from my_executor import MyCustomExecutor

async def main():
    executor = MyCustomExecutor()
    await executor.run()

if __name__ == "__main__":
    asyncio.run(main()) 