# Fractrade Executor Documentation

Welcome to the Fractrade Executor documentation. This package provides a framework for executing trading signals and actions on HyperLiquid and other exchanges.

## Overview

The Fractrade Executor is designed to connect to a WebSocket server to receive trading signals and action messages, and then execute them on the specified exchange. It currently supports HyperLiquid perpetual futures trading, including setting stop losses and take profits.

## Installation

You can install the Fractrade Executor using pip:

```bash
pip install fractrade-executor
```

Or using Poetry:

```bash
poetry add fractrade-executor
```

## Quick Start

To get started with the Fractrade Executor, you need to set up the required environment variables and run the executor:

```bash
# Set environment variables
export FRAC_WS_URL="wss://your-websocket-server.com/ws"
export HYPERLIQUID_PRIVATE_KEY="your-private-key"
export HYPERLIQUID_PUBLIC_ADDRESS="your-public-address"

# Run the executor
fractrade-executor
```

## Documentation Sections

- [Installation](installation.md)
- [Configuration](configuration.md)
- [Usage](usage.md)
- [Examples](examples.md)
- [Contributing](contributing.md) 