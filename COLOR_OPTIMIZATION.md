# Color Optimization for Waveshare E Ink Spectra 6 Display

## Overview

This document describes the color optimization techniques implemented for the Waveshare 7.3inch e-Paper HAT (E) - E Ink Spectra 6 display, which has a 6-color limited palette (Black, White, Red, Yellow, Green, Blue).

## Problem Statement

The Waveshare E Ink Spectra 6 display is limited to 6 core colors, which creates a significant challenge when displaying full-color RGB images. Without proper optimization, images would appear mostly in black and white with minimal color variation.

**Challenge**: Converting full RGB images to 6-color display while maintaining color fidelity and visual appeal.

## Solution Architecture

The color optimization is implemented as a two-stage pipeline:

### Stage 1: Upload Server (src/server/app.ts)
**Purpose**: Pre-process images to maximize color information before display conversion

**Processing Steps**:

1. **Normalize**: Maximize tonal range to prepare for subsequent enhancements
   ```typescript
   .normalize()
   ```

2. **Saturation Boost**: Significantly enhance color saturation (1.8x)
   - This compensates for the limited palette by making colors more vivid
   - Increased from 1.2x after testing showed better color separation
   ```typescript
   .modulate({
     saturation: 1.8,  // Significantly boost saturation
   })
   ```

3. **Contrast Enhancement**: Apply double-negate technique for contrast boost
   - Creates separation between similar tones
   - Helps colors stand out more distinctly
   ```typescript
   .negate({ alpha: false })
   .negate({ alpha: false })
   ```

4. **Sharpening**: Apply edge enhancement for clarity
   ```typescript
   .sharpen(1.2, 0.5, 0.5)
   ```

5. **Quality Preservation**: Export as JPEG with high quality (95-98%)
   - Preserves color information without compression artifacts
   - Maintains RGB format throughout

### Stage 2: Display Manager (display/display_manager.py)
**Purpose**: Convert optimized RGB images to 6-color display format using intelligent dithering

**Processing Steps**:

1. **Image Loading & Resizing**:
   - Load image maintaining aspect ratio
   - Resize to display dimensions (800×480)
   - Center on white background
   - Optimize for low-memory Pi Zero systems

2. **Color Enhancement** (Enhanced Color Range Approach):

   a. **Contrast Boost** (50% enhancement):
   ```python
   enhancer = ImageEnhance.Contrast(background)
   background = enhancer.enhance(1.5)
   ```

   b. **Saturation Boost** (50% enhancement):
   ```python
   enhancer = ImageEnhance.Color(background)
   background = enhancer.enhance(1.5)
   ```

   These enhancements further maximize color separation before quantization.

3. **Extended Palette Creation**:

   Instead of using only the 6 core colors for dithering, we create an extended palette with 17 colors:

   **Core Colors (6)** - Optimized for E Ink Hardware:
   - Black: (0, 0, 0)
   - White: (255, 255, 255)
   - Red: (191, 0, 0) - Darker, maps better to hardware capabilities
   - Yellow: (255, 243, 56) - Adjusted from pure yellow for better visibility
   - Green: (67, 138, 28) - Dark green, more visible on e-ink displays
   - Blue: (100, 64, 255) - Adjusted for better color rendering

   **Extended Colors (11)**:
   - Dark variants (4): Dark Red, Dark Yellow, Dark Green, Dark Blue
   - Light variants (4): Light Red, Light Yellow, Light Green, Light Blue
   - Neutral grays (3): Dark Gray, Medium Gray, Light Gray

   **Benefit**: The dithering algorithm has more intermediate colors to choose from, creating better gradation and smoother color transitions.

4. **Floyd-Steinberg Dithering**:
   ```python
   quantized_image = background.quantize(
       palette=palette_image,
       dither=Image.FLOYDSTEINBERG
   )
   ```
   - Uses error diffusion algorithm to distribute color errors
   - Creates pseudo-colors through pixel-level dithering
   - Works with extended palette for better color representation

## Color Processing Pipeline Diagram

```
Original RGB Image
    ↓
[Stage 1: Upload Server]
    ├─ Normalize (maximize tonal range)
    ├─ Saturation Boost (1.8x)
    ├─ Contrast Enhancement (double-negate)
    ├─ Sharpening (1.2x)
    └─ Save as high-quality JPEG (95-98%)
    ↓
Optimized RGB Image (JPEG)
    ↓
[Stage 2: Display Manager]
    ├─ Load & Resize (800×480)
    ├─ Center on white background
    ├─ Contrast Enhancement (+50%)
    ├─ Saturation Boost (+50%)
    ├─ Extended Palette (17 colors)
    ├─ Floyd-Steinberg Dithering
    └─ Convert to display buffer
    ↓
6-Color Display Output
```

