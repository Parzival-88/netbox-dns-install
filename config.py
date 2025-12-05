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

# Base path to the NetBox installation
NETBOX_PATH = "/opt/netbox/current"

# Path to the Python executable in the virtual environment
PYTHON_PATH = "/opt/netbox/current/venv-py3/bin/python"

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
# NetBox IPDNS Plugin Settings
# =============================================================================

# SSH git repository for netbox-ipdns plugin
NETBOX_IPDNS_REPO = "git@github.com:Parzival-88/netbox-ipdns.git"

# Default SOA RNAME (responsible person email in DNS format)
IPDNS_DEFAULT_SOA_RNAME = "sgn-netbox.ibm.com"

# Default MNAME (primary nameserver) for SOA records
IPDNS_DEFAULT_MNAME = "netbox.sgn.ibm.com"

# Protected zones that require special permissions to modify
IPDNS_PROTECTED_ZONES = [
    "stglabs.ibm.com",
    "pok.stglabs.ibm.com",
    "aus.stglabs.ibm.com",
    "tuc.stglabs.ibm.com",
    "rch.stglabs.ibm.com",
    "rtp.stglabs.ibm.com",
    "alm.stglabs.ibm.com",
    "gdl.stglabs.ibm.com",
    "sgn.ibm.com",
    "tadn.ibm.com",
]

# Default nameservers for new zones
IPDNS_DEFAULT_NAMESERVERS = [
    "pokdns-att-01.stglabs.ibm.com",
    "pokdns-att-02.stglabs.ibm.com",
    "tucdns-att-01.stglabs.ibm.com",
    "tucdns-att-02.stglabs.ibm.com",
]

# Tenant group prefix for IPDNS
IPDNS_TENANT_GROUP_PREFIX = "sgn-tenant"

# Shared directory for netbox-ipdns plugin
IPDNS_SHARED_DIR = "/opt/netbox/shared/netbox-ipdns"

# Directory permissions mode for IPDNS shared directory
IPDNS_DIR_MODE = 0o755

# User and group for IPDNS shared directory ownership
IPDNS_USER = "netbox"
IPDNS_GROUP = "netbox"

# Systemd service override directories
NETBOX_SERVICE_OVERRIDE_DIR = "/etc/systemd/system/netbox.service.d"
NETBOX_RQWORKER_OVERRIDE_DIR = "/etc/systemd/system/netbox-rqworker@.service.d"

# Systemd override content to allow privilege escalation for DNS scripts
IPDNS_SERVICE_OVERRIDE_CONTENT = """[Service]
NoNewPrivileges=no
"""

# Sudoers file for netbox-ipdns DNS script permissions
IPDNS_SUDOERS_FILE = "/etc/sudoers.d/netbox-dns-script"

# Sudoers rules for netbox user to run DNS management commands
IPDNS_SUDOERS_CONTENT = """netbox ALL=(root) NOPASSWD: /usr/bin/python3 /opt/netbox/current/netbox/plugins/netbox-ipdns/netbox_ipdns/scripts/dns/zone_config_management.py *
netbox ALL=(root) NOPASSWD: /usr/sbin/named-checkconf
netbox ALL=(root) NOPASSWD: /usr/sbin/named-checkzone
netbox ALL=(root) NOPASSWD: /usr/bin/systemctl reload named-chroot
"""

# NetBox services to stop/start during IPDNS installation
NETBOX_SERVICES = [
    "netbox",
    "netbox-rqworker@1",
    "netbox.socket",
]

# Logging configuration for NetBox with netbox-ipdns support
IPDNS_LOGGING_CONFIG = r'''{"version": 1, "disable_existing_loggers": false, "formatters": {"verbose": {"format": "[{asctime}] {levelname} {name} {module} {process:d} {thread:d} - {message}", "style": "{"}, "simple": {"format": "{levelname}: {message}", "style": "{"}}, "handlers": {"file": {"level": "INFO", "class": "logging.FileHandler", "filename": "/opt/netbox/netbox/logs/debug.log", "formatter": "verbose"}, "console": {"level": "INFO", "class": "logging.StreamHandler", "formatter": "simple"}, "netbox_ipdns_file": {"level": "DEBUG", "class": "logging.FileHandler", "filename": "/opt/netbox/netbox/logs/netbox-ipdns.log", "formatter": "verbose"}, "netbox_ipdns_console": {"level": "DEBUG", "class": "logging.StreamHandler", "formatter": "simple"}}, "root": {"handlers": ["file", "console"], "level": "DEBUG"}, "loggers": {"django": {"handlers": ["file"], "level": "INFO", "propagate": true}, "netbox": {"handlers": ["file"], "level": "INFO", "propagate": false}, "django.request": {"handlers": ["file"], "level": "INFO", "propagate": false}, "django.db.backends": {"handlers": ["file"], "level": "INFO", "propagate": false}, "netbox_ipdns": {"handlers": ["netbox_ipdns_file", "netbox_ipdns_console"], "level": "DEBUG", "propagate": false}}}'''

# Plugins list for NetBox configuration
IPDNS_PLUGINS_LIST = r'''["netbox_dns", "netbox_ipdns", "netbox_lists"]'''

# Plugins configuration for NetBox
IPDNS_PLUGINS_CONFIG_SETTINGS = r'''{"netbox_dns": {"feature_ipam_coupling": true, "ipam_coupling_ip_address_status_list": ["active", "dhcp", "slaac"], "zone_nameservers": ["tucdns-att-02.stglabs.ibm.com", "pokdns-att-01.stglabs.ibm.com", "tucdns-att-01.stglabs.ibm.com", "pokdns-att-02.stglabs.ibm.com"], "zone_soa_mname": "pokdns01.stglabs.ibm.com", "zone_soa_rname": "sgn-netbox.ibm.com", "zone_soa_refresh": 28800, "zone_soa_retry": 7200, "zone_soa_expire": 604800, "zone_soa_minimum": 3600, "soa_serial_auto": true, "enforce_unique_records": false}, "netbox_acls": {"top_level_menu": true}}'''

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
