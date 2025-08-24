#!/bin/bash

# Hardware Integration Validation Script
# Automated testing for Raspberry Pi + Waveshare e-ink display

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Test results
TESTS_PASSED=0
TESTS_FAILED=0
TEST_RESULTS=()

log_test() {
    local test_name="$1"
    local result="$2"
    local details="$3"
    
    if [ "$result" = "PASS" ]; then
        echo -e "${GREEN}✓${NC} $test_name"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}✗${NC} $test_name - $details"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
    
    TEST_RESULTS+=("$test_name: $result")
}

run_test() {
    local test_name="$1"
    local test_command="$2"
    
    echo -e "${BLUE}Testing:${NC} $test_name"
    
    if eval "$test_command" >/dev/null 2>&1; then
        log_test "$test_name" "PASS"
    else
        log_test "$test_name" "FAIL" "Command failed: $test_command"
    fi
}

# Test 1: Hardware Detection
echo -e "${YELLOW}=== Hardware Detection Tests ===${NC}"

run_test "Raspberry Pi Detection" "grep -q 'Raspberry Pi' /proc/cpuinfo"
run_test "SPI Interface Available" "ls /dev/spi* | grep -q spidev"
run_test "GPIO Available" "test -d /sys/class/gpio"
run_test "I2C Available" "test -c /dev/i2c-1"

# Test 2: Software Dependencies
echo -e "${YELLOW}=== Software Dependencies ===${NC}"

run_test "Python3 Available" "python3 --version"
run_test "Bun Runtime Available" "/home/pi/.bun/bin/bun --version"
run_test "PIL/Pillow Installed" "python3 -c 'import PIL'"
run_test "psutil Installed" "python3 -c 'import psutil'"
run_test "Sharp Module Available" "cd /home/pi/photo_frame && bun run -e 'require(\"sharp\")'"

# Test 3: Service Configuration
echo -e "${YELLOW}=== Service Configuration ===${NC}"

run_test "Service File Exists" "test -f /etc/systemd/system/photo-frame.service"
run_test "Service Enabled" "systemctl is-enabled photo-frame.service | grep -q enabled"
run_test "Uploads Directory Exists" "test -d /home/pi/photo_frame/uploads"
run_test "Display Scripts Executable" "test -x /home/pi/photo_frame/display/display_manager.py"

# Test 4: Display Hardware
echo -e "${YELLOW}=== Display Hardware Tests ===${NC}"

# Test display manager initialization
if python3 /home/pi/photo_frame/display/display_manager.py test >/dev/null 2>&1; then
    log_test "Display Manager Initialization" "PASS"
else
    log_test "Display Manager Initialization" "FAIL" "Display test failed"
fi

# Test SPI communication
if python3 -c "
import spidev
try:
    spi = spidev.SpiDev()
    spi.open(0, 0)
    spi.close()
    print('SPI OK')
except Exception as e:
    print(f'SPI Error: {e}')
    exit(1)
" >/dev/null 2>&1; then
    log_test "SPI Communication" "PASS"
else
    log_test "SPI Communication" "FAIL" "SPI not working"
fi

# Test 5: Web Service
echo -e "${YELLOW}=== Web Service Tests ===${NC}"

# Start service if not running
if ! systemctl is-active --quiet photo-frame.service; then
    echo "Starting photo-frame service..."
    sudo systemctl start photo-frame.service
    sleep 5
fi

run_test "Service Running" "systemctl is-active --quiet photo-frame.service"
run_test "Web Server Responding" "curl -s http://localhost:3000/api/status | grep -q success"
run_test "API Endpoints Available" "curl -s http://localhost:3000/api/photo | grep -q success"

# Test 6: Performance Validation
echo -e "${YELLOW}=== Performance Tests ===${NC}"

# Create performance report
if python3 /home/pi/photo_frame/performance_monitor.py --benchmark >/tmp/benchmark.json 2>/dev/null; then
    PROCESSING_TIME=$(cat /tmp/benchmark.json | jq -r '.processing_time_seconds')
    if (( $(echo "$PROCESSING_TIME < 15" | bc -l) )); then
        log_test "Image Processing Performance" "PASS"
    else
        log_test "Image Processing Performance" "FAIL" "Too slow: ${PROCESSING_TIME}s"
    fi
