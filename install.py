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

  # Install DNS as primary server
  python3 install.py --dns-install --primary-ip 10.1.2.3

  # Install DNS as secondary server
  python3 install.py --dns-install --secondary-ip 9.11.227.25

  # Install pip packages and DNS together
  python3 install.py --pip-packages --dns-install --primary-ip 10.1.2.3

  # Install all components
  python3 install.py --all --primary-ip 10.1.2.3
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
        "--dns-install",
        action="store_true",
        help="Install and configure BIND DNS server in chroot environment"
    )

    # Primary IP for DNS (used with --dns-install)
    parser.add_argument(
        "--primary-ip",
        type=str,
        metavar="IP",
        help="Configure as primary DNS server with specified IP address"
    )

    # Secondary IP for DNS (used with --dns-install)
    parser.add_argument(
        "--secondary-ip",
        type=str,
        metavar="IP",
        help="Configure as secondary DNS server using config for specified IP"
    )

    # Install all modules
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all installation modules"
    )

    args = parser.parse_args()

    # Validate arguments
    if args.dns_install or args.all:
        if not args.primary_ip and not args.secondary_ip:
            parser.error("--dns-install requires either --primary-ip or --secondary-ip")
        if args.primary_ip and args.secondary_ip:
            parser.error("Cannot specify both --primary-ip and --secondary-ip")

    # Check if no modules selected
    if not args.pip_packages and not args.dns_install and not args.all:
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


def run_dns_install(logger, primary_ip=None, secondary_ip=None):
    """
    Executes the BIND DNS installation module.

    Args:
        logger: Logger instance for output
        primary_ip: IP address for primary DNS configuration
        secondary_ip: IP address for secondary DNS configuration

    Returns:
        True if successful, False otherwise
    """
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
    run_dns = args.dns_install or args.all

    # Execute pip packages module
    if run_pip:
        if not run_pip_packages(logger):
            logger.error("Failed to install pip dependencies")
            success = False

    # Execute DNS install module
    if run_dns:
        if not run_dns_install(logger, args.primary_ip, args.secondary_ip):
            logger.error("Failed to install BIND DNS")
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
