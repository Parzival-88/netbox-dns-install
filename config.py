#!/usr/bin/env python3
"""
Configuration file for NetBox DNS Plugin installer.
Contains all paths, dependencies, and settings used throughout the installation process.
"""

# =============================================================================
# NetBox Directory Paths
# =============================================================================

# Path to the Python virtual environment used by NetBox
VENV_PATH = "/opt/netbox/current/venv-py3/"

# Path to the NetBox plugins directory
PLUGINS_PATH = "/opt/netbox/current/netbox/plugins/"

# Path to the Django manage.py script for running management commands
MANAGE_PY = "/opt/netbox/current/netbox/manage.py"

# Path to the NetBox configuration file
NETBOX_CONFIG = "/opt/netbox/current/netbox/netbox/configuration.py"

# =============================================================================
# Pip Dependencies
# =============================================================================

# List of Python packages to install in the virtual environment
PIP_PACKAGES = [
    "octodns",
    "mysql-connector-python>=8.0.0",
    "netaddr",
    "octodns-bind",
    "octodns-ddns",
    "octodns-netbox-dns",
    "PyYAML>=6.0",
    "pynetbox>=7.0.0",
    "requests>=2.31.0",
    "urllib3>=2.0.0",
]
