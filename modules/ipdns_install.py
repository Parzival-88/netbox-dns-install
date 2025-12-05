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


def stop_services(services):
    """
    Stops the specified systemd services.

    Args:
        services: List of service names to stop

    Returns:
        True if all services stopped successfully, False otherwise
    """
    logger.info("Stopping NetBox services...")

    for service in services:
        logger.info(f"Stopping {service}...")
        try:
            command = ["systemctl", "stop", service]
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=False
            )

            if result.returncode == 0:
                logger.info(f"Service {service} stopped")
            else:
                # Log warning but continue - service may not be running
                logger.warning(f"Could not stop {service}: {result.stderr}")

        except subprocess.SubprocessError as e:
            logger.error(f"Failed to stop {service}: {e}")
            return False

    logger.info("All services stopped")
    return True


def start_services(services):
    """
    Starts the specified systemd services in reverse order.
    Socket should be started before the main service.

    Args:
        services: List of service names to start (will be reversed)

    Returns:
        True if all services started successfully, False otherwise
    """
    logger.info("Starting NetBox services...")

    # Start in reverse order: socket first, then main services
    start_order = ["netbox.socket", "netbox", "netbox-rqworker@1"]

    for service in start_order:
        if service in services:
            logger.info(f"Starting {service}...")
            try:
                command = ["systemctl", "start", service]
                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    check=False
                )

                if result.returncode == 0:
                    logger.info(f"Service {service} started")
                else:
                    logger.error(f"Failed to start {service}: {result.stderr}")
                    return False

            except subprocess.SubprocessError as e:
                logger.error(f"Failed to start {service}: {e}")
                return False

    logger.info("All services started")
    return True


def create_service_override(override_dir, override_content):
    """
    Creates a systemd service override file to modify service behavior.

    Args:
        override_dir: Path to the service override directory (e.g., /etc/systemd/system/netbox.service.d)
        override_content: Content to write to the override.conf file

    Returns:
        True if override created successfully, False otherwise
    """
    override_file = os.path.join(override_dir, "override.conf")

    logger.info(f"Creating systemd override: {override_file}")

    try:
        # Create override directory if it doesn't exist
        os.makedirs(override_dir, exist_ok=True)

        # Write the override file
        with open(override_file, 'w') as f:
            f.write(override_content)

        logger.info(f"Service override created: {override_file}")
        return True

    except OSError as e:
        logger.error(f"Failed to create service override: {e}")
        return False


def update_netbox_configuration(config_file, logging_config, plugins_list, plugins_config):
    """
    Updates the NetBox configuration.py file with IPDNS logging and plugin settings.

    Args:
        config_file: Path to the NetBox configuration.py file
        logging_config: JSON string for LOGGING configuration
        plugins_list: JSON string for PLUGINS list
        plugins_config: JSON string for PLUGINS_CONFIG

    Returns:
        True if configuration updated successfully, False otherwise
    """
    logger.info(f"Updating NetBox configuration: {config_file}")

    try:
        # Read the current configuration file
        with open(config_file, 'r') as f:
            content = f.read()

        # Replace LOGGING configuration (handles single or multi-line assignments)
        # Matches from LOGGING = to closing ) with optional whitespace/newlines
        content = re.sub(
            r'^LOGGING\s*=\s*json\.loads\(r?[\'\"]{1,3}.*?[\'\"]{1,3}\s*\)',
            f"LOGGING = json.loads(r'''{logging_config}''')",
            content,
            flags=re.MULTILINE | re.DOTALL
        )

        # Replace PLUGINS configuration (handles single or multi-line assignments)
        # Use word boundary to avoid matching PLUGINS_CONFIG
        content = re.sub(
            r'^PLUGINS\s*=\s*json\.loads\(r?[\'\"]{1,3}.*?[\'\"]{1,3}\s*\)(?=\s*\n)',
            f"PLUGINS = json.loads(r'''{plugins_list}''')",
            content,
            flags=re.MULTILINE | re.DOTALL
        )

        # Replace PLUGINS_CONFIG configuration (handles single or multi-line assignments)
        content = re.sub(
            r'^PLUGINS_CONFIG\s*=\s*json\.loads\(r?[\'\"]{1,3}.*?[\'\"]{1,3}\s*\)',
            f"PLUGINS_CONFIG = json.loads(r'''{plugins_config}''')",
            content,
            flags=re.MULTILINE | re.DOTALL
        )

        # Ensure json import exists at the top of the file
        if 'import json' not in content:
            # Add import after the first line or at the beginning
            if content.startswith('#'):
                # Find end of initial comments/docstrings
                lines = content.split('\n')
                insert_idx = 0
                for i, line in enumerate(lines):
                    if line and not line.startswith('#'):
                        insert_idx = i
                        break
                lines.insert(insert_idx, 'import json')
                content = '\n'.join(lines)
            else:
                content = 'import json\n' + content

        # Write the updated configuration
        with open(config_file, 'w') as f:
            f.write(content)

        logger.info("NetBox configuration updated successfully")
        return True

    except (OSError, IOError) as e:
        logger.error(f"Failed to update NetBox configuration: {e}")
        return False


