#!/usr/bin/env python3
"""
Module for installing and configuring OctoDNS.
Handles directory creation, permissions, and config file generation.
"""

import logging
import os
import stat
import subprocess
from string import Template

# Get logger for this module
logger = logging.getLogger(__name__)


def create_config_directory(config_dir):
    """
    Creates the OctoDNS configuration directory and parent directories.

    Args:
        config_dir: Full path to the config directory to create

    Returns:
        True if directory created successfully, False otherwise
    """
    logger.info(f"Creating OctoDNS config directory: {config_dir}")
    try:
        os.makedirs(config_dir, exist_ok=True)
        logger.info(f"Directory created: {config_dir}")
        return True
    except OSError as e:
        logger.error(f"Failed to create directory {config_dir}: {e}")
        return False


def set_directory_ownership(directory, user, group):
    """
    Sets ownership on the specified directory.

    Args:
        directory: Path to the directory
        user: Username for ownership
        group: Group name for ownership

    Returns:
        True if ownership set successfully, False otherwise
    """
    logger.info(f"Setting ownership to {user}:{group} on {directory}")
    try:
        command = ["chown", f"{user}:{group}", directory]
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False
        )

        if result.returncode == 0:
            logger.info(f"Ownership set successfully on {directory}")
            return True
        else:
            logger.error(f"Failed to set ownership: {result.stderr}")
            return False

    except subprocess.SubprocessError as e:
        logger.error(f"Failed to execute chown command: {e}")
        return False


def set_directory_permissions(directory, mode):
    """
    Sets permissions and SGID bit on the specified directory.

    Args:
        directory: Path to the directory
        mode: Permission mode (e.g., 0o755)

    Returns:
        True if permissions set successfully, False otherwise
    """
    logger.info(f"Setting permissions {oct(mode)} with SGID on {directory}")
    try:
        # Set base permissions
        os.chmod(directory, mode)

        # Add SGID bit so new files inherit the group
        current_mode = os.stat(directory).st_mode
        new_mode = current_mode | stat.S_ISGID
        os.chmod(directory, new_mode)

        logger.info(f"Permissions set successfully on {directory}")
        return True

    except OSError as e:
        logger.error(f"Failed to set permissions on {directory}: {e}")
        return False


def create_config_file(config_file, template, env_config):
    """
    Creates the OctoDNS config.yaml file from template with environment values.

    Args:
        config_file: Full path to the config file to create
        template: Template string with $placeholders
        env_config: Dictionary containing server_ip, server_url, server_api_key

    Returns:
        True if file created successfully, False otherwise
    """
    logger.info(f"Creating OctoDNS config file: {config_file}")
    try:
        # Substitute environment values into template
        config_template = Template(template)
        config_content = config_template.substitute(
            server_url=env_config["server_url"],
            server_api_key=env_config["server_api_key"],
            server_ip=env_config["server_ip"]
        )

        # Write the config file
        with open(config_file, 'w') as f:
            f.write(config_content)

        logger.info(f"Config file created: {config_file}")
        return True

    except (OSError, KeyError) as e:
        logger.error(f"Failed to create config file {config_file}: {e}")
        return False


def install_octodns(config_dir, config_file, template, dir_mode, user, group, env_config):
    """
    Main entry point for OctoDNS installation.
    Orchestrates directory creation, permissions, and config file generation.

    Args:
        config_dir: Path to OctoDNS config directory
        config_file: Path to config.yaml file
        template: Config file template string
        dir_mode: Permission mode for directory
        user: User for directory ownership
        group: Group for directory ownership
        env_config: Environment configuration dictionary

    Returns:
        True if installation succeeded, False otherwise
    """
    logger.info("=" * 60)
    logger.info("Starting OctoDNS Installation")
    logger.info("=" * 60)

    # Step 1: Create config directory
    if not create_config_directory(config_dir):
        logger.error("Failed to create OctoDNS config directory")
        return False

    # Step 2: Set directory ownership
    if not set_directory_ownership(config_dir, user, group):
        logger.error("Failed to set directory ownership")
        return False

    # Step 3: Set directory permissions with SGID
    if not set_directory_permissions(config_dir, dir_mode):
        logger.error("Failed to set directory permissions")
        return False

    # Step 4: Create config.yaml from template
    if not create_config_file(config_file, template, env_config):
        logger.error("Failed to create OctoDNS config file")
        return False

    logger.info("=" * 60)
    logger.info("OctoDNS installation completed successfully")
    logger.info("=" * 60)

    return True
