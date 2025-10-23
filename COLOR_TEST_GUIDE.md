# Color Optimization Testing Guide

This guide provides step-by-step instructions to verify that the color optimization enhancements are working correctly on your Waveshare E Ink Spectra 6 display.

## Color Palette Information

The system uses **hardware-optimized color values** based on research from the EPF project. These values account for how actual e-ink hardware renders colors:

**Core Colors Used**:
- **Black**: RGB(0, 0, 0)
- **White**: RGB(255, 255, 255)
- **Red**: RGB(191, 0, 0) ← Adjusted from pure (255, 0, 0)
- **Yellow**: RGB(255, 243, 56) ← Adjusted from pure (255, 255, 0)
- **Green**: RGB(67, 138, 28) ← Adjusted from pure (0, 128, 0)
- **Blue**: RGB(100, 64, 255) ← Adjusted from pure (0, 0, 255)

Using adjusted values provides better color fidelity on the actual display compared to theoretical RGB values.

## Quick Start: Test Color Display

### Option 1: Local Development Testing (Fastest)

If you're running the system locally in development mode with mock display:

```bash
# Start development server
bun dev

# Open browser and access the upload page
open http://localhost:3000
```

Then proceed to the "Upload Test Image" section below.

### Option 2: Raspberry Pi Testing (Production)

For testing on actual Raspberry Pi hardware with display:

```bash
# SSH into Pi
ssh pi@YOUR_PI_IP

# Check service status
sudo systemctl status photo-frame.service

# If not running, start it
sudo systemctl start photo-frame.service

# Access web interface from phone/laptop
# Open browser: http://<YOUR_PI_IP>:3000
```

Then proceed to the "Upload Test Image" section below.

## Test 1: Pure Color Test Image

This test verifies that all 6 core colors appear distinctly.

### Step 1: Create Test Image

On the Pi or development machine, run:

```bash
python3 << 'EOF'
from PIL import Image, ImageDraw

# Create 800x480 image (display resolution)
img = Image.new('RGB', (800, 480), 'white')
draw = ImageDraw.Draw(img)

# Hardware-optimized E Ink Spectra 6 colors
# Based on EPF project research - these map better to actual hardware
colors = {
    'BLACK': ((0, 0, 0), 'white'),           # Black
    'WHITE': ((255, 255, 255), 'black'),     # White
    'RED': ((191, 0, 0), 'white'),           # Red (adjusted)
    'YELLOW': ((255, 243, 56), 'black'),     # Yellow (adjusted)
    'GREEN': ((67, 138, 28), 'white'),       # Green (adjusted)
    'BLUE': ((100, 64, 255), 'white'),       # Blue (adjusted)
}

# Draw rectangles for each core color
x_positions = [0, 133, 266, 399, 532, 665]
x = 0
for i, (name, (color, text_color)) in enumerate(colors.items()):
    x1 = x_positions[i]
    x2 = x_positions[i] if i == 5 else x_positions[i+1]
    draw.rectangle([(x1, 0), (x2, 240)], fill=color)
    draw.text((x1 + 20, 100), name, fill=text_color)

# Bottom half: Grayscale gradient
for x in range(800):
    gray = int(255 * x / 800)
    draw.rectangle([(x, 240), (x+1, 480)], fill=(gray, gray, gray))

img.save('color_test.jpg', 'JPEG')
print("✓ Created color_test.jpg with hardware-optimized palette")
EOF
```

### Step 2: Upload Image

**Development Mode** (mock display):
```bash
curl -X POST -F "photo=@color_test.jpg" http://localhost:3000/api/photo
```

**Raspberry Pi**:
```bash
curl -X POST -F "photo=@color_test.jpg" http://YOUR_PI_IP:3000/api/photo
```

Or use the web interface: drag & drop `color_test.jpg` onto the upload area.

### Step 3: Verify Results

Check the logs for optimization details:

```bash
# On Pi:
tail -50 /tmp/display_manager.log | grep -E "Step|Contrast|saturation|dither|palette"

# Expected output:
# [INFO] Step 1: Enhancing color separation and contrast
# [INFO] Contrast enhanced by 50%
# [INFO] Color saturation enhanced by 50%
# [INFO] Step 2: Creating extended color palette for better dithering
# [INFO] Created extended palette with 17 color variations
# [INFO] Step 3: Applying Floyd-Steinberg dithering
```

**Visual Inspection**:
- All 6 colors should appear distinct and visible
- Black should be solid black, not gray
- Red, Yellow, Green, Blue should be vibrant
- White should be solid white
- Grayscale gradient at bottom should show gradation from black to white

## Test 2: Colorful Photo Test

### Step 1: Create Multi-Color Test Image

```bash
python3 << 'EOF'
from PIL import Image, ImageDraw

img = Image.new('RGB', (800, 480), 'white')
draw = ImageDraw.Draw(img)

# Create a more complex pattern to test color mixing
colors = {
    'red': (255, 0, 0),
    'green': (0, 128, 0),
    'blue': (0, 0, 255),
    'yellow': (255, 255, 0),
    'magenta': (255, 0, 255),
    'cyan': (0, 255, 255),
    'orange': (255, 165, 0),
    'purple': (128, 0, 128),
}

# Create a grid of colors
cell_width = 100
cell_height = 96

x = 0
for color_name, color_value in colors.items():
    y = 0
    for intensity in [1.0, 0.7, 0.4]:
        r, g, b = color_value
        adjusted = (
            int(r * intensity),
            int(g * intensity),
            int(b * intensity)
        )
        draw.rectangle(
            [(x, y), (x + cell_width, y + cell_height)],
            fill=adjusted
        )
        y += cell_height
    x += cell_width

img.save('color_grid_test.jpg', 'JPEG')
print("✓ Created color_grid_test.jpg")
EOF
```

### Step 2: Upload and Verify

Upload as in Test 1, then verify:

- Color grid should show all distinct colors
- Intensity variations (full, 70%, 40%) should create perception of different shades
- Dithering pattern should be visible (not just solid colors)

## Test 3: Real Photo Test

### Step 1: Prepare a Colorful Photo

Use a real photo with:
- Distinct color regions (landscape with blue sky, green trees, brown earth)
- Multiple saturated colors
- Some grayscale areas (white clouds, gray rocks)
- Good contrast

### Step 2: Upload and Evaluate

Upload the photo and observe:

**Good Results** ✅:
- Colors are distinguishable and vivid
- Color transitions are smooth (due to dithering)
- Sky appears distinct from ground
- Different colored objects are visually separable
- No large blocks of solid colors

**Poor Results** ❌:
- Image appears mostly black and white
- Colors are barely visible
- All colored regions blend together
- Looks like a poor quality grayscale conversion

If you see poor results, consult the "Troubleshooting" section below.

## Test 4: Performance Benchmarking

### Step 1: Monitor Processing Time

Create a test to measure processing time:

```bash
# On Pi, run:
time curl -X POST -F "photo=@color_test.jpg" http://localhost:3000/api/photo

# On development machine, run in another terminal while uploading:
watch -n 0.5 'ps aux | grep -i sharp'  # Monitor Sharp processing
```

### Step 2: Verify Timing

**Expected Processing Time**:
- Server-side Sharp processing: ~1-2 seconds
- Display manager optimization: ~1-2 seconds
- Display update to e-ink: 30-40 seconds (this is hardware limitation)

**Total upload to display**: ~35-45 seconds

If processing takes significantly longer (>5 seconds), check:
- CPU usage and temperature
- Available memory
- Check if system is low-memory optimized

## Test 5: Extended Palette Verification

### Verify Palette is Extended

Check that the extended palette is being created:

```bash
# Watch the logs while uploading
tail -f /tmp/display_manager.log | grep -i "palette\|color"

# You should see:
# Created extended palette with 17 color variations
# Applying Floyd-Steinberg dithering
```

If you see:
- "Created extended palette with 6 color variations" → Only core colors used
- "No extended palette" → Error in palette creation

Then review the display_manager.py file and ensure the palette code is properly implemented.

## Troubleshooting

### Problem: Display Still Shows Mostly Black and White