def run_migrations(python_path, manage_py):
    """
    Runs Django migrations for netbox_ipdns plugin.

    Args:
        python_path: Path to the Python executable in the virtual environment
        manage_py: Path to the Django manage.py script

    Returns:
        True if migrations ran successfully, False otherwise
    """
    logger.info("Running database migrations for netbox_ipdns...")

    try:
        command = [python_path, manage_py, "migrate", "netbox_ipdns", "--no-input"]
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False
        )

        if result.returncode == 0:
            logger.info("Migrations completed successfully")
            if result.stdout:
                logger.debug(result.stdout)
            return True
        else:
            logger.error(f"Migrations failed: {result.stderr}")
            return False

    except subprocess.SubprocessError as e:
        logger.error(f"Failed to run migrations: {e}")
        return False


def run_collectstatic(python_path, manage_py):
    """
    Runs Django collectstatic command to gather static files.

    Args:
        python_path: Path to the Python executable in the virtual environment
        manage_py: Path to the Django manage.py script

    Returns:
        True if collectstatic ran successfully, False otherwise
    """
    logger.info("Running collectstatic...")

    try:
        command = [python_path, manage_py, "collectstatic", "--clear", "--no-input"]
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False
        )

        if result.returncode == 0:
            logger.info("Collectstatic completed successfully")
            if result.stdout:
                logger.debug(result.stdout)
            return True
        else:
            logger.error(f"Collectstatic failed: {result.stderr}")
            return False

    except subprocess.SubprocessError as e:
        logger.error(f"Failed to run collectstatic: {e}")
        return False


def create_sudoers_file(sudoers_file, sudoers_content):
    """
    Creates a sudoers file with proper permissions for DNS script execution.

    Args:
        sudoers_file: Path to the sudoers file to create
        sudoers_content: Content to write to the sudoers file

    Returns:
        True if sudoers file created successfully, False otherwise
    """
    logger.info(f"Creating sudoers file: {sudoers_file}")

    try:
        # Write the sudoers file
        with open(sudoers_file, 'w') as f:
            f.write(sudoers_content)

        # Set proper permissions (0440 - read only for root and root group)
        os.chmod(sudoers_file, 0o440)

        logger.info(f"Sudoers file created with permissions 0440: {sudoers_file}")
        return True

    except OSError as e:
        logger.error(f"Failed to create sudoers file: {e}")
        return False


def reload_systemd():
    """
    Reloads the systemd daemon to apply service override changes.

    Returns:
        True if reload succeeded, False otherwise
    """
    logger.info("Reloading systemd daemon")

    try:
        command = ["systemctl", "daemon-reload"]
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False
        )

        if result.returncode == 0:
            logger.info("Systemd daemon reloaded successfully")
            return True
        else:
            logger.error(f"Failed to reload systemd daemon: {result.stderr}")
            return False

    except subprocess.SubprocessError as e:
        logger.error(f"Failed to execute systemctl daemon-reload: {e}")
        return False


def create_shared_directory(shared_dir, user, group, mode):
    """
    Creates the IPDNS shared directory with proper ownership and permissions.

    Args:
        shared_dir: Path to the shared directory to create
        user: Username for ownership
        group: Group name for ownership
        mode: Permission mode (e.g., 0o755)

    Returns:
        True if directory created and configured successfully, False otherwise
    """
    import stat

    logger.info(f"Creating shared directory: {shared_dir}")

    try:
        # Create directory and parent directories
        os.makedirs(shared_dir, exist_ok=True)
        logger.info(f"Directory created: {shared_dir}")

        # Set ownership
        command = ["chown", f"{user}:{group}", shared_dir]
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False
        )

        if result.returncode != 0:
            logger.error(f"Failed to set ownership: {result.stderr}")
            return False

        logger.info(f"Ownership set to {user}:{group}")

        # Set base permissions
        os.chmod(shared_dir, mode)

        # Add SGID bit so new files inherit the group
        current_mode = os.stat(shared_dir).st_mode
        new_mode = current_mode | stat.S_ISGID
        os.chmod(shared_dir, new_mode)

        logger.info(f"Permissions set to {oct(mode)} with SGID")
        return True

    except OSError as e:
        logger.error(f"Failed to create shared directory: {e}")
        return False
    except subprocess.SubprocessError as e:
        logger.error(f"Failed to set ownership: {e}")
        return False