else
    log_test "Performance Benchmark" "FAIL" "Benchmark failed to run"
fi

# Check memory usage
MEMORY_PERCENT=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100.0}')
if [ "$MEMORY_PERCENT" -lt 80 ]; then
    log_test "Memory Usage Normal" "PASS"
else
    log_test "Memory Usage Normal" "FAIL" "High memory usage: ${MEMORY_PERCENT}%"
fi

# Check temperature
if command -v vcgencmd >/dev/null 2>&1; then
    TEMP=$(vcgencmd measure_temp | grep -o '[0-9]\+\.[0-9]\+')
    if (( $(echo "$TEMP < 70" | bc -l) )); then
        log_test "Operating Temperature" "PASS"
    else
        log_test "Operating Temperature" "FAIL" "High temperature: ${TEMP}°C"
    fi
else
    log_test "Temperature Monitoring" "SKIP" "vcgencmd not available"
fi

# Test 7: End-to-End Workflow
echo -e "${YELLOW}=== End-to-End Workflow Test ===${NC}"

# Create test image
python3 -c "
from PIL import Image
img = Image.new('RGB', (800, 600), 'blue')
img.save('/tmp/hardware_test.jpg', 'JPEG')
" >/dev/null 2>&1

if [ -f /tmp/hardware_test.jpg ]; then
    log_test "Test Image Creation" "PASS"
    
    # Test photo upload
    if curl -s -X POST -F "photo=@/tmp/hardware_test.jpg" http://localhost:3000/api/photo | grep -q success; then
        log_test "Photo Upload API" "PASS"
        
        # Wait for display update
        sleep 3
        
        # Check if photo is in system
        if curl -s http://localhost:3000/api/photo | grep -q filename; then
            log_test "Photo Storage" "PASS"
        else
            log_test "Photo Storage" "FAIL" "Photo not found in system"
        fi
        
        # Test photo deletion
        if curl -s -X DELETE http://localhost:3000/api/photo | grep -q success; then
            log_test "Photo Deletion" "PASS"
        else
            log_test "Photo Deletion" "FAIL" "Delete API failed"
        fi
    else
        log_test "Photo Upload API" "FAIL" "Upload failed"
    fi
    
    # Cleanup
    rm -f /tmp/hardware_test.jpg
else
    log_test "Test Image Creation" "FAIL" "Could not create test image"
fi

# Generate Report
echo -e "\n${YELLOW}=== Hardware Validation Report ===${NC}"
echo "Date: $(date)"
echo "Hardware: $(cat /proc/cpuinfo | grep Model | cut -d':' -f2 | xargs)"
echo "OS: $(cat /etc/os-release | grep PRETTY_NAME | cut -d'=' -f2 | tr -d '\"')"
echo "Kernel: $(uname -r)"

if command -v vcgencmd >/dev/null 2>&1; then
    echo "Temperature: $(vcgencmd measure_temp)"
fi

echo "Memory: $(free -h | grep Mem | awk '{print $3 "/" $2}')"
echo "Disk: $(df -h / | tail -1 | awk '{print $3 "/" $2 " (" $5 " used)"}')"

echo -e "\n${YELLOW}Test Results:${NC}"
echo "Passed: ${GREEN}$TESTS_PASSED${NC}"
echo "Failed: ${RED}$TESTS_FAILED${NC}"
echo "Total:  $((TESTS_PASSED + TESTS_FAILED))"

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "\n${GREEN}✓ All hardware validation tests passed!${NC}"
    echo -e "${GREEN}✓ System is ready for production use.${NC}"
    exit 0
else
    echo -e "\n${RED}✗ Some tests failed. Check the issues above.${NC}"
    echo -e "${YELLOW}Refer to HARDWARE_TEST.md for troubleshooting guidance.${NC}"
    exit 1
fi