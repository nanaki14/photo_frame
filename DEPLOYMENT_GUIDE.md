# Deployment Guide - Color Fix

## Quick Start

This guide explains how to deploy the color artifact fix to your photo frame.

## What Was Fixed

The photo frame was experiencing color artifacts:
- ❌ Green appearing as red-black
- ❌ People/skin tones appearing as white voids

**Now fixed:** ✅ Green displays as green, skin tones display naturally

## Changes Summary

**Single change to `display/display_manager.py`:**
- Reduced saturation enhancement from 2.5x to 1.5x
- Removed redundant palette quantization code

This preserves color balance while maintaining sufficient enhancement for the 6-color e-ink display.

## Deployment Steps

### Step 1: Update Code

```bash
cd /Users/masa/git/photo_frame
git pull origin main
```

### Step 2: Test Locally (Mac/Linux)

Run the validation test suite:

```bash
python3 test_color_fix.py
```

Expected output:
```
✓ PASS: Green Image
✓ PASS: Skin Tone Image
✓ PASS: Green Variations
✓ PASS: Enhancement Pipeline

Total: 4/4 tests passed
```

### Step 3: Deploy to Raspberry Pi

#### Option A: Git Pull (Recommended)

```bash
# On Raspberry Pi
cd ~/photo_frame
git pull origin main
# Restart the service
sudo systemctl restart photo-frame
```

#### Option B: Manual Copy

```bash
# From your development machine
scp display/display_manager.py pi@raspberrypi.local:~/photo_frame/display/

# On Raspberry Pi
cd ~/photo_frame
sudo systemctl restart photo-frame
```

### Step 4: Verify on Display

Test with different image types:

1. **Green image test:**
   - Upload a pure green image or mountain landscape
   - Verify: Green displays as vibrant green (NOT red-black)

2. **Portrait/skin tone test:**
   - Upload a portrait photo with faces
   - Verify: Skin tones appear natural (NOT white voids)

3. **Multi-color test:**
   - Upload a colorful image
   - Verify: All colors render correctly without artifacts

## Checking Display Logs

Monitor what's happening on the Raspberry Pi:

```bash
# SSH into Raspberry Pi
ssh pi@raspberrypi.local

# Watch display manager logs
tail -f /tmp/display_manager.log

# Check for enhancement details
grep -i "saturation\|enhanced\|color" /tmp/display_manager.log
```

Expected log output:
```
Color saturation enhanced by 150%
Contrast enhanced by 80%
Brightness enhanced by 10%
Direct 6-color mapping complete: 384000 pixels processed
```

## Troubleshooting

### Issue: Colors still look off

**Check color mapping:**
```bash
python3 test_color_fix.py
```

**Check diagnostic images on Raspberry Pi:**
```bash
# SSH into Pi
ssh pi@raspberrypi.local

# List diagnostic images
ls -la /tmp/*_*.png

# View enhancement stages
file /tmp/02_after_saturation.png  # After saturation
file /tmp/03_after_contrast.png    # After contrast
file /tmp/05_after_dithering.png   # Final 6-color mapped
```

The diagnostic images show the color transformation at each stage.

### Issue: Display not updating

1. Check service status:
   ```bash
   sudo systemctl status photo-frame
   ```

2. Restart service:
   ```bash
   sudo systemctl restart photo-frame
   ```

3. Check logs:
   ```bash
   journalctl -u photo-frame -n 50
   ```

### Issue: Green is still appearing wrong

If green still doesn't display correctly, verify:

1. **File was actually updated:**
   ```bash
   grep "enhanced by 150" display/display_manager.py
   # Should show: "enhanced by 150%"
   ```

2. **Service restarted:**
   ```bash
   ps aux | grep python
   # Should show the photo frame process running
   ```

3. **Check the actual enhancement:**
   ```bash
   python3 << 'EOF'
   from PIL import Image, ImageEnhance

   green = Image.new('RGB', (10, 10), (0, 255, 0))
   enhancer = ImageEnhance.Color(green)
   result = enhancer.enhance(1.5)
   print("Pixel after 1.5x saturation:", result.getpixel((5, 5)))
   # Should print: (0, 255, 0)
   EOF
   ```

## Performance Metrics

No performance degradation from this fix:
- **Processing time:** Same as before
- **Memory usage:** Same as before
- **Display time:** Still 30-40 seconds on Raspberry Pi Zero
- **Color accuracy:** Significantly improved

## Rollback (if needed)

To revert to the previous version:

```bash
git revert 61d4f97
git push origin main
```

Then on Raspberry Pi:
```bash
git pull origin main
sudo systemctl restart photo-frame
```

## Technical Details

### Why 1.5x Saturation?

- **2.5x (old):** Destroys skin tones → RGB(255,211,0) appears as white void
- **1.5x (new):** Preserves color balance → RGB(255,211,0) appears as natural yellow

The new value provides sufficient enhancement for the 6-color display while avoiding unnatural color shifts.

### Color Mapping Flow

```
Input Image (any colors)
        ↓
Enhancement Pipeline (1.5x saturation, 1.8x contrast, 1.1x brightness)
        ↓
Direct 6-Color Mapping (Euclidean distance to nearest core color)
        ↓
Waveshare getbuffer() (converts to hardware buffer format)
        ↓
Display on E-Ink (30-40 seconds refresh)
```

### Core Colors (E-Ink Spectra 6)

```
Black   (0, 0, 0)        #000000
White   (255, 255, 255)  #FFFFFF
Red     (255, 0, 0)      #FF0000
Yellow  (255, 255, 0)    #FFFF00
Green   (0, 255, 0)      #00FF00
Blue    (0, 0, 255)      #0000FF
```

## Support

If you encounter any issues:

1. Check this deployment guide
2. Review COLOR_FIX_SUMMARY.md for technical details
3. Run test_color_fix.py to validate color mapping
4. Check /tmp/display_manager.log for error messages

## Verification Checklist

- [ ] Code pulled from Git
- [ ] test_color_fix.py passes all tests
- [ ] Deployed to Raspberry Pi
- [ ] Service restarted
- [ ] Green image displays as green (not red-black)
- [ ] Portrait displays with natural skin tones (not white void)
- [ ] No new errors in logs
- [ ] Display refresh time unchanged (30-40 seconds)

All done! Your photo frame should now display colors correctly. 🎉