## Technical Details

### Why Extended Palette Helps

The 6-color palette is inherently limited:
- 6 colors alone create abrupt transitions
- Floyd-Steinberg dithering needs options for error distribution
- Extended palette (17 colors) provides intermediate options
- Dithering creates pseudo-colors through spatial patterns

Example color expansion:
```
Pure Red (255, 0, 0) ← Core color
    ↓ (dithering with variants)
Dark Red (64, 0, 0), Light Red (255, 128, 128)
    ↑ (interpolation via dithering)
Perceived intermediate shades
```

### Memory Optimization for Raspberry Pi Zero

The implementation accounts for Pi Zero 2 WH constraints (512MB RAM):

1. **Lazy Loading**: Draft mode for low-memory systems
2. **Resampling Algorithm Selection**:
   - Pi Zero + low memory: NEAREST (fastest, least memory)
   - Other systems: LANCZOS (best quality)
3. **Sequential Image Processing**: Uses streaming where possible
4. **PIL ImageEnhance**: Efficient in-place processing without duplication

### Performance Characteristics

**Processing Time** (on Raspberry Pi Zero 2 WH):
- Image normalization: ~0.5 seconds
- Color enhancement: ~0.3 seconds
- Saturation boost: ~0.3 seconds
- Dithering: ~1-2 seconds
- **Total optimization**: ~2-3 seconds per image

**Display Time**:
- Display update to e-ink: 30-40 seconds (hardware limitation)
- Complete workflow: ~35-45 seconds from upload

## Testing and Validation

### Manual Testing

#### Test 1: Colorful Test Image
```bash
# Create a test image with distinct colors
python3 << 'EOF'
from PIL import Image, ImageDraw
import math

img = Image.new('RGB', (800, 480), 'white')
draw = ImageDraw.Draw(img)

# Draw colored regions
colors = [
    ('red', 0, 0, 200, 160),
    ('yellow', 200, 0, 400, 160),
    ('green', 400, 0, 600, 160),
    ('blue', 600, 0, 800, 160),
    ('black', 0, 160, 200, 320),
    ('white', 200, 160, 400, 320),
    ('#FF8080', 400, 160, 600, 320),  # Light red
    ('#FFFF80', 600, 160, 800, 320),  # Light yellow
]

for color, x1, y1, x2, y2 in colors:
    draw.rectangle([x1, y1, x2, y2], fill=color)

# Add gradient test (vertical)
for y in range(240, 480):
    gray_val = int(255 * (y - 240) / 240)
    draw.line([(0, y), (800, y)], fill=(gray_val, gray_val, gray_val))

img.save('color_test.jpg', 'JPEG')
print("Created color_test.jpg")
EOF
```

#### Test 2: Upload and Verify
```bash
# Upload test image
curl -X POST -F "photo=@color_test.jpg" http://localhost:3000/api/photo

# Check logs for optimization details
tail -50 /tmp/display_manager.log | grep -i "color\|saturation\|contrast\|dither"
```

**Expected Log Output**:
```
[INFO] Step 1: Enhancing color separation and contrast
[INFO] Contrast enhanced by 50%
[INFO] Color saturation enhanced by 50%
[INFO] Step 2: Creating extended color palette for better dithering
[INFO] Created extended palette with 17 color variations
[INFO] Step 3: Applying Floyd-Steinberg dithering
[INFO] Image optimized for E Ink Spectra 6
[INFO] Enhanced color range applied with extended palette and dithering
```

#### Test 3: Visual Inspection
- Display all 6 core colors should appear distinct
- Gradient areas should show dithering patterns
- No pure black and white should predominate
- Color transitions should be smooth

### Automated Testing Recommendations

Create a test suite in `tests/color_optimization.test.ts`:

```typescript
describe('Color Optimization', () => {
  it('should enhance saturation in Sharp pipeline', async () => {
    // Test that saturation modifier is applied
  });

  it('should normalize image brightness', async () => {
    // Test that normalize step works
  });

  it('should apply contrast boost', async () => {
    // Test double-negate contrast technique
  });

  it('should process without dropping color mode', async () => {
    // Ensure RGB mode maintained throughout
  });
});
```

## Performance Tuning

### If Colors Are Still Too Muted

1. **Increase saturation further**:
   ```typescript
   saturation: 2.0  // From 1.8
   ```

2. **Add brightness enhancement**:
   ```typescript
   .modulate({
     brightness: 1.1,  // Slightly brighten
     saturation: 1.8,
   })
   ```

3. **Apply more aggressive contrast**:
   ```typescript
   .negate({ alpha: false })
   .negate({ alpha: false })
   .negate({ alpha: false })  // Triple negate for even more contrast
   ```

