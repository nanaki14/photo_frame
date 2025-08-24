# Hardware Integration Test Guide

## Raspberry Pi Zero 2 WH + Waveshare 7.3inch e-Paper Display Testing

This guide provides comprehensive testing procedures for validating the digital photo frame on actual hardware.

## 🔧 Pre-Test Hardware Setup

### Required Hardware
- Raspberry Pi Zero 2 WH
- Waveshare 7.3inch e-Paper HAT (800×480)
- MicroSD card (16GB+, Class 10)
- 5V 2.5A power supply
- WiFi network connection

### Hardware Assembly Verification
```bash
# 1. Check GPIO connection
gpio readall

# 2. Verify SPI is enabled
lsmod | grep spi
# Expected output: spi_bcm2835

# 3. Check SPI devices
ls /dev/spi*
# Expected: /dev/spidev0.0  /dev/spidev0.1

# 4. Verify HAT detection
sudo i2cdetect -y 1
```

## 📋 Test Execution Checklist

### Phase 1: System Installation Test
```bash
# 1. Clone project to Pi
git clone <repository> photo_frame
cd photo_frame

# 2. Run installation script
./install.sh

# 3. Verify installation completion
echo $?  # Should be 0

# 4. Check service installation
systemctl is-enabled photo-frame.service
# Expected: enabled

# 5. Verify Python dependencies
source venv/bin/activate
python3 -c "import PIL, psutil; print('Dependencies OK')"
deactivate
```

### Phase 2: Display Hardware Test
```bash
# 1. Test display manager directly
cd display
python3 display_manager.py test

# 2. Verify display initialization
python3 -c "
from display_manager import DisplayManager
d = DisplayManager()
print('Init result:', d.initialize())
print('Status:', d.get_status())
"

# 3. Test image display
python3 display_manager.py display /path/to/test/image.jpg

# 4. Test text display
python3 display_manager.py message "Hardware Test OK"

# 5. Test display clearing
python3 display_manager.py clear
```

### Phase 3: Web Service Integration Test
```bash
# 1. Start the service
sudo systemctl start photo-frame.service

# 2. Check service status
sudo systemctl status photo-frame.service

# 3. Verify web server response
curl -s http://localhost:3000/api/status | jq .

# 4. Test from another device on network
curl -s http://$(hostname -I | awk '{print $1}'):3000/api/status

# 5. Check logs for errors
sudo journalctl -u photo-frame.service --since "5 minutes ago"
```

### Phase 4: Complete Workflow Test
```bash
# 1. Create test image
python3 -c "
from PIL import Image
img = Image.new('RGB', (1000, 800), 'red')
img.save('hardware_test.jpg', 'JPEG')
print('Test image created')
"

# 2. Upload via API
curl -X POST -F "photo=@hardware_test.jpg" http://localhost:3000/api/photo

# 3. Verify display update
# Check if image appears on e-ink display

# 4. Verify system status
curl -s http://localhost:3000/api/status | jq '.data.display'

# 5. Test deletion
curl -X DELETE http://localhost:3000/api/photo

# 6. Verify display cleared
# Check if display is cleared
```

## 🔍 Hardware-Specific Validation

### Display Quality Verification
- [ ] Image appears correctly on e-ink display
- [ ] Aspect ratio is maintained
- [ ] Contrast is appropriate for e-ink
- [ ] No corruption or artifacts
- [ ] Display updates within 10 seconds
- [ ] Multiple uploads work correctly

### Performance Validation
```bash
# Monitor system performance during operation
python3 performance_monitor.py --monitor 5

# Run benchmark on actual hardware
python3 performance_monitor.py --benchmark

# Check temperature during operation
vcgencmd measure_temp

# Monitor memory usage
free -h
```

### Network Integration Test
```bash
# Test web interface from smartphone
# 1. Find Pi IP address
hostname -I

# 2. Access from phone browser: http://<pi-ip>:3000
# 3. Test photo upload from phone
# 4. Verify display updates
# 5. Test different image sizes and types
```

## 🚨 Common Hardware Issues and Solutions

