#!/usr/bin/env python3
"""
Module for installing the netbox-ipdns plugin.
Handles cloning the plugin repository to the NetBox plugins directory
and configuring the global_variables.py file.
"""

import logging
import subprocess
import os
import shutil
import re

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


def copy_global_variables(plugins_path):
    """
    Copies the global_variables.example.py to global_variables.py.

    Args:
        plugins_path: Path to the NetBox plugins directory

    Returns:
        True if copy succeeded, False otherwise
    """
    example_file = os.path.join(
        plugins_path, "netbox-ipdns", "netbox_ipdns", "global_variables.example.py"
    )
    target_file = os.path.join(
        plugins_path, "netbox-ipdns", "netbox_ipdns", "global_variables.py"
    )

    logger.info(f"Copying {example_file} to {target_file}")

    # Check if example file exists
    if not os.path.exists(example_file):
        logger.error(f"Example file not found: {example_file}")
        return False

    try:
        shutil.copy2(example_file, target_file)
        logger.info("global_variables.py created successfully")
        return True
    except (shutil.Error, OSError) as e:
        logger.error(f"Failed to copy global_variables file: {e}")
        return False


def configure_global_variables(plugins_path, ipdns_config):
    """
    Configures the global_variables.py file with environment-specific values.

    Args:
        plugins_path: Path to the NetBox plugins directory
        ipdns_config: Dictionary containing configuration values

    Returns:
        True if configuration succeeded, False otherwise
    """
    target_file = os.path.join(
        plugins_path, "netbox-ipdns", "netbox_ipdns", "global_variables.py"
    )

    logger.info(f"Configuring {target_file}")

    try:
        # Read the current file content
        with open(target_file, 'r') as f:
            content = f.read()

        # Replace NETBOX_PATH value
        content = re.sub(
            r'NETBOX_PATH\s*=\s*["\'][^"\']*["\']',
            f'NETBOX_PATH = \'{ipdns_config["netbox_path"]}\'',
            content
        )

        # Replace PYTHON_PATH value
        content = re.sub(
            r'PYTHON_PATH\s*=\s*["\'][^"\']*["\']',
            f'PYTHON_PATH = \'{ipdns_config["python_path"]}\'',
            content
        )

        # Replace NETBOX_TOKEN value
        content = re.sub(
            r'NETBOX_TOKEN\s*=\s*["\'][^"\']*["\']',
            f'NETBOX_TOKEN = \'{ipdns_config["server_api_key"]}\'',
            content
        )

        # Replace DEFAULT_SOA_RNAME value
        content = re.sub(
            r'DEFAULT_SOA_RNAME\s*=\s*["\'][^"\']*["\']',
            f'DEFAULT_SOA_RNAME = \'{ipdns_config["default_soa_rname"]}\'',
            content
        )

        # Replace PREFIX_SIGNALS_ENABLED value
        content = re.sub(
            r'PREFIX_SIGNALS_ENABLED\s*=\s*(True|False)',
            'PREFIX_SIGNALS_ENABLED = False',
            content
        )

        # Replace ZONE_SIGNALS_ENABLED value
        content = re.sub(
            r'ZONE_SIGNALS_ENABLED\s*=\s*(True|False)',
            'ZONE_SIGNALS_ENABLED = False',
            content
        )

        # Replace TENANT_GROUP_PREFIX value
        content = re.sub(
            r'TENANT_GROUP_PREFIX\s*=\s*["\'][^"\']*["\']',
            f'TENANT_GROUP_PREFIX = \'{ipdns_config["tenant_group_prefix"]}\'',
            content
        )

        # Build protected zones list string
        protected_zones_str = ",\n        ".join(
            [f'"{zone}"' for zone in ipdns_config["protected_zones"]]
        )

        # Replace protected_zones list in PROTECTED_ZONE_CONFIG
        content = re.sub(
            r"('protected_zones':\s*\[)[^\]]*(\])",
            f"\\1\n        {protected_zones_str},\n    \\2",
            content,
            flags=re.DOTALL
        )

        # Replace default MNAME in get_default_mname function
        content = re.sub(
            r'(NameServer\.objects\.get\(name=)["\'][^"\']*["\'](\))',
            f'\\1"{ipdns_config["default_mname"]}"\\2',
            content
        )

        # Build nameservers list string
        nameservers_str = ",\n        ".join(
            [f'"{ns}"' for ns in ipdns_config["default_nameservers"]]
        )

        # Replace nameservers list in get_default_nameservers function
        content = re.sub(
            r'(NameServer\.objects\.filter\(name__in=\[)[^\]]*(\]\))',
            f'\\1\n        {nameservers_str},\n    \\2',
            content,
            flags=re.DOTALL
        )

        # Write the updated content back
        with open(target_file, 'w') as f:
            f.write(content)

        logger.info("global_variables.py configured successfully")
        return True

    except (OSError, IOError) as e:
        logger.error(f"Failed to configure global_variables.py: {e}")
        return False


def install_ipdns(repo_url, plugins_path, ipdns_config):
    """
    Main entry point for netbox-ipdns plugin installation.
    Clones the plugin repository and configures global_variables.py.

    Args:
        repo_url: SSH URL of the netbox-ipdns repository
        plugins_path: Path to the NetBox plugins directory
        ipdns_config: Dictionary containing configuration values

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

    # Copy global_variables.example.py to global_variables.py
    if not copy_global_variables(plugins_path):
        logger.error("Failed to copy global_variables file")
        return False

    # Configure global_variables.py with environment values
    if not configure_global_variables(plugins_path, ipdns_config):
        logger.error("Failed to configure global_variables.py")
        return False

    logger.info("=" * 60)
    logger.info("netbox-ipdns plugin installation completed successfully")
    logger.info("=" * 60)

    return True