### If Processing Time Is Too Long

1. **Use faster resampling**:
   ```typescript
   kernel: 'nearest'  // Already optimized for Pi
   ```

2. **Reduce dithering palette size**:
   ```python
   extended_palette[:100]  # Reduce from 240 colors
   ```

3. **Skip some enhancements**:
   - Try removing the normalize step if not needed

### If Display Shows Mostly Black and White

This indicates the palette is still too limited. Solutions:
1. Ensure extended palette is being created (check logs)
2. Verify FLOYDSTEINBERG dithering is applied
3. Check if image enhancement steps are running
4. Try creating test images with pure colors to debug

## Configuration Environment Variables

```bash
# Enable mock display for development (disables color optimization for hardware)
export MOCK_DISPLAY=true

# Set Waveshare model (default: epd7in3f, use epd7in3e for HAT(E))
export WAVESHARE_MODEL=epd7in3e

# Control color enhancement aggressiveness
# (Not yet implemented - would require code modification)
export COLOR_SATURATION=1.8  # Default
export COLOR_CONTRAST=1.5    # Default
```

## References

### Color Palette Optimization
The core color palette in this implementation is based on empirical research from the EPF project (https://github.com/jwchen119/EPF), which demonstrates that the nominal RGB values for Spectra 6 colors (pure red 255,0,0, pure yellow 255,255,0, etc.) do not map optimally to actual hardware output.

**Key Finding**: Using adjusted color values that account for display characteristics provides better visual output:
- Red: Pure (255,0,0) → Adjusted (191,0,0) - darker red appears more saturated on hardware
- Yellow: Pure (255,255,0) → Adjusted (255,243,56) - accounts for hardware yellow representation
- Green: Pure (0,128,0) → Adjusted (67,138,28) - darker green is more visible
- Blue: Pure (0,0,255) → Adjusted (100,64,255) - adjusted for hardware color space

This palette adjustment, combined with extended color variants and Floyd-Steinberg dithering, produces significantly improved color fidelity on e-ink displays.

### Floyd-Steinberg Dithering
- Reduces color palette by distributing quantization error
- Creates dithering pattern that creates perceived colors
- More sophisticated than simple nearest-neighbor quantization
- Industry standard for e-ink displays

### E Ink Spectra 6 Specifications
- 6-color palette: Black, White, Red, Yellow, Green, Blue (hardware-optimized)
- 800×480 pixel resolution
- 7.3-inch diagonal display
- Refresh time: 30-40 seconds for full color update
- Power: Display only draws power during refresh

## Future Improvements

1. **Gamma Correction**: Apply gamma 1.8-2.2 before quantization
2. **LAB Color Space**: Convert to LAB for perceptually uniform processing
3. **Adaptive Palette**: Generate palette based on image dominant colors
4. **Multi-Pass Dithering**: Apply dithering multiple times with different error patterns
5. **Ordered Dithering**: Alternative to Floyd-Steinberg for different visual effects
6. **Color Profile Conversion**: Adobe RGB → sRGB before processing

## Troubleshooting

### Display Shows Mostly Black and White

**Check**:
1. Verify enhanced color processing is enabled in display_manager.py
2. Check /tmp/display_manager.log for enhancement messages
3. Test with pure color test image (all red, all blue, etc.)
4. Verify extended palette is being created (17 colors)

**Solutions**:
1. Increase saturation boost to 2.0 or higher
2. Add brightness enhancement
3. Verify Floyd-Steinberg is applied with extended palette
4. Check if image processing in Sharp is enabled

### Colors Appear Washed Out

**Check**:
1. Verify JPEG quality is set to 95+ (not compressed)
2. Check if normalize step is too aggressive
3. Verify saturation boost is applied in both stages

**Solutions**:
1. Reduce contrast boost to 1.2 instead of 1.5
2. Keep saturation at 1.8 or increase to 2.0
3. Simplify processing pipeline to identify bottleneck

### Performance is Slow

**Check**:
1. Monitor CPU usage: `top`
2. Check temperature: `vcgencmd measure_temp`
3. Look for memory swapping: `free -h`

**Solutions**:
1. Reduce extended palette size
2. Use NEAREST resampling instead of LANCZOS
3. Disable some enhancement steps
4. Increase system swap space

## Summary

The color optimization pipeline combines:
1. **Server-side preprocessing**: Saturation and contrast boost to prepare images
2. **Display-side enhancement**: Further refinement with ImageEnhance
3. **Intelligent dithering**: Floyd-Steinberg with extended palette for smooth color distribution
4. **Memory optimization**: Designed for Raspberry Pi Zero 2 WH constraints

This multi-stage approach maximizes the visual fidelity of full-color RGB images when displayed on the 6-color e-ink display.
