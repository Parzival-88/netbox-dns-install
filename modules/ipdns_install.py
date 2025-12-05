#!/usr/bin/env python3
"""
Module for installing the netbox-ipdns plugin.
Handles cloning the plugin repository to the NetBox plugins directory.
"""

import logging
import subprocess
import os

# Get logger for this module
logger = logging.getLogger(__name__)


def clone_repository(repo_url, dest_path):
    """
    Clones a git repository to the specified destination.

    Args:
        repo_url: SSH or HTTPS URL of the git repository
        dest_path: Directory where the repository should be cloned

    Returns:
        True if clone succeeded, False otherwise
    """
    # Extract repository name from URL for the target directory
    repo_name = os.path.basename(repo_url).replace(".git", "")
    target_dir = os.path.join(dest_path, repo_name)

    # Check if target directory already exists
    if os.path.exists(target_dir):
        logger.warning(f"Directory already exists: {target_dir}")
        logger.info("Skipping clone - repository may already be installed")
        return True

    logger.info(f"Cloning repository: {repo_url}")
    logger.info(f"Destination: {target_dir}")

    try:
        command = ["git", "clone", repo_url, target_dir]
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False
        )

        if result.returncode == 0:
            logger.info(f"Repository cloned successfully to {target_dir}")
            if result.stdout:
                logger.debug(result.stdout)
            return True
        else:
            logger.error(f"Git clone failed with return code: {result.returncode}")
            if result.stderr:
                logger.error(result.stderr)
            return False

    except subprocess.SubprocessError as e:
        logger.error(f"Failed to execute git clone: {e}")
        return False


def install_ipdns(repo_url, plugins_path):
    """
    Main entry point for netbox-ipdns plugin installation.
    Clones the plugin repository to the NetBox plugins directory.

    Args:
        repo_url: SSH URL of the netbox-ipdns repository
        plugins_path: Path to the NetBox plugins directory

    Returns:
        True if installation succeeded, False otherwise
    """
    logger.info("=" * 60)
    logger.info("Starting netbox-ipdns Plugin Installation")
    logger.info("=" * 60)

    # Verify plugins directory exists
    if not os.path.exists(plugins_path):
        logger.error(f"Plugins directory does not exist: {plugins_path}")
        return False

    # Clone the repository
    if not clone_repository(repo_url, plugins_path):
        logger.error("Failed to clone netbox-ipdns repository")
        return False

    logger.info("=" * 60)
    logger.info("netbox-ipdns plugin installation completed successfully")
    logger.info("=" * 60)

    return True
