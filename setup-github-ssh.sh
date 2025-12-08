#!/bin/bash
# Generates SSH key for GitHub access and configures SSH client.
# Creates an ed25519 key pair and adds github.ibm.com to SSH config.

# Validate command line argument
if [ -z "$1" ]; then
    echo "Usage: $0 <ip-address>"
    echo "Example: $0 9.11.227.25"
    exit 1
fi

IP_ADDRESS="$1"
KEY_NAME="netbox-dns-install-${IP_ADDRESS}"
KEY_PATH="${HOME}/.ssh/${KEY_NAME}"
SSH_CONFIG="${HOME}/.ssh/config"

# Create .ssh directory if it doesn't exist
if [ ! -d "${HOME}/.ssh" ]; then
    echo "Creating ~/.ssh directory..."
    mkdir -p "${HOME}/.ssh"
    chmod 700 "${HOME}/.ssh"
fi

# Check if key already exists
if [ -f "${KEY_PATH}" ]; then
    echo "Warning: Key already exists at ${KEY_PATH}"
    read -p "Overwrite? (y/N): " confirm
    if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
        echo "Aborted."
        exit 1
    fi
fi

# Generate the SSH key pair
echo "Generating SSH key: ${KEY_PATH}"
ssh-keygen -t ed25519 -C "secondary-${IP_ADDRESS}" -f "${KEY_PATH}" -N ""

if [ $? -ne 0 ]; then
    echo "Error: Failed to generate SSH key"
    exit 1
fi

# Check if github.ibm.com entry already exists in SSH config
if [ -f "${SSH_CONFIG}" ] && grep -q "Host github.ibm.com" "${SSH_CONFIG}"; then
    echo "Warning: github.ibm.com entry already exists in ${SSH_CONFIG}"
    echo "You may need to manually update the IdentityFile path."
else
    # Append github.ibm.com configuration to SSH config
    echo "Updating SSH config: ${SSH_CONFIG}"
    cat >> "${SSH_CONFIG}" << EOF

# GitHub IBM - added for netbox-dns-install
Host github.ibm.com
    HostName github.ibm.com
    User git
    IdentityFile ${KEY_PATH}
    IdentitiesOnly yes
EOF
    chmod 600 "${SSH_CONFIG}"
fi

# Display the public key for copy/paste
echo ""
echo "========================================"
echo "Done! Copy the following public key to GitHub:"
echo "========================================"
echo ""
cat "${KEY_PATH}.pub"
echo ""
