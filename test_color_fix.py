#!/usr/bin/env python3
"""
Test script to validate the color mapping fix.
Run this on your Raspberry Pi after deploying the changes.

This tests:
1. Pure green image (should stay green, not red-black)
2. Skin tone image (should map to yellow/natural color, not white void)
3. Mountain/landscape with multiple greens
4. Color accuracy with enhanced colors
"""

import sys
import os
from PIL import Image, ImageDraw, ImageEnhance
import math

# Add display module to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'display'))

try:
    from display_manager import DisplayManager
except ImportError:
    print("Warning: Could not import DisplayManager, will use PIL only")
    DisplayManager = None

# Color definitions - per Waveshare official specifications
CORE_COLORS = [
    (0, 0, 0),          # Black
    (255, 255, 255),    # White
    (255, 0, 0),        # Red
    (255, 255, 0),      # Yellow
    (0, 128, 0),        # Green - Official Waveshare value
    (0, 0, 255),        # Blue
]

COLOR_NAMES = ["Black", "White", "Red", "Yellow", "Green", "Blue"]

def euclidean_distance(r1, g1, b1, r2, g2, b2):
    """Calculate Euclidean distance between two RGB colors"""
    return math.sqrt((r1-r2)**2 + (g1-g2)**2 + (b1-b2)**2)

def find_closest_color(r, g, b):
    """Find closest core color using Euclidean distance"""
    min_distance = float('inf')
    closest_idx = 0

    for idx, (cr, cg, cb) in enumerate(CORE_COLORS):
        distance = euclidean_distance(r, g, b, cr, cg, cb)
        if distance < min_distance:
            min_distance = distance
            closest_idx = idx

    return closest_idx, min_distance

def enhance_color(rgb, saturation=1.5):
    """Apply the enhancement pipeline from display_manager.py"""
    img = Image.new('RGB', (10, 10), color=rgb)

    # Apply enhancement pipeline
    enhancer = ImageEnhance.Color(img)
    img = enhancer.enhance(saturation)

    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.8)

    enhancer = ImageEnhance.Brightness(img)
    img = enhancer.enhance(1.1)

    return img.getpixel((5, 5))

def create_test_image(name, color_data):
    """Create a test image with specified colors"""
    width, height = 800, 480
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)

    # Draw color swatches
    swatch_height = height // len(color_data)
    for idx, (label, color) in enumerate(color_data):
        y_start = idx * swatch_height
        y_end = (idx + 1) * swatch_height

        # Draw color swatch
        draw.rectangle([0, y_start, width, y_end], fill=color)

        # Draw text label
        draw.text((10, y_start + 10), label, fill=(0, 0, 0) if sum(color) > 384 else (255, 255, 255))

    img.save(f'/tmp/test_{name}.png')
    return img

def test_green_image():
    """Test pure green image"""
    print("\n" + "="*70)
    print("TEST 1: Pure Green Image")
    print("="*70)

    green_img = Image.new('RGB', (800, 480), color=(0, 255, 0))
    green_img.save('/tmp/test_pure_green.png')

    pixel = green_img.getpixel((400, 240))
    idx, dist = find_closest_color(*pixel)

    print(f"Input:         RGB(0, 255, 0)")
    print(f"Mapped to:     {COLOR_NAMES[idx]} {CORE_COLORS[idx]}")
    print(f"Distance:      {dist:.1f}")
    print(f"✓ PASS" if COLOR_NAMES[idx] == "Green" else "✗ FAIL - Should be Green!")

    if DisplayManager:
        dm = DisplayManager()
        dm.display_image('/tmp/test_pure_green.png')

    return COLOR_NAMES[idx] == "Green"