def create_log_directory(log_dir, log_file, user, group, mode):
    """
    Creates or configures the log directory and creates an empty log file.
    If the directory exists, only sets permissions and ownership.
    Creates an empty log file owned by the specified user/group.

    Args:
        log_dir: Path to the log directory
        log_file: Path to the log file to create
        user: Username for ownership
        group: Group name for ownership
        mode: Permission mode (e.g., 0o755)

    Returns:
        True if directory and file configured successfully, False otherwise
    """
    import stat

    logger.info(f"Configuring log directory: {log_dir}")

    try:
        # Check if directory exists
        if os.path.exists(log_dir):
            logger.info(f"Log directory already exists: {log_dir}")
        else:
            # Create directory if it doesn't exist
            os.makedirs(log_dir, exist_ok=True)
            logger.info(f"Created log directory: {log_dir}")

        # Set ownership on the directory
        command = ["chown", f"{user}:{group}", log_dir]
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False
        )

        if result.returncode != 0:
            logger.error(f"Failed to set ownership on log directory: {result.stderr}")
            return False

        logger.info(f"Log directory ownership set to {user}:{group}")

        # Set base permissions
        os.chmod(log_dir, mode)

        # Add SGID bit so new files inherit the group
        current_mode = os.stat(log_dir).st_mode
        new_mode = current_mode | stat.S_ISGID
        os.chmod(log_dir, new_mode)

        logger.info(f"Log directory permissions set to {oct(mode)} with SGID")

        # Create empty log file if it doesn't exist
        if not os.path.exists(log_file):
            # Create empty file
            with open(log_file, 'w') as f:
                pass
            logger.info(f"Created empty log file: {log_file}")
        else:
            logger.info(f"Log file already exists: {log_file}")

        # Set ownership on the log file
        command = ["chown", f"{user}:{group}", log_file]
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False
        )

        if result.returncode != 0:
            logger.error(f"Failed to set ownership on log file: {result.stderr}")
            return False

        logger.info(f"Log file ownership set to {user}:{group}")

        return True

    except OSError as e:
        logger.error(f"Failed to configure log directory: {e}")
        return False
    except subprocess.SubprocessError as e:
        logger.error(f"Failed to set ownership: {e}")
        return False


def set_directory_ownership(directory, user, group, recursive=True):
    """
    Sets ownership on a directory and optionally its contents recursively.

    Args:
        directory: Path to the directory
        user: Username for ownership
        group: Group name for ownership
        recursive: If True, apply ownership recursively to all contents

    Returns:
        True if ownership set successfully, False otherwise
    """
    logger.info(f"Setting ownership on {directory} to {user}:{group}")

    try:
        if recursive:
            command = ["chown", "-R", f"{user}:{group}", directory]
        else:
            command = ["chown", f"{user}:{group}", directory]

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False
        )

        if result.returncode != 0:
            logger.error(f"Failed to set ownership: {result.stderr}")
            return False

        logger.info(f"Ownership set to {user}:{group} on {directory}")
        return True

    except subprocess.SubprocessError as e:
        logger.error(f"Failed to set ownership: {e}")
        return False


def pip_install_plugin(pip_path, plugin_path):
    """
    Installs a plugin in editable mode using pip install -e.

    Args:
        pip_path: Path to the pip executable in the virtual environment
        plugin_path: Path to the plugin directory to install

    Returns:
        True if installation succeeded, False otherwise
    """
    logger.info(f"Installing plugin from {plugin_path} using pip install -e")

    try:
        command = [pip_path, "install", "-e", plugin_path]
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False
        )

        if result.returncode == 0:
            logger.info("Plugin installed successfully")
            if result.stdout:
                logger.debug(result.stdout)
            return True
        else:
            logger.error(f"pip install failed: {result.stderr}")
            return False

    except subprocess.SubprocessError as e:
        logger.error(f"Failed to run pip install: {e}")
        return False


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


