#!/usr/bin/env python3
"""
Main installer script for NetBox DNS Plugin.
Orchestrates the installation process by calling individual modules based on
command-line arguments. Supports running modules individually or together.
"""

import argparse
import logging
import sys

# Import configuration
import config

# Import installation modules
from modules import pip_dependencies
from modules import bind_install
from modules import octodns_install
from modules import ipdns_install


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


def parse_arguments():
    """
    Parses command-line arguments for the installer.
    Supports modular installation with individual flags for each component.

    Returns:
        Parsed argument namespace
    """
    parser = argparse.ArgumentParser(
        description="NetBox DNS Plugin Installer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Install only pip packages
  python3 install.py --pip-packages

  # Install DNS as primary server (uses server_ip from ENVIRONMENT config)
  python3 install.py --dns --primary

  # Install DNS as secondary server
  python3 install.py --dns --secondary 9.11.227.25

  # Install OctoDNS configuration
  python3 install.py --octodns

  # Install netbox-ipdns plugin
  python3 install.py --ipdns

  # Install pip packages and DNS together
  python3 install.py --pip-packages --dns --primary

  # Install all components
  python3 install.py --all --primary
        """
    )

    # Pip packages module
    parser.add_argument(
        "--pip-packages",
        action="store_true",
        help="Install Python pip dependencies in the NetBox virtual environment"
    )

    # DNS install module
    parser.add_argument(
        "--dns",
        action="store_true",
        help="Install and configure BIND DNS server in chroot environment"
    )

    # Primary flag for DNS (used with --dns)
    parser.add_argument(
        "--primary",
        action="store_true",
        help="Configure as primary DNS server (uses server_ip from environment config)"
    )

    # Secondary IP for DNS (used with --dns)
    parser.add_argument(
        "--secondary",
        type=str,
        metavar="IP",
        help="Configure as secondary DNS server using config for specified IP"
    )

    # OctoDNS install module
    parser.add_argument(
        "--octodns",
        action="store_true",
        help="Install and configure OctoDNS with config.yaml"
    )

    # netbox-ipdns plugin install module
    parser.add_argument(
        "--ipdns",
        action="store_true",
        help="Install netbox-ipdns plugin from git repository"
    )

    # Install all modules
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all installation modules"
    )

    args = parser.parse_args()

    # Validate arguments
    if args.dns or args.all:
        if not args.primary and not args.secondary:
            parser.error("--dns requires either --primary or --secondary")
        if args.primary and args.secondary:
            parser.error("Cannot specify both --primary and --secondary")

    # Check if no modules selected
    if not args.pip_packages and not args.dns and not args.octodns and not args.ipdns and not args.all:
        parser.error("No installation module selected. Use --help for options.")

    return args


def run_pip_packages(logger):
    """
    Executes the pip packages installation module.

    Args:
        logger: Logger instance for output

    Returns:
        True if successful, False otherwise
    """
    logger.info("=" * 60)
    logger.info("Module: Pip Packages Installation")
    logger.info("=" * 60)

    return pip_dependencies.install_dependencies(
        config.VENV_PATH,
        config.PIP_PACKAGES
    )


def run_dns_install(logger, is_primary=False, secondary_ip=None):
    """
    Executes the BIND DNS installation module.

    Args:
        logger: Logger instance for output
        is_primary: True if installing as primary DNS server
        secondary_ip: IP address for secondary DNS configuration

    Returns:
        True if successful, False otherwise
    """
    # Get server_ip from environment config for primary installs
    env_config = config.get_env_config()
    primary_ip = env_config["server_ip"] if is_primary else None

    return bind_install.install_dns(
        configs_path=config.BIND_CONFIGS_PATH,
        primary_config_dir=config.BIND_PRIMARY_CONFIG_DIR,
        bind_packages=config.BIND_PACKAGES,
        chroot_etc=config.BIND_CHROOT_ETC,
        chroot_log=config.BIND_CHROOT_LOG,
        etc_directories=config.BIND_ETC_DIRECTORIES,
        managed_directories=config.BIND_MANAGED_DIRECTORIES,
        dir_mode=config.BIND_DIR_MODE,
        bind_user=config.BIND_USER,
        bind_group=config.BIND_GROUP,
        bind_service=config.BIND_SERVICE,
        primary_ip=primary_ip,
        secondary_ip=secondary_ip
    )


def run_octodns_install(logger):
    """
    Executes the OctoDNS installation module.

    Args:
        logger: Logger instance for output

    Returns:
        True if successful, False otherwise
    """
    logger.info("=" * 60)
    logger.info("Module: OctoDNS Installation")
    logger.info("=" * 60)

    # Get environment config for template substitution
    env_config = config.get_env_config()

    return octodns_install.install_octodns(
        config_dir=config.OCTODNS_CONFIG_DIR,
        config_file=config.OCTODNS_CONFIG_FILE,
        template=config.OCTODNS_CONFIG_TEMPLATE,
        dir_mode=config.OCTODNS_DIR_MODE,
        user=config.OCTODNS_USER,
        group=config.OCTODNS_GROUP,
        env_config=env_config
    )


def run_ipdns_install(logger):
    """
    Executes the netbox-ipdns plugin installation module.

    Args:
        logger: Logger instance for output

    Returns:
        True if successful, False otherwise
    """
    logger.info("=" * 60)
    logger.info("Module: netbox-ipdns Plugin Installation")
    logger.info("=" * 60)

    # Get environment config for API key
    env_config = config.get_env_config()

    # Build IPDNS configuration dictionary
    ipdns_config = {
        "netbox_path": config.NETBOX_PATH,
        "python_path": config.PYTHON_PATH,
        "server_api_key": env_config["server_api_key"],
        "default_soa_rname": config.IPDNS_DEFAULT_SOA_RNAME,
        "default_mname": config.IPDNS_DEFAULT_MNAME,
        "protected_zones": config.IPDNS_PROTECTED_ZONES,
        "default_nameservers": config.IPDNS_DEFAULT_NAMESERVERS,
        "tenant_group_prefix": config.IPDNS_TENANT_GROUP_PREFIX,
    }

    return ipdns_install.install_ipdns(
        repo_url=config.NETBOX_IPDNS_REPO,
        plugins_path=config.PLUGINS_PATH,
        ipdns_config=ipdns_config
    )


def main():
    """
    Main entry point for the installer.
    Parses arguments and executes requested installation modules.
    """
    # Initialize logging before any operations
    setup_logging()
    logger = logging.getLogger(__name__)

    # Parse command-line arguments
    args = parse_arguments()

    logger.info("=" * 60)
    logger.info("NetBox DNS Plugin Installer")
    logger.info("=" * 60)

    # Track overall installation success
    success = True

    # Determine which modules to run
    run_pip = args.pip_packages or args.all
    run_dns = args.dns or args.all
    run_octodns = args.octodns or args.all
    run_ipdns = args.ipdns or args.all

    # Execute pip packages module
    if run_pip:
        if not run_pip_packages(logger):
            logger.error("Failed to install pip dependencies")
            success = False

    # Execute DNS install module
    if run_dns:
        if not run_dns_install(logger, args.primary, args.secondary):
            logger.error("Failed to install BIND DNS")
            success = False

    # Execute OctoDNS install module
    if run_octodns:
        if not run_octodns_install(logger):
            logger.error("Failed to install OctoDNS")
            success = False

    # Execute netbox-ipdns plugin install module
    if run_ipdns:
        if not run_ipdns_install(logger):
            logger.error("Failed to install netbox-ipdns plugin")
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
