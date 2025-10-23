#!/bin/bash

# Minimal Digital Photo Frame Installation Script
set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() { echo -e "${GREEN}[INFO]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

# Core dependencies only
install_dependencies() {
    log "Installing minimal dependencies..."
    sudo apt update
    sudo apt install -y git python3-pip curl
}

# Install Node.js runtime (Bun preferred, Node.js fallback)
install_runtime() {
    log "Installing JavaScript runtime..."

    # Check if Bun is already installed
    if command -v bun &>/dev/null; then
        log "Bun already installed at $(which bun)"
        return
    fi

    # Check if Node.js is already installed
    if command -v node &>/dev/null; then
        log "Node.js already installed at $(which node)"
        return
    fi

    # Install Bun from official script
    log "Installing Bun runtime..."
    curl -fsSL https://bun.sh/install | bash

    # Update PATH for current session
    export BUN_INSTALL="$HOME/.bun"
    export PATH="$BUN_INSTALL/bin:$PATH"

    # Verify Bun installation
    if command -v bun &>/dev/null; then
        log "Bun installed successfully at $(which bun)"
    else
        warn "Bun installation failed, falling back to Node.js..."
        sudo apt install -y nodejs npm
    fi
}

# Install project dependencies
install_project_deps() {
    log "Installing project dependencies..."

    # Python dependencies (if display dir exists)
    if [ -d "display" ] && [ -f "display/requirements.txt" ]; then
        log "Setting up Python dependencies..."

        # Create virtual environment (PEP 668 compliant)
        python3 -m venv venv
        source venv/bin/activate

        # Upgrade pip in venv
        python3 -m pip install --upgrade pip

        # Install requirements in venv
        pip install -r display/requirements.txt

        # Deactivate venv (service will activate it)
        deactivate
    fi

    # Node.js dependencies
    if [ -f "package.json" ]; then
        if command -v bun &>/dev/null; then
            bun install
        else
            npm install
        fi
    fi
}

# Setup minimal directories
setup_directories() {
    log "Creating directories..."
    mkdir -p uploads storage/config
    chmod 755 uploads storage 2>/dev/null || true
}

# Create systemd service
create_service() {
    log "Setting up systemd service..."

    local runtime_cmd
    local runtime_path
    local venv_activate=""

    # Determine which runtime to use
    if command -v bun &>/dev/null; then
        runtime_path=$(which bun)
        runtime_cmd="bun start"
    elif command -v node &>/dev/null; then
        runtime_path=$(which node)
        runtime_cmd="npm start"
    else
        error "Neither Bun nor Node.js found. Please run install_runtime() first."
    fi

    # If venv was created, activate it in the service
    if [ -d "venv" ]; then
        venv_activate="source venv/bin/activate && "
    fi

    log "Using runtime: $runtime_path"
    log "Command: ${venv_activate}${runtime_cmd}"

    sudo tee /etc/systemd/system/photo-frame.service > /dev/null << EOF
[Unit]
Description=Photo Frame Server
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
Environment=NODE_ENV=production
Environment=PORT=3000
Environment=PATH=/root/.bun/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
ExecStart=/bin/bash -c '${venv_activate}${runtime_cmd}'
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl daemon-reload
    sudo systemctl enable photo-frame.service
    log "Service created and enabled"
}

# Main
main() {
    log "Starting minimal Photo Frame installation"
    read -p "Continue? (y/N): " -n 1 -r; echo
    [[ ! $REPLY =~ ^[Yy]$ ]] && exit 0

    install_dependencies
    install_runtime
    install_project_deps
    setup_directories
    create_service

    log "Installation complete!"
    echo -e "${GREEN}Next steps:${NC}"
    echo "1. Start service: ${BLUE}sudo systemctl start photo-frame.service${NC}"
    echo "2. Check status: ${BLUE}sudo systemctl status photo-frame.service${NC}"
    echo "3. View logs: ${BLUE}sudo journalctl -u photo-frame.service -f${NC}"
}

exec > >(tee -a installation.log) 2>&1
main "$@"