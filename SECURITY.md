# Security Audit & Hardening Guide

## Digital Photo Frame Security Assessment

This document provides a comprehensive security audit and hardening recommendations for the digital photo frame system.

## 🔍 Security Risk Assessment

### Risk Level: **MODERATE**
- **Network Exposure**: Web server accessible on local network
- **File Upload**: Accepts file uploads from network clients
- **System Access**: Runs with user privileges on Raspberry Pi
- **Physical Access**: Device may be in accessible locations

## 🛡️ Current Security Measures

### Application Level
✅ **File Type Validation**: Only JPEG files accepted  
✅ **File Size Limits**: 10MB maximum upload size  
✅ **Input Validation**: Proper error handling for malformed requests  
✅ **Non-root Execution**: Service runs as 'pi' user, not root  
✅ **Single File Management**: No file accumulation, reduces storage risks  

### System Level  
✅ **Local Network Only**: No external internet exposure by default  
✅ **Standard Pi OS**: Regular security updates available  
✅ **SSH Access**: Can be secured with key-based authentication  

## 🚨 Identified Security Concerns

### HIGH PRIORITY
1. **No Authentication**: Web interface has no access control
2. **No HTTPS**: All traffic is unencrypted
3. **Default SSH**: May use default credentials
4. **No Rate Limiting**: Vulnerable to upload flooding

### MEDIUM PRIORITY
5. **Directory Traversal**: Path handling should be validated
6. **No Input Sanitization**: Minimal validation of file contents
7. **Error Information**: May leak system information
8. **No Audit Logging**: No record of access attempts

### LOW PRIORITY
9. **Physical Security**: Device access could compromise system
10. **Network Exposure**: Broadcast on local network

## 🔒 Security Hardening Recommendations

### 1. Authentication & Access Control

#### Add Basic Authentication
```javascript
// Add to server configuration
const ADMIN_USERNAME = process.env.ADMIN_USER || 'admin';
const ADMIN_PASSWORD = process.env.ADMIN_PASS || 'change-me-now';

app.use('/api/*', async (c, next) => {
  const auth = c.req.header('Authorization');
  if (!auth || !auth.startsWith('Basic ')) {
    return c.text('Unauthorized', 401, {
      'WWW-Authenticate': 'Basic realm="Photo Frame"'
    });
  }
  
  const credentials = atob(auth.slice(6));
  const [username, password] = credentials.split(':');
  
  if (username !== ADMIN_USERNAME || password !== ADMIN_PASSWORD) {
    return c.text('Unauthorized', 401);
  }
  
  await next();
});
```

#### Environment Variables
```bash
# Add to /etc/systemd/system/photo-frame.service
Environment=ADMIN_USER=your_username
Environment=ADMIN_PASS=your_secure_password
```

### 2. HTTPS Implementation

#### Generate Self-Signed Certificate
```bash
# Create SSL certificate
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/ssl/private/photoframe.key \
  -out /etc/ssl/certs/photoframe.crt \
  -subj "/C=US/ST=State/L=City/O=PhotoFrame/CN=photoframe.local"

# Set proper permissions
sudo chmod 600 /etc/ssl/private/photoframe.key
sudo chmod 644 /etc/ssl/certs/photoframe.crt
```

#### Update Server Configuration
```javascript
import { readFileSync } from 'fs';

const httpsOptions = {
  key: readFileSync('/etc/ssl/private/photoframe.key'),
  cert: readFileSync('/etc/ssl/certs/photoframe.crt')
};

serve({
  fetch: app.fetch,
  port: 3443,
  tls: httpsOptions
});
```

### 3. Input Validation & Sanitization

#### Enhanced File Validation
```javascript
// Add magic number validation
const validateJPEG = (buffer) => {
  // JPEG magic numbers: FF D8 FF
  return buffer[0] === 0xFF && buffer[1] === 0xD8 && buffer[2] === 0xFF;
};

// Add image content validation
const validateImageContent = async (buffer) => {
  try {
    const metadata = await sharp(buffer).metadata();
    // Check for reasonable dimensions
    if (metadata.width > 10000 || metadata.height > 10000) {
      throw new Error('Image dimensions too large');
    }
    return true;
  } catch (error) {
    return false;
  }
};
```

