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

# Install Node.js runtime (choose one)
install_runtime() {
    log "Installing JavaScript runtime..."
    if command -v bun &>/dev/null; then
        log "Bun already installed"
    elif command -v node &>/dev/null; then
        log "Node.js already installed"
    else
        warn "Installing Node.js (fallback)..."
        sudo apt install -y nodejs npm
    fi
}

# Install project dependencies
install_project_deps() {
    log "Installing project dependencies..."

    # Python dependencies (if display dir exists)
    if [ -d "display" ] && [ -f "display/requirements.txt" ]; then
        log "Setting up Python dependencies..."
        python3 -m pip install --upgrade pip
        pip install -r display/requirements.txt
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

    local cmd
    if command -v bun &>/dev/null; then
        cmd="bun start"
    else
        cmd="npm start"
    fi

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
ExecStart=$cmd
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl daemon-reload
    sudo systemctl enable photo-frame.service
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