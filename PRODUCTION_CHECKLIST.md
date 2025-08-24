# Production Deployment Checklist

This checklist ensures your digital photo frame is ready for production deployment on Raspberry Pi Zero 2 WH with Waveshare 7.3inch e-Paper display.

## Pre-Deployment Validation

### ✅ Hardware Requirements
- [ ] Raspberry Pi Zero 2 WH confirmed and functional
- [ ] Waveshare 7.3inch e-Paper display (800×480) connected
- [ ] SPI interface enabled and tested
- [ ] GPIO pins properly connected (refer to HARDWARE_TEST.md)
- [ ] Adequate power supply (minimum 2.5A recommended)
- [ ] MicroSD card (minimum 16GB, Class 10 recommended)

### ✅ Software Prerequisites
- [ ] Raspberry Pi OS Lite installed and updated
- [ ] Python 3.9+ installed and configured
- [ ] Node.js/Bun runtime installed
- [ ] Required Python packages installed (requirements.txt)
- [ ] SPI interface enabled (`sudo raspi-config`)
- [ ] SSH access configured (if remote management needed)

### ✅ Code Quality Validation
- [ ] All unit tests passing (`bun test` and `python3 -m pytest`)
- [ ] No compilation errors (`bun run build`)
- [ ] Python syntax validation (`python3 -m py_compile display/*.py`)
- [ ] TypeScript type checking passed
- [ ] Code formatting validated (`bun run lint`)

## Security Hardening

### ✅ System Security
- [ ] Run security hardening script: `bash harden_security.sh`
- [ ] Firewall configured (UFW enabled with required ports)
- [ ] Fail2Ban installed and configured
- [ ] SSH key-based authentication enabled (disable password auth)
- [ ] Default passwords changed (pi user, etc.)
- [ ] Unnecessary services disabled
- [ ] Automatic security updates enabled

### ✅ Application Security
- [ ] File upload restrictions enforced (JPEG only, size limits)
- [ ] Input validation implemented for all API endpoints
- [ ] Error messages don't expose sensitive information
- [ ] File permissions properly set (644 for files, 755 for executables)
- [ ] Storage directory permissions secured
- [ ] No hardcoded credentials in code

## Performance Optimization

### ✅ Resource Management
- [ ] Memory usage optimized for Pi Zero 2 WH (512MB RAM)
- [ ] Image processing settings tuned for e-ink display
- [ ] Swap file configured if needed
- [ ] CPU governor set appropriately
- [ ] Background processes minimized
- [ ] Log rotation configured to prevent disk fill

### ✅ Storage Management
- [ ] Storage monitoring implemented
- [ ] Automatic cleanup of old photos configured
- [ ] Log file rotation enabled
- [ ] Disk space alerts configured
- [ ] Backup strategy planned (if applicable)

## Service Configuration

### ✅ SystemD Service
- [ ] photo-frame.service file created and installed
- [ ] Service starts automatically on boot
- [ ] Service restart policy configured
- [ ] Service logs properly configured
- [ ] Service health monitoring enabled

### ✅ Web Server Configuration
- [ ] Application runs on correct port (3000)
- [ ] Static file serving configured
- [ ] CORS settings appropriate for deployment
- [ ] Request timeout settings configured
- [ ] Rate limiting configured (if needed)

## Testing and Validation

### ✅ Functional Testing
- [ ] Photo upload workflow tested end-to-end
- [ ] Display update functionality verified
- [ ] Settings management tested
- [ ] API endpoints responding correctly
- [ ] Error handling tested (network errors, file errors, etc.)
- [ ] Mobile device compatibility verified

### ✅ Hardware Integration Testing
- [ ] Run hardware validation: `bash validate_hardware.sh`
- [ ] E-ink display refresh tested
- [ ] SPI communication verified
- [ ] GPIO status confirmed
- [ ] Temperature monitoring functional
- [ ] Power consumption within acceptable limits

### ✅ Load Testing
- [ ] Multiple concurrent uploads tested
- [ ] Memory usage under load verified
- [ ] Display update performance measured
- [ ] Network connectivity resilience tested
- [ ] Long-running stability tested (24+ hours)

