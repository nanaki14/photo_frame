# Raspberry Pi Deployment Guide

## Digital Photo Frame for Waveshare 7.3inch e-ink Display

This guide provides step-by-step instructions for deploying the digital photo frame on a Raspberry Pi Zero 2 WH with Waveshare 7.3inch e-ink display.

## Hardware Requirements

- **Raspberry Pi Zero 2 WH** (recommended)
- **Waveshare 7.3inch e-Paper HAT** (800×480 resolution)
- **MicroSD Card** (16GB or larger, Class 10 recommended)
- **Power Supply** (5V 2.5A recommended for stable operation)
- **Internet Connection** (WiFi or Ethernet adapter)

## Prerequisites

### 1. Raspberry Pi OS Setup

Install Raspberry Pi OS Lite (headless setup recommended):

```bash
# Flash Raspberry Pi OS Lite to SD card using Raspberry Pi Imager
# Enable SSH and configure WiFi during imaging process
```

### 2. Initial Pi Configuration

```bash
# SSH into your Pi
ssh pi@raspberrypi.local

# Update system
sudo apt update && sudo apt upgrade -y

# Enable SPI interface (required for e-ink display)
sudo raspi-config
# Navigate to: Interface Options → SPI → Yes

# Reboot to apply changes
sudo reboot
```

## Installation Steps

### 1. Install System Dependencies

```bash
# Install required system packages
sudo apt install -y git python3-pip python3-venv nodejs npm curl

# Install Bun JavaScript runtime
curl -fsSL https://bun.sh/install | bash
source ~/.bashrc
```

### 2. Download Waveshare e-Paper Library

```bash
# Clone Waveshare e-Paper library
cd /home/pi
git clone https://github.com/waveshare/e-Paper.git

# Verify the library path (should contain RaspberryPi_JetsonNano/python/)
ls -la e-Paper/RaspberryPi_JetsonNano/python/
```

### 3. Clone Photo Frame Project

```bash
# Clone your photo frame project
cd /home/pi
git clone <your-photo-frame-repo> photo_frame
cd photo_frame
```

### 4. Install Python Dependencies

```bash
# Create virtual environment for Python dependencies
python3 -m venv venv
source venv/bin/activate

# Install Python requirements
pip install -r display/requirements.txt

# Install additional Pi-specific packages
pip install RPi.GPIO spidev

# Test display manager
cd display
python3 display_manager.py test
```

### 5. Install Node.js Dependencies

```bash
# Install JavaScript dependencies
cd /home/pi/photo_frame
bun install
```

### 6. Configure Environment

```bash
# Create uploads directory
mkdir -p uploads storage/config

# Set proper permissions
chmod 755 uploads storage
```

### 7. Update Display Manager Path

Edit `src/server/app.ts` to use the correct Waveshare library path:

```typescript
// Update the DISPLAY_SCRIPT path if needed
const DISPLAY_SCRIPT = path.join(process.cwd(), 'display', 'update_display.py');
```

Update `display/display_manager.py` to use the correct Waveshare library path:

```python
# Update the path to point to your Waveshare installation
sys.path.append('/home/pi/e-Paper/RaspberryPi_JetsonNano/python/lib')
```

## Production Deployment

### 1. Create Systemd Service

Create service file for auto-start:

```bash
sudo nano /etc/systemd/system/photo-frame.service
```

Add the following content:

```ini
[Unit]
Description=Digital Photo Frame Server
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/photo_frame
Environment=NODE_ENV=production
Environment=PORT=3000
ExecStart=/home/pi/.bun/bin/bun start
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### 2. Enable and Start Service

```bash
# Reload systemd and enable service
sudo systemctl daemon-reload
sudo systemctl enable photo-frame.service
sudo systemctl start photo-frame.service

# Check service status
sudo systemctl status photo-frame.service
```

### 3. Configure Firewall (Optional)

```bash
# Install and configure UFW
sudo apt install ufw
sudo ufw allow ssh
sudo ufw allow 3000
sudo ufw --force enable
```

## Testing Deployment

### 1. Test Web Interface

```bash
# Test from Pi
curl http://localhost:3000/api/status

