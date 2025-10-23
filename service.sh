#!/bin/bash

# Photo Frame Service Management Script
# Usage: ./service.sh [start|stop|restart|status|logs|install|uninstall]

SERVICE_NAME="photo-frame"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"

case "$1" in
    start)
        echo "Starting photo frame service..."
        sudo systemctl start $SERVICE_NAME
        ;;
    stop)
        echo "Stopping photo frame service..."
        sudo systemctl stop $SERVICE_NAME
        ;;
    restart)
        echo "Restarting photo frame service..."
        sudo systemctl restart $SERVICE_NAME
        ;;
    status)
        sudo systemctl status $SERVICE_NAME
        ;;
    logs)
        echo "Showing service logs (press Ctrl+C to exit)..."
        sudo journalctl -u $SERVICE_NAME -f
        ;;
    enable)
        echo "Enabling service for auto-start..."
        sudo systemctl enable $SERVICE_NAME
        ;;
    disable)
        echo "Disabling service auto-start..."
        sudo systemctl disable $SERVICE_NAME
        ;;
    install)
        echo "Installing systemd service..."
        if [ -f "$SERVICE_FILE" ]; then
            echo "Service already exists. Use 'restart' to reload."
        else
            echo "Run ./install.sh to install the complete system"
        fi
        ;;
    uninstall)
        echo "Uninstalling service..."
        sudo systemctl stop $SERVICE_NAME 2>/dev/null || true
        sudo systemctl disable $SERVICE_NAME 2>/dev/null || true
        sudo rm -f $SERVICE_FILE
        sudo systemctl daemon-reload
        echo "Service uninstalled"
        ;;
    test)
        echo "Testing photo frame components..."
        echo "1. Testing display manager..."
        if [ -d "venv" ]; then
            source venv/bin/activate
            cd display && python3 display_manager.py test
            deactivate
        else
            cd display && python3 display_manager.py test
        fi
        echo "2. Testing web server..."
        if curl -s http://localhost:3000/api/status > /dev/null; then
            echo "✓ Web server is running"
        else
            echo "✗ Web server is not responding"
        fi
        ;;
    *)
        echo "Photo Frame Service Management"
        echo "Usage: $0 {start|stop|restart|status|logs|enable|disable|install|uninstall|test}"
        echo ""
        echo "Commands:"
        echo "  start      - Start the service"
        echo "  stop       - Stop the service" 
        echo "  restart    - Restart the service"
        echo "  status     - Show service status"
        echo "  logs       - Show live logs"
        echo "  enable     - Enable auto-start on boot"
        echo "  disable    - Disable auto-start"
        echo "  install    - Install service (use install.sh instead)"
        echo "  uninstall  - Remove service"
        echo "  test       - Test system components"
        exit 1
        ;;
esac