def install_ipdns(repo_url, plugins_path, ipdns_config, shared_dir, dir_mode, user, group,
                  netbox_override_dir, rqworker_override_dir, service_override_content,
                  sudoers_file, sudoers_content, services, netbox_config_file,
                  logging_config, plugins_list, plugins_config_settings,
                  python_path, manage_py, log_dir, log_file, pip_path):
    """
    Main entry point for netbox-ipdns plugin installation.
    Stops services, clones the plugin repository, configures global_variables.py,
    creates shared directory, sets up systemd overrides, configures sudoers permissions,
    updates NetBox configuration, runs migrations, and starts services.

    Args:
        repo_url: SSH URL of the netbox-ipdns repository
        plugins_path: Path to the NetBox plugins directory
        ipdns_config: Dictionary containing configuration values
        shared_dir: Path to the shared directory to create
        dir_mode: Permission mode for the shared directory
        user: Username for shared directory ownership
        group: Group name for shared directory ownership
        netbox_override_dir: Path to netbox service override directory
        rqworker_override_dir: Path to netbox-rqworker service override directory
        service_override_content: Content for the systemd override files
        sudoers_file: Path to the sudoers file to create
        sudoers_content: Content for the sudoers file
        services: List of NetBox services to stop/start
        netbox_config_file: Path to NetBox configuration.py
        logging_config: JSON string for LOGGING configuration
        plugins_list: JSON string for PLUGINS list
        plugins_config_settings: JSON string for PLUGINS_CONFIG
        python_path: Path to the Python executable
        manage_py: Path to Django manage.py
        log_dir: Path to the log directory for netbox-ipdns
        log_file: Path to the log file for netbox-ipdns
        pip_path: Path to the pip executable in the virtual environment

    Returns:
        True if installation succeeded, False otherwise
    """
    logger.info("=" * 60)
    logger.info("Starting netbox-ipdns Plugin Installation")
    logger.info("=" * 60)

    # Create plugins directory if it doesn't exist
    if not os.path.exists(plugins_path):
        logger.info(f"Plugins directory does not exist, creating: {plugins_path}")
        if not create_shared_directory(plugins_path, user, group, dir_mode):
            logger.error("Failed to create plugins directory")
            return False
    else:
        logger.info(f"Plugins directory exists: {plugins_path}")

    # Stop NetBox services before making changes
    if not stop_services(services):
        logger.error("Failed to stop NetBox services")
        return False

    # Create shared directory with proper ownership and permissions
    if not create_shared_directory(shared_dir, user, group, dir_mode):
        logger.error("Failed to create shared directory")
        return False

    # Create logs subdirectory under shared directory
    logs_subdir = os.path.join(shared_dir, "logs")
    if not create_shared_directory(logs_subdir, user, group, dir_mode):
        logger.error("Failed to create logs subdirectory")
        return False

    # Create or configure log directory and log file
    if not create_log_directory(log_dir, log_file, user, group, dir_mode):
        logger.error("Failed to configure log directory")
        return False

    # Clone the repository
    if not clone_repository(repo_url, plugins_path):
        logger.error("Failed to clone netbox-ipdns repository")
        return False

    # Set ownership on cloned netbox-ipdns directory recursively
    ipdns_dir = os.path.join(plugins_path, "netbox-ipdns")
    if not set_directory_ownership(ipdns_dir, user, group, recursive=True):
        logger.error("Failed to set ownership on netbox-ipdns directory")
        return False

    # Install the plugin using pip install -e
    if not pip_install_plugin(pip_path, ipdns_dir):
        logger.error("Failed to install netbox-ipdns plugin via pip")
        return False

    # Copy global_variables.example.py to global_variables.py
    if not copy_global_variables(plugins_path):
        logger.error("Failed to copy global_variables file")
        return False

    # Configure global_variables.py with environment values
    if not configure_global_variables(plugins_path, ipdns_config):
        logger.error("Failed to configure global_variables.py")
        return False

    # Create systemd override for netbox service
    if not create_service_override(netbox_override_dir, service_override_content):
        logger.error("Failed to create netbox service override")
        return False

    # Create systemd override for netbox-rqworker service
    if not create_service_override(rqworker_override_dir, service_override_content):
        logger.error("Failed to create netbox-rqworker service override")
        return False

    # Reload systemd to apply override changes
    if not reload_systemd():
        logger.error("Failed to reload systemd daemon")
        return False

    # Create sudoers file for DNS script permissions
    if not create_sudoers_file(sudoers_file, sudoers_content):
        logger.error("Failed to create sudoers file")
        return False

    # Update NetBox configuration.py with IPDNS settings
    if not update_netbox_configuration(netbox_config_file, logging_config,
                                        plugins_list, plugins_config_settings):
        logger.error("Failed to update NetBox configuration")
        return False

    # Run database migrations for netbox_ipdns
    if not run_migrations(python_path, manage_py):
        logger.error("Failed to run database migrations")
        return False

    # Run collectstatic to gather static files
    if not run_collectstatic(python_path, manage_py):
        logger.error("Failed to run collectstatic")
        return False

    # Start NetBox services after installation
    if not start_services(services):
        logger.error("Failed to start NetBox services")
        return False

    logger.info("=" * 60)
    logger.info("netbox-ipdns plugin installation completed successfully")
    logger.info("=" * 60)

    return True