### Display Not Working
```bash
# Check GPIO connections
gpio readall

# Verify SPI configuration
sudo raspi-config
# Interface Options → SPI → Enable

# Check for hardware conflicts
dmesg | grep -i spi

# Test with minimal example
python3 -c "
import RPi.GPIO as GPIO
import spidev
spi = spidev.SpiDev()
spi.open(0, 0)
print('SPI OK')
spi.close()
"
```

### Service Won't Start
```bash
# Check detailed logs
sudo journalctl -u photo-frame.service -f

# Verify Bun installation
/home/pi/.bun/bin/bun --version

# Check permissions
ls -la /home/pi/photo_frame/
sudo chown -R pi:pi /home/pi/photo_frame/

# Test manual start
cd /home/pi/photo_frame
/home/pi/.bun/bin/bun start
```

### Memory Issues
```bash
# Check memory usage
free -h

# Increase swap if needed
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
# Set CONF_SWAPSIZE=1024
sudo dphys-swapfile setup
sudo dphys-swapfile swapon

# Enable low-memory optimizations
export PHOTO_FRAME_LOW_MEMORY=true
```

### WiFi Connectivity Issues
```bash
# Check WiFi status
iwconfig

# Test connectivity
ping google.com

# Restart WiFi if needed
sudo systemctl restart networking

# Check WiFi configuration
cat /etc/wpa_supplicant/wpa_supplicant.conf
```

## 📊 Hardware Test Results Template

### Test Environment
- Pi Model: Raspberry Pi Zero 2 WH
- RAM: 512MB
- SD Card: [Brand/Size/Class]
- Power Supply: [Voltage/Amperage]
- WiFi: [Network type/speed]
- Temperature: [Ambient/Operating]

### Performance Metrics
```
Image Processing Time: _____ seconds
Memory Usage Peak: _____ MB
CPU Usage Peak: _____ %
Display Update Time: _____ seconds
Network Response Time: _____ ms
Operating Temperature: _____ °C
```

### Functionality Tests
- [ ] Hardware assembly completed
- [ ] System installation successful
- [ ] Display initialization working
- [ ] Image processing functional
- [ ] Web interface accessible
- [ ] Photo upload working
- [ ] Display updates correctly
- [ ] Error handling appropriate
- [ ] Performance acceptable
- [ ] Network connectivity stable

### Quality Assessment
- [ ] Display image quality: Excellent/Good/Acceptable/Poor
- [ ] System responsiveness: Fast/Moderate/Slow
- [ ] Stability: Very Stable/Stable/Occasional Issues/Unstable
- [ ] Power consumption: Low/Moderate/High
- [ ] Heat generation: Cool/Warm/Hot

## 🔧 Hardware Optimization Recommendations

### Based on Test Results

#### If Processing Time > 10 seconds:
- Enable low-memory optimizations
- Reduce image quality settings
- Check CPU temperature for throttling

#### If Memory Usage > 400MB:
- Increase swap space
- Enable chunked processing
- Restart service periodically

#### If Display Updates Fail:
- Check GPIO connections
- Verify SPI configuration
- Test with minimal display example

#### If Network Issues:
- Check WiFi signal strength
- Consider ethernet adapter
- Optimize network settings

## 📋 Sign-off Checklist

### Hardware Integration Complete ✅
- [ ] All hardware components connected correctly
- [ ] System installation completed successfully
- [ ] Display functionality verified on actual hardware
- [ ] Web interface accessible from external devices
- [ ] Complete photo upload workflow tested
- [ ] Performance meets acceptable thresholds
- [ ] Error conditions handled gracefully
- [ ] System stable under normal operation
- [ ] Documentation updated with any hardware-specific notes
- [ ] End-user can successfully operate the system

### Notes:
```
Date: ___________
Tester: ___________
Hardware Revision: ___________
Software Version: ___________
Issues Found: ___________
Recommended Actions: ___________
```

---

## Summary

This hardware integration test ensures the digital photo frame works correctly on actual Raspberry Pi Zero 2 WH hardware with the Waveshare e-ink display. Complete all test phases and document any issues for future reference.