#!/usr/bin/env python3
"""
Configuration file for NetBox DNS Plugin installer.
Contains all paths, dependencies, and settings used throughout the installation process.
"""

import os

# =============================================================================
# Installer Base Path
# =============================================================================

# Base path where the installer and config files are located
INSTALLER_BASE_PATH = os.path.dirname(os.path.abspath(__file__))

# Path to bind environment configuration files within the installer
BIND_CONFIGS_PATH = os.path.join(INSTALLER_BASE_PATH, "bind-environment-configs")

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

# =============================================================================
# BIND DNS Configuration
# =============================================================================

# DNF packages required for BIND DNS server with chroot and utilities
BIND_PACKAGES = [
    "bind",
    "bind-chroot",
    "bind-utils",
]

# Base path for BIND chroot environment
BIND_CHROOT_BASE = "/var/named/chroot/"

# Path to BIND config files within chroot
BIND_CHROOT_ETC = "/var/named/chroot/etc/"

# Path to BIND log directory within chroot
BIND_CHROOT_LOG = "/var/named/chroot/var/named/log/"

# User and group for BIND ownership
BIND_USER = "named"
BIND_GROUP = "named"

# Service name for chroot BIND
BIND_SERVICE = "named-chroot"

# Directories to create under /var/named/chroot/etc/
BIND_ETC_DIRECTORIES = [
    "backups",
    "archived",
    "archived/forward",
    "archived/reverse",
    "zones",
    "zones/forward",
    "zones/reverse",
    "third-party-dns",
]

# All directories that need permissions, ownership, and SGID set
BIND_MANAGED_DIRECTORIES = [
    "/var/named/chroot/etc",
    "/var/named/chroot/etc/zones/forward",
    "/var/named/chroot/etc/zones/reverse",
    "/var/named/chroot/etc/archived",
    "/var/named/chroot/etc/archived/forward",
    "/var/named/chroot/etc/archived/reverse",
    "/var/named/chroot/etc/backups",
    "/var/named/chroot/var/named/log",
    "/var/named/chroot/etc/third-party-dns",
]

# Directory permissions mode
BIND_DIR_MODE = 0o755

# Primary BIND config source directory name
BIND_PRIMARY_CONFIG_DIR = "netbox-primary"
