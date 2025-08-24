#!/bin/bash

# Digital Photo Frame Security Hardening Script
# Implements basic security measures for Raspberry Pi deployment

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Digital Photo Frame Security Hardening${NC}"
echo "This script will implement basic security measures."
echo

# Confirmation
read -p "Continue with security hardening? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Security hardening cancelled"
    exit 0
fi

log() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 1. System Updates
log "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# 2. Install Security Tools
log "Installing security tools..."
sudo apt install -y ufw fail2ban unattended-upgrades rkhunter chkrootkit

# 3. Configure Automatic Updates
log "Configuring automatic security updates..."
echo 'APT::Periodic::Update-Package-Lists "1";' | sudo tee /etc/apt/apt.conf.d/20auto-upgrades
echo 'APT::Periodic::Unattended-Upgrade "1";' | sudo tee -a /etc/apt/apt.conf.d/20auto-upgrades

# Configure unattended upgrades for security only
sudo tee /etc/apt/apt.conf.d/50unattended-upgrades > /dev/null << 'EOF'
Unattended-Upgrade::Allowed-Origins {
    "${distro_id}:${distro_codename}-security";
};
Unattended-Upgrade::Automatic-Reboot "false";
Unattended-Upgrade::Remove-Unused-Dependencies "true";
EOF

# 4. Configure Firewall
log "Configuring UFW firewall..."
sudo ufw --force reset
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow SSH (check if port has been changed)
SSH_PORT=$(grep "^Port" /etc/ssh/sshd_config | awk '{print $2}' || echo "22")
sudo ufw allow $SSH_PORT/tcp comment "SSH"

# Allow photo frame web interface
sudo ufw allow 3000/tcp comment "Photo Frame Web"

# Enable firewall
sudo ufw --force enable

# 5. Configure Fail2Ban
log "Configuring Fail2Ban..."
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local

# Create custom jail for photo frame
sudo tee /etc/fail2ban/jail.d/photo-frame.conf > /dev/null << 'EOF'
[photo-frame]
enabled = true
port = 3000
protocol = tcp
filter = photo-frame
logpath = /var/log/syslog
maxretry = 5
bantime = 3600
findtime = 600
EOF

# Create filter for photo frame
sudo tee /etc/fail2ban/filter.d/photo-frame.conf > /dev/null << 'EOF'
[Definition]
failregex = photo-frame.*Failed login from <HOST>
            photo-frame.*Unauthorized access from <HOST>
            photo-frame.*Too many requests from <HOST>
ignoreregex =
EOF

# Start and enable fail2ban
sudo systemctl enable fail2ban
sudo systemctl restart fail2ban

# 6. SSH Hardening
log "Hardening SSH configuration..."

# Backup original SSH config
sudo cp /etc/ssh/sshd_config /etc/ssh/sshd_config.backup

# Apply SSH hardening
sudo tee -a /etc/ssh/sshd_config > /dev/null << 'EOF'

# Photo Frame Security Hardening
Protocol 2
PermitRootLogin no
PasswordAuthentication yes
PermitEmptyPasswords no
MaxAuthTries 3
MaxSessions 2
ClientAliveInterval 300
ClientAliveCountMax 2
X11Forwarding no
AllowUsers pi
EOF

# 7. Disable Unnecessary Services
log "Disabling unnecessary services..."
services_to_disable=(
    "bluetooth"
    "cups"
    "avahi-daemon"
    "triggerhappy"
)

for service in "${services_to_disable[@]}"; do
    if systemctl is-enabled "$service" >/dev/null 2>&1; then
        sudo systemctl disable "$service"
        sudo systemctl stop "$service"
        log "Disabled $service"
    fi
done

# 8. Set File Permissions
log "Setting secure file permissions..."
sudo chmod 700 /home/pi/.ssh 2>/dev/null || true
sudo chmod 600 /home/pi/.ssh/authorized_keys 2>/dev/null || true
sudo chmod 644 /home/pi/photo_frame/uploads 2>/dev/null || true

