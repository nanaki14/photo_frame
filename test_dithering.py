#!/usr/bin/env python3
"""
Test Floyd-Steinberg dithering with 6-color palette
"""

import sys
import numpy as np
from PIL import Image

# 6-color palette for E Ink Spectra 6
PALETTE_6COLOR = np.array([
    [0, 0, 0],       # Black
    [255, 255, 255], # White
    [255, 0, 0],     # Red
    [255, 255, 0],   # Yellow
    [0, 128, 0],     # Green
    [0, 0, 255]      # Blue
], dtype=np.float32)


def find_closest_color(pixel):
    """Find the closest palette color to the given pixel"""
    distances = np.sum((PALETTE_6COLOR - pixel) ** 2, axis=1)
    closest_idx = np.argmin(distances)
    return closest_idx, PALETTE_6COLOR[closest_idx]


def apply_floyd_steinberg_dithering(image: Image.Image) -> Image.Image:
    """Apply Floyd-Steinberg error diffusion dithering"""
    print("Applying Floyd-Steinberg dithering...")

    pixels = np.array(image, dtype=np.float32)
    height, width = pixels.shape[:2]

    print(f"Image size: {width}x{height}")

    for y in range(height):
        for x in range(width):
            old_pixel = pixels[y, x].copy()

            # Find closest color
            _, new_pixel = find_closest_color(old_pixel)
            pixels[y, x] = new_pixel

            # Calculate error
            error = old_pixel - new_pixel

            # Distribute error to neighboring pixels
            #     X   7/16
            # 3/16 5/16 1/16

            if x + 1 < width:
                pixels[y, x + 1] += error * 7/16

            if y + 1 < height:
                if x > 0:
                    pixels[y + 1, x - 1] += error * 3/16
                pixels[y + 1, x] += error * 5/16
                if x + 1 < width:
                    pixels[y + 1, x + 1] += error * 1/16

        # Progress
        if (y + 1) % 50 == 0 or y == height - 1:
            progress = (y + 1) / height * 100
            print(f"Progress: {progress:.1f}%")

    # Clip and convert back to image
    pixels = np.clip(pixels, 0, 255).astype(np.uint8)
    result_img = Image.fromarray(pixels)

    print("Dithering completed!")
    return result_img


def create_test_images():
    """Create test images for dithering"""
    print("\n" + "="*80)
    print("Creating test images...")
    print("="*80)

    # Test 1: Simple color blocks
    print("\n1. Creating color blocks test image...")
    img = Image.new('RGB', (800, 480), 'white')
    from PIL import ImageDraw
    draw = ImageDraw.Draw(img)

    colors = [
        ("Red", (255, 0, 0), 0, 0),
        ("Yellow", (255, 255, 0), 200, 0),
        ("Green", (0, 128, 0), 400, 0),
        ("Blue", (0, 0, 255), 600, 0),
        ("Black", (0, 0, 0), 0, 120),
        ("White", (255, 255, 255), 200, 120),
    ]

    for name, color, x, y in colors:
        draw.rectangle([x, y, x + 180, y + 100], fill=color)
        text_color = (255, 255, 255) if sum(color) < 384 else (0, 0, 0)
        draw.text((x + 10, y + 10), name, fill=text_color)

    img.save("/tmp/test_colors_original.png")
    print("   Saved: /tmp/test_colors_original.png")

    dithered = apply_floyd_steinberg_dithering(img)
    dithered.save("/tmp/test_colors_dithered.png")
    print("   Saved: /tmp/test_colors_dithered.png")

    # Test 2: Gradient
    print("\n2. Creating gradient test image...")
    img = Image.new('RGB', (800, 480), 'white')
    pixels = img.load()

    for y in range(480):
        for x in range(800):
            # Red to yellow gradient
            if y < 160:
                r = 255
                g = int((x / 800) * 255)
                b = 0
            # Green to blue gradient
            elif y < 320:
                r = int((1 - x / 800) * 0)
                g = int((1 - x / 800) * 128 + (x / 800) * 0)
                b = int((x / 800) * 255)
            # Grayscale gradient
            else:
                gray = int((x / 800) * 255)
                r = g = b = gray

            pixels[x, y] = (r, g, b)

    img.save("/tmp/test_gradient_original.png")
    print("   Saved: /tmp/test_gradient_original.png")

    dithered = apply_floyd_steinberg_dithering(img)
    dithered.save("/tmp/test_gradient_dithered.png")
    print("   Saved: /tmp/test_gradient_dithered.png")

    print("\n" + "="*80)
    print("Test images created!")
    print("="*80)


def test_with_file(input_path, output_path):
    """Test dithering with a specific file"""
    try:
        print(f"\nLoading: {input_path}")
        img = Image.open(input_path).convert('RGB')

        # Resize to display size if needed
        if img.size != (800, 480):
            print(f"Resizing from {img.size} to (800, 480)")
            img = img.resize((800, 480), Image.Resampling.LANCZOS)

        dithered = apply_floyd_steinberg_dithering(img)
        dithered.save(output_path)
        print(f"Saved: {output_path}")

    except FileNotFoundError:
        print(f"Error: File '{input_path}' not found")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

    return True


def main():
    print("="*80)
    print("Floyd-Steinberg Dithering Test (6-color palette)")
    print("="*80)

    if len(sys.argv) == 1:
        # No arguments - create test images
        create_test_images()
        print("\nNext steps:")
        print("  1. View test images in /tmp/test_*")
        print("  2. Test with your own image:")
        print("     python3 test_dithering.py input.jpg output.png")

    elif len(sys.argv) == 3:
        # Test with specific file
        input_path = sys.argv[1]
        output_path = sys.argv[2]
        if test_with_file(input_path, output_path):
            print("\nSuccess!")
        else:
            sys.exit(1)

    else:
        print("Usage:")
        print("  python3 test_dithering.py                    # Create test images")
        print("  python3 test_dithering.py <input> <output>   # Dither specific image")
        sys.exit(1)


if __name__ == "__main__":
    main()