**Check Log Output**:
```bash
tail -100 /tmp/display_manager.log | grep -i "step\|contrast\|saturation"
```

**If you don't see enhancement messages**:
1. Verify display_manager.py has the enhancement code (lines 253-268)
2. Ensure the image is in RGB mode (should be logged)
3. Check for errors in the logs

**If enhancement messages are there but colors still poor**:
1. Try increasing saturation further (test in display_manager.py)
2. Reduce contrast if image appears too washed out
3. Test with a pure color test image first (Test 1)

### Problem: Processing Time is Very Long

**Check**:
```bash
# Monitor resource usage
free -h  # Check available memory
top     # Check CPU usage
vcgencmd measure_temp  # Check temperature

# Check if system is low-memory
grep "is_low_memory" /tmp/display_manager.log
```

**Solutions**:
- Reduce extended palette size in display_manager.py
- Use NEAREST resampling instead of LANCZOS
- Enable swap if memory is limited
- Check for CPU throttling due to heat

### Problem: Colors Appear Washed Out or Faded

**Solutions**:
1. Verify saturation is set to 1.8 in src/server/app.ts (line 209)
2. Check that contrast enhancement is enabled in display_manager.py
3. Try reducing contrast boost from 1.5 to 1.2 if colors are blown out
4. Verify JPEG quality is 95+ (not compressed)

### Problem: Web Upload Works, But Display Doesn't Update

**Check**:
1. Verify display is initialized: `sudo systemctl status photo-frame.service`
2. Check for display hardware errors: `tail -50 /tmp/display_manager.log | grep -i error`
3. Test display directly:
   ```bash
   source ~/photo_frame/venv/bin/activate
   cd ~/photo_frame/display
   python3 display_manager.py test
   ```

## Performance Tuning Options

If the standard configuration doesn't give desired results, try these tuning options:

### For Better Color Intensity

**In src/server/app.ts** (line 209):
```typescript
saturation: 2.0,  // Increase from 1.8 to 2.0
```

**In display/display_manager.py** (line 267):
```python
background = enhancer.enhance(2.0)  # Increase from 1.5 to 2.0
```

### For Better Contrast

**In display/display_manager.py** (line 262):
```python
background = enhancer.enhance(2.0)  # Increase from 1.5 to 2.0
```

Or add more negation iterations in src/server/app.ts.

### For Faster Processing

**In display/display_manager.py** (line 312):
```python
extended_palette[:100]  # Reduce from 240 colors
```

### For Better Dithering

Try different approaches in display/display_manager.py:
```python
# Current: Floyd-Steinberg
quantized_image = background.quantize(
    palette=palette_image,
    dither=Image.FLOYDSTEINBERG
)

# Alternative: Ordered dithering
quantized_image = background.quantize(
    palette=palette_image,
    dither=Image.ORDERED
)
```

## Expected Behavior Summary

### What's Working ✅
- Images upload successfully
- Server processes images without errors
- Display updates (30-40 second refresh time)
- All 6 core colors are achievable
- Extended palette enables dithering

### What's Inherent to 6-Color Display
- No true gradients, only dithered pseudo-gradients
- Limited color accuracy (no pastels or light tints)
- Best results with images of distinct color regions
- Dithering pattern visible when zoomed in
- Grayscale and low-contrast images appear mostly B&W

### Color Optimization Benefits
- More vivid colors than standard palette quantization
- Better color separation due to extended palette
- Smoother transitions due to Floyd-Steinberg dithering
- Optimized for Raspberry Pi Zero resource constraints

## Next Steps

If all tests pass:
1. Document your setup and any custom tuning
2. Test with various real-world photos
3. Monitor system temperature and performance over time
4. Consider creating additional test images for specific use cases

If tests show room for improvement:
1. Note specific colors that don't display well
2. Try tuning saturation/contrast values
3. Experiment with different image types
4. Consider providing feedback for further optimization

## Reference

For more detailed information about the color processing pipeline, see [COLOR_OPTIMIZATION.md](COLOR_OPTIMIZATION.md).

For hardware integration testing, see [HARDWARE_TEST.md](HARDWARE_TEST.md).
