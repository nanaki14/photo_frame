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

```bash
# 1. Copy project to your Pi
scp -r . pi@raspberrypi.local:~/photo_frame

# 2. SSH into Pi and run installation
ssh pi@raspberrypi.local
cd photo_frame
./install.sh

# 3. Reboot and start service
sudo reboot
sudo systemctl start photo-frame
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
