#!/usr/bin/env python3
"""
Module for installing and configuring BIND DNS server in a chroot environment.
Handles package installation, directory creation, config file deployment,
permissions, and service management.
"""

import logging
import subprocess
import os
import shutil
import stat

# Get logger for this module
logger = logging.getLogger(__name__)


def run_command(command, description):
    """
    Executes a shell command and logs the result.

    Args:
        command: List of command arguments to execute
        description: Human-readable description of the command for logging

    Returns:
        True if command succeeded, False otherwise
    """
    logger.info(f"Running: {description}")
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False
        )

        if result.returncode == 0:
            logger.debug(result.stdout)
            return True
        else:
            logger.error(f"Command failed: {' '.join(command)}")
            if result.stderr:
                logger.error(result.stderr)
            return False

    except subprocess.SubprocessError as e:
        logger.error(f"Failed to execute command: {e}")
        return False


def install_bind_packages(packages):
    """
    Installs BIND DNS packages using dnf package manager.

    Args:
        packages: List of package names to install

    Returns:
        True if installation succeeded, False otherwise
    """
    logger.info("Installing BIND DNS packages...")
    command = ["dnf", "install", "-y"] + packages
    return run_command(command, f"Installing packages: {', '.join(packages)}")


def create_directories(base_path, directories):
    """
    Creates required directories under the specified base path.

    Args:
        base_path: Base directory path to create subdirectories under
        directories: List of directory paths relative to base_path

    Returns:
        True if all directories created successfully, False otherwise
    """
    logger.info(f"Creating directories under {base_path}...")
    success = True

    for directory in directories:
        full_path = os.path.join(base_path, directory)
        try:
            os.makedirs(full_path, exist_ok=True)
            logger.info(f"Created directory: {full_path}")
        except OSError as e:
            logger.error(f"Failed to create directory {full_path}: {e}")
            success = False

    return success


def create_log_directory(log_path):
    """
    Creates the BIND log directory.

    Args:
        log_path: Full path to the log directory

    Returns:
        True if directory created successfully, False otherwise
    """
    logger.info(f"Creating log directory: {log_path}")
    try:
        os.makedirs(log_path, exist_ok=True)
        return True
    except OSError as e:
        logger.error(f"Failed to create log directory {log_path}: {e}")
        return False


def copy_config_files(source_dir, dest_dir, primary_ip=None):
    """
    Copies BIND configuration files from source to destination.
    For primary installs, replaces $ip placeholder with actual IP in named.conf.acl.

    Args:
        source_dir: Source directory containing config files
        dest_dir: Destination directory for config files
        primary_ip: IP address to substitute in named.conf.acl (primary installs only)

    Returns:
        True if all files copied successfully, False otherwise
    """
    logger.info(f"Copying config files from {source_dir} to {dest_dir}...")

    if not os.path.exists(source_dir):
        logger.error(f"Source directory does not exist: {source_dir}")
        return False

    success = True

    # Walk through source directory and copy all files
    for root, dirs, files in os.walk(source_dir):
        # Calculate relative path from source_dir
        rel_path = os.path.relpath(root, source_dir)

        # Determine destination path
        if rel_path == ".":
            current_dest = dest_dir
        else:
            current_dest = os.path.join(dest_dir, rel_path)

        # Create destination subdirectories if needed
        if not os.path.exists(current_dest):
            try:
                os.makedirs(current_dest, exist_ok=True)
            except OSError as e:
                logger.error(f"Failed to create directory {current_dest}: {e}")
                success = False
                continue

        # Copy each file
        for filename in files:
            src_file = os.path.join(root, filename)
            dest_file = os.path.join(current_dest, filename)

            try:
                shutil.copy2(src_file, dest_file)
                logger.info(f"Copied: {filename} -> {dest_file}")

                # For primary installs, update named.conf.acl with the provided IP
                if primary_ip and filename == "named.conf.acl":
                    update_acl_file(dest_file, primary_ip)

            except (shutil.Error, OSError) as e:
                logger.error(f"Failed to copy {src_file} to {dest_file}: {e}")
                success = False

    return success


def update_acl_file(file_path, ip_address):
    """
    Updates the named.conf.acl file by replacing $ip placeholder with actual IP.

    Args:
        file_path: Path to the named.conf.acl file
        ip_address: IP address to substitute for $ip placeholder
    """
    logger.info(f"Updating {file_path} with IP: {ip_address}")
    try:
        with open(file_path, 'r') as f:
            content = f.read()

        # Replace $ip placeholder with actual IP address
        updated_content = content.replace('$ip', ip_address)

        with open(file_path, 'w') as f:
            f.write(updated_content)

        logger.info(f"Successfully updated named.conf.acl with IP: {ip_address}")
    except IOError as e:
        logger.error(f"Failed to update {file_path}: {e}")


def add_user_to_group(user, group):
    """
    Adds a user to a specified group.

    Args:
        user: Username to add to group
        group: Group name to add user to

    Returns:
        True if user added successfully, False otherwise
    """
    logger.info(f"Adding user '{user}' to group '{group}'...")
    command = ["usermod", "-a", "-G", group, user]
    return run_command(command, f"Adding {user} to {group} group")


def set_ownership(directories, user, group):
    """
    Sets ownership on directories and their contents recursively.

    Args:
        directories: List of directory paths to set ownership on
        user: Username for ownership
        group: Group name for ownership

    Returns:
        True if all ownership set successfully, False otherwise
    """
    logger.info(f"Setting ownership to {user}:{group}...")
    success = True

    for directory in directories:
        if os.path.exists(directory):
            command = ["chown", "-R", f"{user}:{group}", directory]
            if not run_command(command, f"Setting ownership on {directory}"):
                success = False
        else:
            logger.warning(f"Directory does not exist, skipping ownership: {directory}")

    return success


