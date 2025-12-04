#!/usr/bin/env python3
"""
Main installer script for NetBox DNS Plugin.
Orchestrates the installation process by calling individual modules in sequence.
"""

import logging
import sys

# Import configuration
import config

# Import installation modules
from modules import pip_dependencies


def setup_logging():
    """
    Configures the logging system for the installer.
    Sets up console output with timestamp, level, and message formatting.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


def main():
    """
    Main entry point for the installer.
    Executes each installation step in sequence and tracks overall success.
    """
    # Initialize logging before any operations
    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("=" * 60)
    logger.info("NetBox DNS Plugin Installer")
    logger.info("=" * 60)

    # Track overall installation success
    success = True

    # Step 1: Install pip dependencies
    if not pip_dependencies.install_dependencies(config.VENV_PATH, config.PIP_PACKAGES):
        logger.error("Failed to install pip dependencies")
        success = False

    # Final status report
    logger.info("=" * 60)
    if success:
        logger.info("Installation completed successfully")
    else:
        logger.error("Installation completed with errors")
        sys.exit(1)

    logger.info("=" * 60)


if __name__ == "__main__":
    main()
