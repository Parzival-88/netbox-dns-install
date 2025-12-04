#!/usr/bin/env python3
"""
Module for installing pip dependencies into the NetBox virtual environment.
Handles package installation with error checking and logging.
"""

import logging
import subprocess
import sys
import os

# Get logger for this module
logger = logging.getLogger(__name__)


def get_pip_path(venv_path):
    """
    Constructs the full path to the pip executable within a virtual environment.

    Args:
        venv_path: Path to the virtual environment directory

    Returns:
        Full path to the pip executable
    """
    return os.path.join(venv_path, "bin", "pip")


def install_packages(venv_path, packages):
    """
    Installs a list of Python packages using the pip from the specified virtual environment.

    Args:
        venv_path: Path to the virtual environment directory
        packages: List of package names/specifiers to install

    Returns:
        True if all packages installed successfully, False otherwise
    """
    pip_path = get_pip_path(venv_path)

    # Verify pip executable exists before attempting installation
    if not os.path.exists(pip_path):
        logger.error(f"Pip executable not found at: {pip_path}")
        return False

    logger.info(f"Using pip at: {pip_path}")
    logger.info(f"Installing {len(packages)} packages...")

    # Build the pip install command with all packages
    command = [pip_path, "install"] + packages

    try:
        # Execute pip install and capture output
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False
        )

        # Log stdout if present
        if result.stdout:
            logger.debug(result.stdout)

        # Check if the command succeeded
        if result.returncode == 0:
            logger.info("All packages installed successfully")
            return True
        else:
            # Log error output if installation failed
            logger.error(f"Pip install failed with return code: {result.returncode}")
            if result.stderr:
                logger.error(result.stderr)
            return False

    except subprocess.SubprocessError as e:
        # Handle any subprocess-related errors
        logger.error(f"Failed to execute pip command: {e}")
        return False
    except Exception as e:
        # Catch any unexpected errors
        logger.error(f"Unexpected error during package installation: {e}")
        return False


def install_dependencies(venv_path, packages):
    """
    Main entry point for installing pip dependencies.
    Wrapper function that provides a clean interface for the installer.

    Args:
        venv_path: Path to the virtual environment directory
        packages: List of package names/specifiers to install

    Returns:
        True if installation succeeded, False otherwise
    """
    logger.info("=" * 60)
    logger.info("Starting pip dependency installation")
    logger.info("=" * 60)

    success = install_packages(venv_path, packages)

    if success:
        logger.info("Pip dependency installation completed successfully")
    else:
        logger.error("Pip dependency installation failed")

    return success