# Test from another device on same network
curl http://<pi-ip-address>:3000/api/status
```

### 2. Test Display Functionality

```bash
# Test display directly
cd /home/pi/photo_frame/display
python3 display_manager.py test

# Test complete workflow
curl -X POST -F "photo=@test_image.jpg" http://localhost:3000/api/photo
```

## Troubleshooting

### Common Issues

1. **SPI Permission Error**
   ```bash
   # Add pi user to spi group
   sudo usermod -a -G spi pi
   sudo reboot
   ```

2. **Display Not Working**
   ```bash
   # Check SPI is enabled
   lsmod | grep spi
   
   # Verify connections
   # Check Waveshare documentation for proper wiring
   ```

3. **Memory Issues on Pi Zero**
   ```bash
   # Increase swap file
   sudo dphys-swapfile swapoff
   sudo nano /etc/dphys-swapfile
   # Set CONF_SWAPSIZE=512
   sudo dphys-swapfile setup
   sudo dphys-swapfile swapon
   ```

4. **Service Won't Start**
   ```bash
   # Check logs
   sudo journalctl -u photo-frame.service -f
   
   # Check Bun installation
   /home/pi/.bun/bin/bun --version
   ```

### Performance Optimization

1. **Reduce Memory Usage**
   ```bash
   # Disable unnecessary services
   sudo systemctl disable bluetooth
   sudo systemctl disable cups
   sudo systemctl disable avahi-daemon
   ```

2. **GPU Memory Split**
   ```bash
   # Reduce GPU memory (we don't need graphics)
   sudo raspi-config
   # Advanced Options → Memory Split → 16
   ```

## Network Configuration

### WiFi Setup

Edit `/etc/wpa_supplicant/wpa_supplicant.conf`:

```
network={
    ssid="YourNetworkName"
    psk="YourPassword"
}
```

### Static IP (Optional)

Edit `/etc/dhcpcd.conf`:

```
interface wlan0
static ip_address=192.168.1.100/24
static routers=192.168.1.1
static domain_name_servers=8.8.8.8
```

## Maintenance

### Regular Updates

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Update photo frame code
cd /home/pi/photo_frame
git pull

# Restart service
sudo systemctl restart photo-frame.service
```

### Log Management

```bash
# View service logs
sudo journalctl -u photo-frame.service --since "1 hour ago"

# View display logs
tail -f /tmp/display_manager.log
tail -f /tmp/update_display.log
```

### Backup Configuration

```bash
# Backup important files
tar -czf photo_frame_backup.tar.gz \
  /home/pi/photo_frame/uploads \
  /home/pi/photo_frame/storage \
  /etc/systemd/system/photo-frame.service
```

## Security Considerations

1. **Change Default Password**
   ```bash
   passwd
   ```

2. **SSH Key Authentication**
   ```bash
   # Generate SSH key on your computer
   ssh-keygen -t rsa -b 4096
   
   # Copy to Pi
   ssh-copy-id pi@raspberrypi.local
   ```

3. **Disable Password Authentication**
   ```bash
   sudo nano /etc/ssh/sshd_config
   # Set: PasswordAuthentication no
   sudo systemctl restart ssh
   ```

## Access Points

After successful deployment:

- **Web Interface**: `http://<pi-ip-address>:3000`
- **Upload Photos**: Drag and drop JPEG files on the web interface
- **Monitor Status**: Check system status via web interface
- **SSH Access**: `ssh pi@<pi-ip-address>`

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review system logs: `sudo journalctl -u photo-frame.service`
3. Test components individually (display, web server, API)
4. Verify hardware connections and power supply

## Hardware Connections

### Waveshare 7.3inch e-Paper HAT

The HAT connects directly to the Pi's GPIO header. No additional wiring required.

**Verify connection:**
```bash
# Check if display is detected
ls /dev/spi*
# Should show: /dev/spidev0.0  /dev/spidev0.1
```

**GPIO Usage:**
- SPI0: Display communication
- Power: 3.3V and 5V from Pi
- Ground: GND connections

The display will be automatically detected when the service starts.