#### Path Sanitization
```javascript
const sanitizePath = (filename) => {
  // Remove path traversal attempts
  return path.basename(filename).replace(/[^a-zA-Z0-9._-]/g, '');
};
```

### 4. Rate Limiting

#### API Rate Limiting
```javascript
const rateLimiter = new Map();

const rateLimit = (ip, maxRequests = 10, windowMs = 60000) => {
  const now = Date.now();
  const requests = rateLimiter.get(ip) || [];
  
  // Remove old requests
  const recentRequests = requests.filter(time => now - time < windowMs);
  
  if (recentRequests.length >= maxRequests) {
    return false;
  }
  
  recentRequests.push(now);
  rateLimiter.set(ip, recentRequests);
  return true;
};

app.use('/api/photo', async (c, next) => {
  const clientIP = c.req.header('X-Forwarded-For') || 'unknown';
  if (!rateLimit(clientIP)) {
    return c.text('Too Many Requests', 429);
  }
  await next();
});
```

### 5. System Hardening

#### SSH Security
```bash
# 1. Change default password
passwd

# 2. Generate SSH key pair (on your computer)
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"

# 3. Copy public key to Pi
ssh-copy-id pi@raspberrypi.local

# 4. Disable password authentication
sudo nano /etc/ssh/sshd_config
# Add/modify:
PasswordAuthentication no
PermitRootLogin no
Protocol 2
Port 2222  # Change from default 22

# 5. Restart SSH
sudo systemctl restart ssh
```

#### Firewall Configuration
```bash
# Install and configure UFW
sudo apt install ufw

# Default policies
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow necessary services
sudo ufw allow 2222/tcp  # SSH (if changed)
sudo ufw allow 3000/tcp  # Photo frame web interface
sudo ufw allow 3443/tcp  # HTTPS (if implemented)

# Enable firewall
sudo ufw --force enable

# Check status
sudo ufw status verbose
```

#### System Updates
```bash
# Auto-update configuration
sudo nano /etc/apt/apt.conf.d/20auto-upgrades
# Add:
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Unattended-Upgrade "1";

# Install unattended-upgrades
sudo apt install unattended-upgrades

# Configure automatic reboot if needed
sudo nano /etc/apt/apt.conf.d/50unattended-upgrades
# Uncomment and set:
Unattended-Upgrade::Automatic-Reboot "false";
```

### 6. Logging & Monitoring

#### Enhanced Logging
```javascript
// Add request logging middleware
app.use('*', async (c, next) => {
  const start = Date.now();
  const method = c.req.method;
  const url = c.req.url;
  const ip = c.req.header('X-Forwarded-For') || 'unknown';
  
  await next();
  
  const duration = Date.now() - start;
  const status = c.res.status;
  
  console.log(`${new Date().toISOString()} ${ip} ${method} ${url} ${status} ${duration}ms`);
});
```

#### Log Monitoring
```bash
# Monitor access logs
sudo journalctl -u photo-frame.service -f | grep -E "(POST|DELETE|ERROR)"

# Set up log rotation
sudo nano /etc/logrotate.d/photo-frame
# Add:
/var/log/photo-frame/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 644 pi pi
}
```

### 7. Network Security

#### Network Isolation
```bash
# Create isolated VLAN for IoT devices (if router supports)
# Or use guest network for photo frame access

# Limit network access with iptables
sudo iptables -A OUTPUT -d 127.0.0.1 -j ACCEPT
sudo iptables -A OUTPUT -d 192.168.0.0/16 -j ACCEPT
sudo iptables -A OUTPUT -j DROP

# Save iptables rules
sudo sh -c "iptables-save > /etc/iptables.rules"
```

