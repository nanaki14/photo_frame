# Digital Photo Frame

**Waveshare 7.3inch e-ink Display + Raspberry Pi Zero 2 WH**

A modern web-based digital photo frame system that allows you to upload photos from your smartphone and display them on a Waveshare e-ink screen.

## ✨ Features

- **📱 Smartphone Upload**: Drag & drop JPEG photos via web interface
- **🖥️ E-ink Display**: 800×480 Waveshare 7.3inch e-Paper display
- **⚡ Real-time Updates**: Instant display refresh when photos are uploaded
- **📡 WiFi Enabled**: Access from any device on your network
- **🔄 Single Photo Mode**: New photos replace old ones automatically
- **🎨 Smart Processing**: Automatic image optimization for e-ink display
- **📊 System Monitoring**: Battery, storage, and display status
- **🔧 Easy Setup**: Automated installation scripts

## 🏗️ Architecture

- **Frontend**: React 19 + TypeScript + Tailwind CSS
- **Backend**: Bun runtime + Hono framework + Sharp image processing
- **Display**: Python + Pillow + Waveshare e-Paper library
- **Hardware**: Raspberry Pi Zero 2 WH + Waveshare 7.3inch e-Paper HAT

## 🚀 Quick Start

### For Development

```bash
# Install dependencies
bun install

# Install Python dependencies
cd display && pip install -r requirements.txt

# Start development server
bun dev

# Access web interface
open http://localhost:3000
```

### For Raspberry Pi Deployment

#### Step 1: Prepare Your Pi

```bash
# Default Raspberry Pi OS credentials: pi / raspberry
# Enable SSH and connect to your network first
```

#### Step 2: Copy Project & Build on Development Machine

```bash
# Build frontend
bun run build

# Copy to Pi (replace YOUR_PI_IP with actual IP address)
scp -r . pi@YOUR_PI_IP:~/photo_frame
```

#### Step 3: Install on Raspberry Pi

```bash
# SSH into Pi
ssh pi@YOUR_PI_IP
cd ~/photo_frame

# Run minimal installation script
chmod +x install.sh
./install.sh

# Follow prompts and wait for completion
```

#### Step 4: Start the Service

```bash
# After installation completes (no reboot needed)
sudo systemctl start photo-frame.service

# Verify service is running
sudo systemctl status photo-frame.service

# View real-time logs
sudo journalctl -u photo-frame.service -f
```

#### Step 5: Access Web Interface

```bash
# Get Pi's IP address
hostname -I

# Open in browser
http://<YOUR_PI_IP>:3000
```

#### Hardware Setup

Before starting the service, ensure hardware is properly connected:

1. **Waveshare e-Paper HAT**: Connect to Raspberry Pi's 40-pin GPIO header
2. **Power Supply**: Use 5V 2.5A or better (USB-C on Pi Zero 2 WH)
3. **MicroSD Card**: 16GB+ with Raspberry Pi OS Lite pre-installed

#### Troubleshooting

```bash
# Check service logs
sudo journalctl -u photo-frame.service -n 50

# Manually test display (if Python display manager exists)
cd ~/photo_frame/display
python3 -c "from display_manager import DisplayManager; d = DisplayManager(); print('OK')"

# Restart service
sudo systemctl restart photo-frame.service

# Enable auto-start on boot (should already be enabled)
sudo systemctl enable photo-frame.service
```

## 📱 Usage

1. **Access Web Interface**: Navigate to `http://<pi-ip-address>:3000`
2. **Upload Photos**: Drag & drop JPEG files or click to browse
3. **View Current Photo**: Check the Gallery page for currently displayed image
4. **Monitor System**: Dashboard shows battery, storage, and display status
5. **Configure Settings**: Adjust display brightness and system preferences

## 📋 Requirements

### Hardware
- Raspberry Pi Zero 2 WH (or any Pi with 40-pin GPIO)
- Waveshare 7.3inch e-Paper HAT (800×480)
- MicroSD card (16GB+ recommended)
- 5V 2.5A power supply

### Software
- Raspberry Pi OS Lite
- Node.js (installed via script)
- Python 3.8+
- Bun runtime (installed via script)

## 📁 Project Structure

```
photo_frame/
├── src/                    # Frontend & Backend source
│   ├── components/         # React components
│   ├── pages/             # Application pages
│   ├── hooks/             # React hooks
│   ├── lib/               # Utilities and API client
│   └── server/            # Hono API server
├── display/               # Python display management
│   ├── display_manager.py # Main display controller
│   ├── update_display.py  # Display update script
│   └── requirements.txt   # Python dependencies
├── uploads/               # Uploaded photos storage
├── docs/                  # Documentation
├── install.sh            # Automated Pi installation
├── service.sh            # Service management
└── DEPLOYMENT.md         # Detailed deployment guide
```

## 🔧 Development

To run for development:

```bash
bun install
bun dev
```

This project was created using `bun init` in bun v1.2.14. [Bun](https://bun.sh) is a fast all-in-one JavaScript runtime.
