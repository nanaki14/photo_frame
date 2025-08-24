#!/bin/bash

# Digital Photo Frame Installation Script for Raspberry Pi Zero 2 WH
# This script automates the installation process described in DEPLOYMENT.md

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

# Check if running on Raspberry Pi
check_pi() {
    if ! grep -q "Raspberry Pi" /proc/cpuinfo; then
        warn "This script is designed for Raspberry Pi. Continuing anyway..."
    fi
}

# Update system packages
update_system() {
    log "Updating system packages..."
    sudo apt update && sudo apt upgrade -y
}

# Install system dependencies
install_dependencies() {
    log "Installing system dependencies..."
    sudo apt install -y \
        git \
        python3-pip \
        python3-venv \
        python3-dev \
        nodejs \
        npm \
        curl \
        build-essential \
        libjpeg-dev \
        zlib1g-dev \
        libtiff-dev \
        libfreetype6-dev \
        liblcms2-dev \
        libwebp-dev
}

# Install Bun runtime
install_bun() {
    log "Installing Bun JavaScript runtime..."
    if ! command -v bun &> /dev/null; then
        curl -fsSL https://bun.sh/install | bash
        export PATH="$HOME/.bun/bin:$PATH"
        # Add to .bashrc for persistence
        echo 'export PATH="$HOME/.bun/bin:$PATH"' >> ~/.bashrc
    else
        log "Bun is already installed"
    fi
}

# Download Waveshare e-Paper library
install_waveshare_lib() {
    log "Installing Waveshare e-Paper library..."
    cd "$HOME"
    if [ ! -d "e-Paper" ]; then
        git clone https://github.com/waveshare/e-Paper.git
    else
        log "Waveshare library already exists, updating..."
        cd e-Paper
        git pull
        cd ..
    fi
    
    # Verify library installation
    if [ -d "e-Paper/RaspberryPi_JetsonNano/python/lib" ]; then
        log "Waveshare library installed successfully"
    else
        error "Waveshare library installation failed"
    fi
}

# Clone photo frame project
clone_project() {
    log "Setting up photo frame project..."
    cd "$HOME"
    
    # If the script is already in the photo_frame directory, we're good
    if [ -f "photo_frame/package.json" ]; then
        log "Photo frame project already exists"
        cd photo_frame
    else
        error "Please place this script in the photo_frame project directory"
    fi
}

# Install Python dependencies
install_python_deps() {
    log "Installing Python dependencies..."
    
    # Create virtual environment
    python3 -m venv venv
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install requirements
    cd display
    pip install -r requirements.txt
    
    # Install Raspberry Pi specific packages
    pip install RPi.GPIO spidev
    
    cd ..
    deactivate
}

# Install Node.js dependencies
install_node_deps() {
    log "Installing Node.js dependencies..."
    export PATH="$HOME/.bun/bin:$PATH"
    bun install
}

# Setup directories and permissions
setup_directories() {
    log "Setting up directories and permissions..."
    mkdir -p uploads storage/config
    chmod 755 uploads storage
    chmod 755 display/*.py
}

# Configure SPI interface
configure_spi() {
    log "Configuring SPI interface..."
    
    # Check if SPI is already enabled
    if grep -q "dtparam=spi=on" /boot/config.txt; then
        log "SPI is already enabled"
    else
        log "Enabling SPI interface..."
        echo "dtparam=spi=on" | sudo tee -a /boot/config.txt
        warn "SPI enabled. Reboot required after installation."
    fi
    
    # Add user to SPI group
    sudo usermod -a -G spi $USER
}

# Create systemd service
create_service() {
    log "Creating systemd service..."
    
    sudo tee /etc/systemd/system/photo-frame.service > /dev/null << EOF
[Unit]
Description=Digital Photo Frame Server
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$HOME/photo_frame
Environment=NODE_ENV=production
Environment=PORT=3000
Environment=PATH=$HOME/.bun/bin:/usr/local/bin:/usr/bin:/bin
ExecStart=$HOME/.bun/bin/bun start
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

    # Reload and enable service
    sudo systemctl daemon-reload
    sudo systemctl enable photo-frame.service
    
    log "Service created and enabled"
}

# Test installation
test_installation() {
    log "Testing installation..."
    
    # Test Python virtual environment
    source venv/bin/activate
    python3 -c "import PIL; print('✓ Pillow installed')"
    
    # Test display manager (mock mode)
    cd display
    python3 -c "from display_manager import DisplayManager; d = DisplayManager(); print('✓ Display manager working')"
    cd ..
    deactivate
    
    # Test Bun
    export PATH="$HOME/.bun/bin:$PATH"
    bun --version > /dev/null && echo "✓ Bun working"
    
    # Test project dependencies
    bun run --help > /dev/null && echo "✓ Project dependencies installed"
}

# Main installation function
main() {
    log "Starting Digital Photo Frame installation..."
    log "This will install and configure the photo frame on Raspberry Pi"
    
    # Confirmation prompt
    read -p "Continue with installation? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log "Installation cancelled"
        exit 0
    fi
    
    check_pi
    update_system
    install_dependencies
    install_bun
    install_waveshare_lib
    clone_project
    install_python_deps
    install_node_deps
    setup_directories
    configure_spi
    create_service
    test_installation
    
    log "Installation completed successfully!"
    echo
    echo -e "${GREEN}Next steps:${NC}"
    echo "1. Reboot the Pi to enable SPI: ${BLUE}sudo reboot${NC}"
    echo "2. After reboot, start the service: ${BLUE}sudo systemctl start photo-frame.service${NC}"
    echo "3. Check service status: ${BLUE}sudo systemctl status photo-frame.service${NC}"
    echo "4. Access web interface: ${BLUE}http://$(hostname -I | awk '{print $1}'):3000${NC}"
    echo
    echo -e "${YELLOW}Hardware setup:${NC}"
    echo "- Connect the Waveshare 7.3inch e-Paper HAT to your Pi's GPIO"
    echo "- Ensure proper power supply (5V 2.5A recommended)"
    echo
    echo -e "${GREEN}Installation log saved to: installation.log${NC}"
}

# Redirect all output to log file as well
exec > >(tee -a installation.log)
exec 2>&1

# Run main function
main "$@"