## Documentation and Maintenance

### ✅ Documentation Complete
- [ ] README.md updated with deployment instructions
- [ ] API.md documentation reviewed and current
- [ ] HARDWARE_TEST.md procedures validated
- [ ] SECURITY.md recommendations implemented
- [ ] Installation scripts tested and documented

### ✅ Monitoring and Logging
- [ ] Application logs configured and accessible
- [ ] System health monitoring enabled
- [ ] Display status monitoring functional
- [ ] Error alerting configured (optional)
- [ ] Performance metrics collection enabled

### ✅ Backup and Recovery
- [ ] Configuration backup strategy defined
- [ ] Photo storage backup plan (if applicable)
- [ ] System recovery procedures documented
- [ ] Rollback plan prepared
- [ ] Factory reset procedure documented

## Deployment Steps

### ✅ Initial Deployment
1. [ ] Flash Raspberry Pi OS to SD card
2. [ ] Enable SSH and SPI in raspi-config
3. [ ] Update system: `sudo apt update && sudo apt upgrade -y`
4. [ ] Install required packages: `bash install.sh`
5. [ ] Clone/copy project files to `/home/pi/photo_frame`
6. [ ] Install Python dependencies: `pip3 install -r display/requirements.txt`
7. [ ] Install Node.js dependencies: `bun install`
8. [ ] Build application: `bun run build`
9. [ ] Configure SystemD service: `sudo systemctl enable photo-frame.service`
10. [ ] Start service: `sudo systemctl start photo-frame.service`

### ✅ Post-Deployment Validation
- [ ] Service status check: `sudo systemctl status photo-frame.service`
- [ ] Application accessible via web browser
- [ ] Upload test photo and verify display update
- [ ] Check system logs for errors
- [ ] Verify all API endpoints responding
- [ ] Test mobile device access
- [ ] Monitor resource usage for 15 minutes

### ✅ Production Monitoring
- [ ] Set up log monitoring: `sudo journalctl -u photo-frame.service -f`
- [ ] Configure health check endpoint monitoring
- [ ] Set up disk space monitoring
- [ ] Configure service restart monitoring
- [ ] Test emergency shutdown/restart procedures

## Troubleshooting Common Issues

### Network Issues
- Check WiFi configuration: `iwconfig`
- Test connectivity: `ping google.com`
- Verify firewall rules: `sudo ufw status`

### Display Issues
- Check SPI configuration: `ls /dev/spi*`
- Verify GPIO connections: `gpio readall`
- Test display hardware: `python3 display/display_manager.py test`

### Service Issues
- Check service status: `sudo systemctl status photo-frame.service`
- View service logs: `sudo journalctl -u photo-frame.service -n 50`
- Restart service: `sudo systemctl restart photo-frame.service`

### Performance Issues
- Check memory usage: `free -h`
- Monitor CPU usage: `htop`
- Check disk space: `df -h`
- Analyze process usage: `ps aux`

## Sign-off

### ✅ Final Validation
- [ ] All checklist items completed
- [ ] System running stable for 24+ hours
- [ ] No critical errors in logs
- [ ] Performance within acceptable parameters
- [ ] Security scan completed successfully
- [ ] Documentation reviewed and accurate

**Deployment Date:** _______________  
**Deployed By:** _______________  
**System Version:** _______________  
**Hardware Serial:** _______________  

---

## Emergency Contacts and Procedures

### Quick Recovery Commands
```bash
# Restart photo frame service
sudo systemctl restart photo-frame.service

# Check service logs
sudo journalctl -u photo-frame.service -f

# Hardware validation
bash validate_hardware.sh

# Security check
bash harden_security.sh --check

# Factory reset (removes all photos and resets settings)
rm -rf storage/photos/* storage/config/*
sudo systemctl restart photo-frame.service
```

### Support Resources
- Hardware documentation: HARDWARE_TEST.md
- API reference: API.md
- Security guide: SECURITY.md
- Installation guide: README.md

This checklist ensures your digital photo frame is production-ready, secure, and maintainable.