# 9. Configure System Limits
log "Configuring system security limits..."
sudo tee -a /etc/security/limits.conf > /dev/null << 'EOF'

# Photo Frame Security Limits
pi soft nofile 1024
pi hard nofile 2048
pi soft nproc 512
pi hard nproc 1024
EOF

# 10. Network Security
log "Applying network security settings..."
sudo tee -a /etc/sysctl.conf > /dev/null << 'EOF'

# Photo Frame Network Security
net.ipv4.ip_forward = 0
net.ipv4.conf.all.accept_redirects = 0
net.ipv4.conf.all.secure_redirects = 0
net.ipv4.conf.all.accept_source_route = 0
net.ipv4.conf.all.log_martians = 1
net.ipv4.icmp_echo_ignore_broadcasts = 1
net.ipv4.icmp_ignore_bogus_error_responses = 1
net.ipv4.tcp_syncookies = 1
EOF

# Apply sysctl settings
sudo sysctl -p

# 11. Create Security Monitoring Script
log "Creating security monitoring script..."
sudo tee /usr/local/bin/photo-frame-security-check > /dev/null << 'EOF'
#!/bin/bash
# Photo Frame Security Monitor

echo "=== Photo Frame Security Check - $(date) ==="

# Check for failed login attempts
echo "Recent failed login attempts:"
grep "authentication failure" /var/log/auth.log | tail -5

# Check firewall status
echo -e "\nFirewall status:"
ufw status

# Check running services
echo -e "\nRunning services:"
systemctl list-units --type=service --state=running | grep -E "(ssh|photo-frame|fail2ban)"

# Check disk usage
echo -e "\nDisk usage:"
df -h / | tail -1

# Check last logins
echo -e "\nRecent logins:"
last | head -5

# Check for unauthorized files
echo -e "\nChecking for unauthorized files in uploads:"
find /home/pi/photo_frame/uploads -type f -not -name "*.jpg" 2>/dev/null || echo "No unauthorized files found"

echo "=== Security check completed ==="
EOF

chmod +x /usr/local/bin/photo-frame-security-check

# 12. Setup Log Rotation
log "Configuring log rotation..."
sudo tee /etc/logrotate.d/photo-frame > /dev/null << 'EOF'
/var/log/photo-frame/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 644 pi pi
    postrotate
        systemctl reload photo-frame.service
    endscript
}
EOF

# 13. Create Security Audit Cron Job
log "Setting up security monitoring..."
(crontab -l 2>/dev/null; echo "0 2 * * * /usr/local/bin/photo-frame-security-check >> /var/log/security-check.log") | crontab -

# 14. Final Security Report
log "Generating security status report..."
echo -e "\n${YELLOW}=== Security Hardening Summary ===${NC}"
echo "✓ System packages updated"
echo "✓ Security tools installed (UFW, Fail2Ban, etc.)"
echo "✓ Automatic security updates configured"
echo "✓ Firewall configured and enabled"
echo "✓ Fail2Ban configured for SSH and photo frame"
echo "✓ SSH hardened (root login disabled, limited auth attempts)"
echo "✓ Unnecessary services disabled"
echo "✓ File permissions secured"
echo "✓ Network security settings applied"
echo "✓ Security monitoring script created"
echo "✓ Log rotation configured"
echo "✓ Daily security checks scheduled"

echo -e "\n${YELLOW}Next Steps:${NC}"
echo "1. Change default password: ${BLUE}passwd${NC}"
echo "2. Set up SSH keys: ${BLUE}ssh-copy-id pi@raspberrypi${NC}"
echo "3. Consider disabling password auth in SSH"
echo "4. Review firewall rules: ${BLUE}sudo ufw status${NC}"
echo "5. Monitor logs: ${BLUE}sudo journalctl -f${NC}"

echo -e "\n${YELLOW}Security Check Command:${NC}"
echo "Run daily security check: ${BLUE}/usr/local/bin/photo-frame-security-check${NC}"

echo -e "\n${GREEN}Security hardening completed successfully!${NC}"
echo -e "${YELLOW}Consider rebooting to apply all changes.${NC}"