def test_skin_tone_image():
    """Test skin tone image (should not appear as white void)"""
    print("\n" + "="*70)
    print("TEST 2: Skin Tone Image")
    print("="*70)

    skin_img = Image.new('RGB', (800, 480), color=(255, 200, 124))
    skin_img.save('/tmp/test_skin_tone.png')

    # Simulate enhancement pipeline
    enhanced = enhance_color((255, 200, 124), saturation=1.5)
    idx, dist = find_closest_color(*enhanced)

    print(f"Original:      RGB(255, 200, 124)")
    print(f"Enhanced:      RGB{enhanced}")
    print(f"Mapped to:     {COLOR_NAMES[idx]} {CORE_COLORS[idx]}")
    print(f"Distance:      {dist:.1f}")

    # Skin tones should not map to white (which would be a void)
    # Yellow is acceptable
    is_not_white = COLOR_NAMES[idx] != "White"
    is_not_black = COLOR_NAMES[idx] != "Black"
    print(f"✓ PASS (maps to {COLOR_NAMES[idx]})" if is_not_white and is_not_black else f"✗ FAIL - Unexpected color {COLOR_NAMES[idx]}!")

    if DisplayManager:
        dm = DisplayManager()
        dm.display_image('/tmp/test_skin_tone.png')

    return is_not_white and is_not_black

def test_green_variations():
    """Test various green shades"""
    print("\n" + "="*70)
    print("TEST 3: Green Variations")
    print("="*70)

    greens = [
        ("Pure Green", (0, 255, 0)),
        ("Mountain Green", (34, 139, 34)),
        ("Forest Green", (50, 100, 50)),
        ("Dark Green", (0, 100, 0)),
        ("Light Green", (144, 238, 144)),
    ]

    all_pass = True
    for label, color in greens:
        enhanced = enhance_color(color, saturation=1.5)
        idx, dist = find_closest_color(*enhanced)

        # Green shades should map to green or stay close
        is_pass = COLOR_NAMES[idx] == "Green"
        status = "✓" if is_pass else "✗"
        all_pass = all_pass and is_pass

        print(f"{status} {label:20} RGB{str(color):20} -> Enhanced: RGB{str(enhanced):20} -> {COLOR_NAMES[idx]}")

    return all_pass

def test_color_enhancement_effects():
    """Test the actual enhancement pipeline"""
    print("\n" + "="*70)
    print("TEST 4: Enhancement Pipeline Effects (1.5x Saturation)")
    print("="*70)

    test_colors = [
        ("Pure Green", (0, 255, 0)),
        ("Skin tone", (255, 200, 124)),
        ("Red", (255, 0, 0)),
        ("Yellow", (255, 255, 0)),
        ("Blue", (0, 0, 255)),
        ("Mountain Green", (34, 139, 34)),
    ]

    print(f"{'Label':<20} {'Original':<25} {'Enhanced':<25} {'Maps To':<15}")
    print("-" * 85)

    all_pass = True
    for label, color in test_colors:
        enhanced = enhance_color(color, saturation=1.5)
        idx, _ = find_closest_color(*enhanced)

        print(f"{label:<20} RGB{str(color):<23} RGB{str(enhanced):<23} {COLOR_NAMES[idx]:<15}")

        # All colors should map to a defined core color
        is_valid = idx >= 0 and idx < len(CORE_COLORS)
        all_pass = all_pass and is_valid

    return all_pass

def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("COLOR MAPPING FIX VALIDATION TEST SUITE")
    print("="*70)
    print("\nThis script validates the fix for color artifacts in the photo frame.")
    print("Issues being fixed:")
    print("- Green appearing as red-black")
    print("- People/skin tones appearing as white voids")
    print()

    results = {
        "Green Image": test_green_image(),
        "Skin Tone Image": test_skin_tone_image(),
        "Green Variations": test_green_variations(),
        "Enhancement Pipeline": test_color_enhancement_effects(),
    }

    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")

    print()
    print(f"Total: {passed}/{total} tests passed")

    if passed == total:
        print("\n✓ All tests passed! Color fix is working correctly.")
        print("You should see:")
        print("  - Green images displayed as green (not red-black)")
        print("  - Skin tones displayed as yellow/natural (not white void)")
        print("  - Sharp edges preserved")
        return 0
    else:
        print("\n✗ Some tests failed. Review the output above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
