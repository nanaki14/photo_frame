# Digital Photo Frame

**Waveshare 7.3inch e-ink Display + Raspberry Pi Zero 2 WH**

A modern web-based digital photo frame system that allows you to upload photos from your smartphone and display them on a Waveshare e-ink screen.

## ✨ Features

- **📱 Smartphone Upload**: Drag & drop JPEG photos via web interface
- **🖥️ E-ink Display**: 800×480 Waveshare 7.3inch e-Paper HAT (E) - E Ink Spectra 6 (6-color)
  - Supports 6 colors: Black, White, Red, Yellow, Green, Blue
- **⚡ Real-time Updates**: Instant display refresh when photos are uploaded
- **📡 WiFi Enabled**: Access from any device on your network
- **🔄 Single Photo Mode**: New photos replace old ones automatically
- **🎨 Smart Processing**: Automatic image optimization for E Ink Spectra 6 display
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

1. **Waveshare e-Paper HAT**: Connect to Raspberry Pi's 40-pin GPIO header (optional - system works without it using mock display)
2. **Power Supply**: Use 5V 2.5A or better (USB-C on Pi Zero 2 WH)
3. **MicroSD Card**: 16GB+ with Raspberry Pi OS Lite pre-installed

**Note**: The installation script automatically installs the Waveshare e-Paper library. If hardware is not connected, the system will use a mock display for development/testing.

#### Troubleshooting

```bash
# Check service logs
sudo journalctl -u photo-frame.service -n 50

# Check display status
source ~/photo_frame/venv/bin/activate
python3 ~/photo_frame/display/update_display.py ~/photo_frame/uploads/photo.jpg

# View display manager logs
tail -20 /tmp/display_manager.log

# Manually test display
source ~/photo_frame/venv/bin/activate
cd ~/photo_frame/display
python3 display_manager.py test

# Restart service
sudo systemctl restart photo-frame.service

# Enable auto-start on boot (should already be enabled)
sudo systemctl enable photo-frame.service
```

## 🎨 Color Display & Image Optimization

The system uses advanced color optimization to maximize visual fidelity on the 6-color e-ink display:

### Two-Stage Color Processing

1. **Server-Side Enhancement** (upload processing):
   - Image normalization for optimal tonal range
   - 1.8x saturation boost for vivid colors
   - Contrast enhancement via double-negation technique
   - High-quality JPEG preservation (95-98%)

2. **Display-Side Optimization** (display rendering):
   - Additional 50% contrast and saturation enhancement
   - Extended 17-color palette for dithering (vs. just 6 core colors)
   - Floyd-Steinberg dithering for smooth color distribution
   - Memory-optimized processing for Raspberry Pi Zero

### Supported Image Types

- **Full-color photos**: RGB images automatically optimized for 6-color display
- **Graphics and illustrations**: Best results with distinct colors
- **Gradients**: Converted using dithering for smooth pseudo-color transitions
- **Mixed content**: Photos with text, charts, and graphics all supported

**Note**: The 6-color palette (Black, White, Red, Yellow, Green, Blue) works best with images that have distinct color regions. Grayscale or low-contrast images may appear predominantly in black and white, which is expected behavior.

For detailed information about color optimization, see [COLOR_OPTIMIZATION.md](COLOR_OPTIMIZATION.md).

## 📱 Usage

1. **Access Web Interface**: Navigate to `http://<pi-ip-address>:3000`
2. **Upload Photos**: Drag & drop JPEG files or click to browse
3. **Automatic Processing**: Images are optimized for 6-color display during upload
4. **View Current Photo**: Check the Gallery page for currently displayed image
5. **Monitor System**: Dashboard shows battery, storage, and display status
6. **Configure Settings**: Adjust display brightness and system preferences

## 📋 Requirements

### Hardware
- Raspberry Pi Zero 2 WH (or any Pi with 40-pin GPIO)
- Waveshare 7.3inch e-Paper HAT (800×480)
- MicroSD card (16GB+ recommended)
- 5V 2.5A power supply

### Software
- Raspberry Pi OS Lite
- Node.js or Bun runtime (installed via script)
- Python 3.8+
- Waveshare e-Paper library (installed via script)

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
├── README.md             # This file
├── COLOR_OPTIMIZATION.md # Color processing details & tuning guide
├── DEPLOYMENT.md         # Detailed deployment guide
├── HARDWARE_TEST.md      # Hardware integration testing
├── PERFORMANCE.md        # Performance optimization guide
└── API.md               # API endpoint documentation
```

## 🔧 Development

To run for development:

```bash
bun install
bun dev
```

This project was created using `bun init` in bun v1.2.14. [Bun](https://bun.sh) is a fast all-in-one JavaScript runtime.
