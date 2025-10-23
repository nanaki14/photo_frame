#!/bin/bash
# Test display script execution

echo "=========================================="
echo "Display Script Diagnostic Test"
echo "=========================================="
echo

# Check Python
echo "1. Checking Python..."
which python3
python3 --version
echo

# Check dependencies
echo "2. Checking Python dependencies..."
python3 -c "import numpy; print(f'numpy: {numpy.__version__}')" 2>&1
python3 -c "import PIL; print(f'PIL: {PIL.__version__}')" 2>&1
python3 -c "import psutil; print(f'psutil: {psutil.__version__}')" 2>&1
echo

# Check script paths
echo "3. Checking script paths..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "Script dir: $SCRIPT_DIR"
echo "display_manager.py: $(ls -lh $SCRIPT_DIR/display/display_manager.py 2>&1)"
echo "update_display.py: $(ls -lh $SCRIPT_DIR/display/update_display.py 2>&1)"
echo

# Check for test image
echo "4. Checking for test images..."
if [ -f "/tmp/test_simple_red.jpg" ]; then
    TEST_IMAGE="/tmp/test_simple_red.jpg"
    echo "Found test image: $TEST_IMAGE"
elif [ -f "$SCRIPT_DIR/uploads/photo.jpg" ]; then
    TEST_IMAGE="$SCRIPT_DIR/uploads/photo.jpg"
    echo "Found uploaded image: $TEST_IMAGE"
else
    echo "No test image found, creating one..."
    python3 -c "
from PIL import Image
img = Image.new('RGB', (800, 480), color=(255, 0, 0))
img.save('/tmp/test_red.jpg')
print('Created: /tmp/test_red.jpg')
"
    TEST_IMAGE="/tmp/test_red.jpg"
fi
echo

# Test display script
echo "5. Testing display script..."
echo "Command: python3 $SCRIPT_DIR/display/update_display.py $TEST_IMAGE"
echo
python3 "$SCRIPT_DIR/display/update_display.py" "$TEST_IMAGE"
RESULT=$?
echo
echo "Exit code: $RESULT"
echo

# Check logs
echo "6. Checking logs..."
if [ -f "/tmp/update_display.log" ]; then
    echo "Last 20 lines of /tmp/update_display.log:"
    tail -20 /tmp/update_display.log
else
    echo "No log file found at /tmp/update_display.log"
fi
echo

if [ -f "/tmp/display_manager.log" ]; then
    echo "Last 20 lines of /tmp/display_manager.log:"
    tail -20 /tmp/display_manager.log
else
    echo "No log file found at /tmp/display_manager.log"
fi
echo

# Check diagnostic images
echo "7. Checking diagnostic images..."
ls -lh /tmp/01_original_image.png 2>&1
ls -lh /tmp/02_dithered_image.png 2>&1
echo

echo "=========================================="
echo "Test complete!"
echo "=========================================="
