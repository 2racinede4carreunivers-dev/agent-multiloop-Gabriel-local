"""
Main entry point for multi-loop agent
"""

import logging
import sys
from pathlib import Path

# Setup logging
from core.logging_setup import setup_logging
setup_logging("./logs")

logger = logging.getLogger(__name__)


def main():
    """Main entry point"""
    
    from ui.cli import CLIInterface
    
    logger.info("Starting Multi-Loop Mathematical Agent")
    
    cli = CLIInterface()
    cli.interactive_mode()


if __name__ == "__main__":
    main()
