#!/usr/bin/env python3
"""
Configuration file for NetBox DNS Plugin installer.
Contains all paths, dependencies, and settings used throughout the installation process.
"""

import os

# =============================================================================
# Environment Configuration
# =============================================================================

# Current environment: "dev", "test", or "prod"
ENVIRONMENT = "dev"

# Environment-specific settings
ENVIRONMENTS = {
    "prod": {
        "server_ip": "9.12.46.13",
        "server_url": "https://netbox.sgn.ibm.com",
        "server_api_key": "09aa8b0b70a15e77b6845baa8be4de90880e14d6",
    },
    "test": {
        "server_ip": "9.12.46.7",
        "server_url": "https://netbox-test.sgn.ibm.com",
        "server_api_key": "09aa8b0b70a15e77b6845baa8be4de90880e14d6",
    },
    "dev": {
        "server_ip": "9.12.46.8",
        "server_url": "https://netbox-dev.sgn.ibm.com",
        "server_api_key": "09aa8b0b70a15e77b6845baa8be4de90880e14d6",
    },
}


def get_env_config():
    """
    Returns the configuration dictionary for the current environment.

    Returns:
        dict: Environment configuration with server_ip, server_url, server_api_key
    """
    if ENVIRONMENT not in ENVIRONMENTS:
        raise ValueError(f"Invalid ENVIRONMENT: {ENVIRONMENT}. Must be one of: {list(ENVIRONMENTS.keys())}")
    return ENVIRONMENTS[ENVIRONMENT]


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

# =============================================================================
# NetBox Plugin Settings
# =============================================================================

# SSH git repository for netbox-ipdns plugin
NETBOX_IPDNS_REPO = "git@github.com:Parzival-88/netbox-ipdns.git"

# =============================================================================
# OctoDNS Configuration
# =============================================================================

# Directory for OctoDNS configuration files
OCTODNS_CONFIG_DIR = "/opt/octodns/config"

# Path to the main OctoDNS config file
OCTODNS_CONFIG_FILE = "/opt/octodns/config/config.yaml"

# Directory permissions mode
OCTODNS_DIR_MODE = 0o755

# User and group for OctoDNS directory ownership
OCTODNS_USER = "root"
OCTODNS_GROUP = "named"

# OctoDNS config.yaml template with placeholders for environment variables
OCTODNS_CONFIG_TEMPLATE = """---
providers:

  netbox:
     class: octodns_netbox_dns.NetBoxDNSProvider
     url: $server_url
     token: "$server_api_key"
     view: false
     replace_duplicates: false
     make_absolute: false
     disable_ptr: false
     insecure_request: true

  rfc2136:
    class: octodns_bind.Rfc2136Provider
    # The address of nameserver to perform zone transfer against
    host: $server_ip
    # The port that the nameserver is listening on. Optional. Default: 53
    port: 53
    # Use IPv6 to perform operations. Optional. Default: False
    ipv6: False
    # The number of seconds to wait until timing out. Optional. Default: 15
    timeout: 15
    # optional, default: non-authed
    key_name: netbox
    # optional, default: non-authed
    key_secret: 5Be6wU3DCAWRsrfNFb996GkbmV3NaOwKLkJJ/ty9N0k=
    # optional, see https://github.com/rthalley/dnspython/blob/master/dns/tsig.py#L78
    # for available algorithms
    key_algorithm: hmac-sha256

zones:

# Forward Zones - All zones/domains that form a FQDN

# Reverse Zone - All reverse zones for prefixes in Netbox
"""