#### Disable Unnecessary Services
```bash
# Disable unused services
sudo systemctl disable bluetooth
sudo systemctl disable avahi-daemon
sudo systemctl disable cups
sudo systemctl disable triggerhappy

# Remove unnecessary packages
sudo apt remove --purge wolfram-engine scratch scratch2 nuscratch
sudo apt autoremove
```

## 🔧 Security Configuration Script

```bash
#!/bin/bash
# Security Hardening Script for Photo Frame

echo "Starting security hardening..."

# 1. Update system
sudo apt update && sudo apt upgrade -y

# 2. Install security tools
sudo apt install -y ufw fail2ban unattended-upgrades

# 3. Configure firewall
sudo ufw --force reset
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp
sudo ufw allow 3000/tcp
sudo ufw --force enable

# 4. Configure fail2ban
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
sudo nano /etc/fail2ban/jail.local
# Enable SSH protection

# 5. Set up automatic updates
echo 'APT::Periodic::Update-Package-Lists "1";' | sudo tee /etc/apt/apt.conf.d/20auto-upgrades
echo 'APT::Periodic::Unattended-Upgrade "1";' | sudo tee -a /etc/apt/apt.conf.d/20auto-upgrades

# 6. Disable unused services
sudo systemctl disable bluetooth
sudo systemctl disable avahi-daemon

echo "Security hardening completed. Please reboot."
```

## 🚨 Security Incident Response

### Suspected Unauthorized Access
1. **Immediate Actions**
   - Check system logs: `sudo journalctl -u photo-frame.service --since "24 hours ago"`
   - Review access logs for unusual patterns
   - Check for new files: `find /home/pi/photo_frame -type f -mtime -1`

2. **Investigation**
   - Check network connections: `netstat -tulpn`
   - Review user accounts: `cat /etc/passwd`
   - Check for scheduled tasks: `crontab -l && sudo crontab -l`

3. **Response**
   - Change passwords immediately
   - Restart services: `sudo systemctl restart photo-frame`
   - Update system: `sudo apt update && sudo apt upgrade`

### File Upload Abuse
1. **Detection**
   - Monitor upload frequency
   - Check file sizes and types
   - Review disk usage: `df -h`

2. **Mitigation**
   - Enable rate limiting
   - Implement authentication
   - Clear uploads: `rm -f /home/pi/photo_frame/uploads/*`

## 📋 Security Checklist

### Pre-Deployment Security
- [ ] Change default passwords
- [ ] Configure SSH key authentication
- [ ] Enable firewall with minimal rules
- [ ] Install security updates
- [ ] Disable unnecessary services
- [ ] Configure secure logging

### Runtime Security
- [ ] Monitor access logs regularly
- [ ] Check for system updates monthly
- [ ] Review uploaded files periodically
- [ ] Monitor network traffic
- [ ] Backup configuration files

### Incident Response
- [ ] Document security incidents
- [ ] Have recovery plan ready
- [ ] Know how to restore from backup
- [ ] Have emergency contacts available

## 🎯 Security Maturity Levels

### Level 1: Basic (Current)
- File type validation
- Basic error handling
- Non-root execution

### Level 2: Enhanced (Recommended)
- Authentication required
- HTTPS encryption
- Rate limiting
- Input sanitization

### Level 3: Advanced (High Security)
- Certificate-based authentication
- Network segmentation
- Intrusion detection
- Regular security audits

## 📚 Security Resources

- [Raspberry Pi Security Guide](https://www.raspberrypi.org/documentation/configuration/security.md)
- [OWASP IoT Security](https://owasp.org/www-project-iot-security-verification-standard/)
- [Node.js Security Checklist](https://blog.risingstack.com/node-js-security-checklist/)
- [Linux Security Hardening](https://github.com/trimstray/the-practical-linux-hardening-guide)

---

## Summary

This security audit identifies key vulnerabilities and provides actionable hardening recommendations. Implementing Level 2 security measures is recommended for most deployments, with Level 3 for high-security environments.