def set_permissions(directories, mode):
    """
    Sets permissions on directories.

    Args:
        directories: List of directory paths to set permissions on
        mode: Permission mode (e.g., 0o755)

    Returns:
        True if all permissions set successfully, False otherwise
    """
    logger.info(f"Setting directory permissions to {oct(mode)}...")
    success = True

    for directory in directories:
        if os.path.exists(directory):
            try:
                os.chmod(directory, mode)
                logger.info(f"Set permissions {oct(mode)} on {directory}")
            except OSError as e:
                logger.error(f"Failed to set permissions on {directory}: {e}")
                success = False
        else:
            logger.warning(f"Directory does not exist, skipping permissions: {directory}")

    return success


def set_sgid(directories):
    """
    Sets the SGID bit on directories so new files inherit the group.

    Args:
        directories: List of directory paths to set SGID on

    Returns:
        True if SGID set successfully on all directories, False otherwise
    """
    logger.info("Setting SGID bit on directories...")
    success = True

    for directory in directories:
        if os.path.exists(directory):
            try:
                # Get current permissions and add SGID bit
                current_mode = os.stat(directory).st_mode
                new_mode = current_mode | stat.S_ISGID
                os.chmod(directory, new_mode)
                logger.info(f"Set SGID bit on {directory}")
            except OSError as e:
                logger.error(f"Failed to set SGID on {directory}: {e}")
                success = False
        else:
            logger.warning(f"Directory does not exist, skipping SGID: {directory}")

    return success


def enable_and_start_service(service_name):
    """
    Enables and starts a systemd service.

    Args:
        service_name: Name of the service to enable and start

    Returns:
        True if service enabled and started successfully, False otherwise
    """
    logger.info(f"Enabling and starting {service_name} service...")

    # Enable service to start on boot
    if not run_command(["systemctl", "enable", service_name], f"Enabling {service_name}"):
        return False

    # Start the service
    if not run_command(["systemctl", "start", service_name], f"Starting {service_name}"):
        return False

    return True


def install_dns(configs_path, primary_config_dir, bind_packages, chroot_etc,
                chroot_log, etc_directories, managed_directories, dir_mode,
                bind_user, bind_group, bind_service, primary_ip=None, secondary_ip=None):
    """
    Main entry point for BIND DNS installation.
    Orchestrates the complete installation and configuration process.

    Args:
        configs_path: Path to bind-environment-configs directory
        primary_config_dir: Name of the primary config subdirectory
        bind_packages: List of packages to install
        chroot_etc: Path to chroot etc directory
        chroot_log: Path to chroot log directory
        etc_directories: List of directories to create under chroot_etc
        managed_directories: List of directories needing permissions/ownership
        dir_mode: Permission mode for directories
        bind_user: User for ownership
        bind_group: Group for ownership
        bind_service: Name of systemd service
        primary_ip: IP address for primary DNS server (mutually exclusive with secondary_ip)
        secondary_ip: IP address for secondary DNS server config lookup

    Returns:
        True if installation succeeded, False otherwise
    """
    logger.info("=" * 60)
    logger.info("Starting BIND DNS Installation")
    logger.info("=" * 60)

    # Validate that either primary or secondary IP is provided
    if not primary_ip and not secondary_ip:
        logger.error("Either --primary-ip or --secondary-ip must be specified")
        return False

    if primary_ip and secondary_ip:
        logger.error("Cannot specify both --primary-ip and --secondary-ip")
        return False

    # Step 1: Install BIND packages
    if not install_bind_packages(bind_packages):
        logger.error("Failed to install BIND packages")
        return False

    # Step 2: Create directories under /var/named/chroot/etc/
    if not create_directories(chroot_etc, etc_directories):
        logger.error("Failed to create required directories")
        return False

    # Step 3: Create log directory
    if not create_log_directory(chroot_log):
        logger.error("Failed to create log directory")
        return False

    # Step 4: Copy configuration files based on primary or secondary
    if primary_ip:
        # Primary install: copy from netbox-primary and update ACL with IP
        source_dir = os.path.join(configs_path, primary_config_dir)
        logger.info(f"Installing as PRIMARY DNS server with IP: {primary_ip}")
        if not copy_config_files(source_dir, chroot_etc, primary_ip=primary_ip):
            logger.error("Failed to copy primary configuration files")
            return False
    else:
        # Secondary install: copy from IP-named directory
        source_dir = os.path.join(configs_path, secondary_ip)
        logger.info(f"Installing as SECONDARY DNS server using config: {secondary_ip}")
        if not os.path.exists(source_dir):
            logger.error(f"Configuration directory not found for IP: {secondary_ip}")
            logger.error(f"Expected path: {source_dir}")
            return False
        if not copy_config_files(source_dir, chroot_etc):
            logger.error("Failed to copy secondary configuration files")
            return False

    # Step 5: Add netbox user to named group
    if not add_user_to_group("netbox", bind_group):
        logger.warning("Failed to add netbox user to named group - user may not exist yet")

    # Step 6: Set ownership on all managed directories
    if not set_ownership(managed_directories, bind_user, bind_group):
        logger.error("Failed to set directory ownership")
        return False

    # Step 7: Set permissions on all managed directories
    if not set_permissions(managed_directories, dir_mode):
        logger.error("Failed to set directory permissions")
        return False

    # Step 8: Set SGID bit on all managed directories
    if not set_sgid(managed_directories):
        logger.error("Failed to set SGID on directories")
        return False

    # Step 9: Enable and start the named-chroot service
    if not enable_and_start_service(bind_service):
        logger.error("Failed to enable/start BIND service")
        return False

    logger.info("=" * 60)
    logger.info("BIND DNS installation completed successfully")
    logger.info("=" * 60)

    return True
