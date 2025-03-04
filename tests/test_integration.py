"""
Integration tests for the fractrade-executor package
"""

import asyncio
import json
import pytest
import os
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime

from fractrade_executor.executor import FractradeExecutor
from fracservice.fracactions.fracaction import ActionType

# Set up test environment variables
os.environ['FRAC_WS_URL'] = 'ws://localhost:8000'
os.environ['FRAC_USER_TOKEN'] = 'test-token-123'
os.environ['HYPERLIQUID_PRIVATE_KEY'] = 'test-private-key'
os.environ['HYPERLIQUID_PUBLIC_ADDRESS'] = 'test-public-address'

class MockWebSocket:
    """Mock WebSocket connection for testing"""
    def __init__(self):
        self.connected = False
        self.messages = []
        self.send = AsyncMock()
        self.recv = AsyncMock(side_effect=self._get_next_message)
        self.close = AsyncMock()

    async def _get_next_message(self):
        """Get next message from queue or raise ConnectionClosed"""
        if self.messages:
            return self.messages.pop(0)
        return await asyncio.sleep(0.1)  # Simulate waiting for messages

    async def __aenter__(self):
        """Async context manager entry"""
        self.connected = True
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        self.connected = False
        await self.close()

class MockHyperliquidClient:
    """Mock HyperLiquid client for testing"""
    def __init__(self, account=None):
        self.execute_perp_trade = AsyncMock()
        self.set_stop_loss = AsyncMock()
        self.set_take_profit = AsyncMock()
        self.is_authenticated = MagicMock(return_value=True)
        self.aclose = AsyncMock()
        self.account = account

    async def close(self):
        """Close the client session"""
        await self.aclose()

class TestExecutor(FractradeExecutor):
    """Test executor implementation"""
    def _init_hyperliquid_client(self):
        """Override to use mock client"""
        self.hl_client = MockHyperliquidClient()
        self.logger.info("Initialized mock HyperLiquid client")

@pytest.fixture
def mock_websocket():
    """Fixture for mock WebSocket"""
    return MockWebSocket()

@pytest.fixture
def mock_hl_client():
    """Fixture for mock HyperLiquid client"""
    return MockHyperliquidClient()

@pytest.mark.asyncio
async def test_executor_trade_handling():
    """Test that executor properly handles trade messages"""
    # Create mock websocket
    mock_ws = MockWebSocket()
    
    # Create test messages
    messages = [
        # 1. Open a BTC long position
        {
            "type": "ACTION",
            "data": {
                "action_id": "execute_hyperliquid_perp_trade",
                "config": {
                    "position": {
                        "symbol": "BTC",
                        "size": "0.01",
                        "side": "BUY",
                        "reduce_only": False
                    }
                }
            }
        },
        # 2. Set stop loss
        {
            "type": "ACTION",
            "data": {
                "action_id": "set_hyperliquid_perp_stop_loss",
                "config": {
                    "position": {
                        "symbol": "BTC",
                        "size": "0.01",
                        "side": "SELL",
                        "trigger_price": "45000",
                        "reduce_only": True
                    }
                }
            }
        },
        # 3. Set take profit
        {
            "type": "ACTION",
            "data": {
                "action_id": "set_hyperliquid_perp_take_profit",
                "config": {
                    "position": {
                        "symbol": "BTC",
                        "size": "0.01",
                        "side": "SELL",
                        "trigger_price": "55000",
                        "reduce_only": True
                    }
                }
            }
        }
    ]
    
    # Queue the messages
    for msg in messages:
        mock_ws.messages.append(json.dumps(msg))
    
    # Create and start executor
    with patch('websockets.connect', return_value=mock_ws):
        executor = TestExecutor()
        try:
            await executor.start()
            
            # Wait for messages to be processed
            await asyncio.sleep(0.5)
            
            # Verify trade execution
            executor.hl_client.execute_perp_trade.assert_called_once_with(
                symbol="BTC",
                size=0.01,
                side="BUY",
                reduce_only=False
            )
            
            # Verify stop loss
            executor.hl_client.set_stop_loss.assert_called_once_with(
                symbol="BTC",
                size=0.01,
                trigger_price=45000.0,
                side="SELL"
            )
            
            # Verify take profit
            executor.hl_client.set_take_profit.assert_called_once_with(
                symbol="BTC",
                size=0.01,
                trigger_price=55000.0,
                side="SELL"
            )
            
        finally:
            await executor.stop() 