"""
Command-line interface for the fractrade-executor package
"""

import argparse
import logging
import sys
from typing import List, Optional

from .simple_executor import SimpleExecutor

logger = logging.getLogger(__name__)

def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """
    Parse command-line arguments
    
    Args:
        args: Command-line arguments (defaults to sys.argv[1:])
        
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Fractrade Executor - Execute trading signals and actions"
    )
    
    parser.add_argument(
        "--executor",
        choices=["simple"],
        default="simple",
        help="Executor type to use (default: simple)"
    )
    
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Logging level (default: INFO)"
    )
    
    return parser.parse_args(args)

def setup_logging(log_level: str) -> None:
    """
    Set up logging configuration
    
    Args:
        log_level: Logging level
    """
    logging.basicConfig(
        level=getattr(logging, log_level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

def main(args: Optional[List[str]] = None) -> int:
    """
    Main entry point for the CLI
    
    Args:
        args: Command-line arguments (defaults to sys.argv[1:])
        
    Returns:
        Exit code
    """
    parsed_args = parse_args(args)
    
    # Set up logging
    setup_logging(parsed_args.log_level)
    
    try:
        # Create executor (only SimpleExecutor is available as a built-in option)
        executor = SimpleExecutor()
        
        # Run executor
        executor.run()
        
        return 0
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received, exiting...")
        return 0
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 