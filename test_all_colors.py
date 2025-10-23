#!/usr/bin/env python3
"""
Test script to create images for all basic colors.
Upload these to the photo frame to see which colors display correctly.
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_color_test_images():
    """Create test images for each color"""

    colors = {
        "red": (255, 0, 0),
        "green": (0, 255, 0),
        "blue": (0, 0, 255),
        "yellow": (255, 255, 0),
        "cyan": (0, 255, 255),
        "magenta": (255, 0, 255),
        "white": (255, 255, 255),
        "black": (0, 0, 0),
    }

    output_dir = "/tmp/color_tests"
    os.makedirs(output_dir, exist_ok=True)

    print("=" * 80)
    print("Creating color test images")
    print("=" * 80)
    print()

    for name, rgb in colors.items():
        # Create solid color image
        img = Image.new('RGB', (800, 480), color=rgb)

        # Add text label
        draw = ImageDraw.Draw(img)

        # Use contrasting text color
        text_color = (255, 255, 255) if sum(rgb) < 384 else (0, 0, 0)

        # Draw text
        text = f"{name.upper()}\nRGB{rgb}"
        draw.text((50, 50), text, fill=text_color)

        # Save
        filepath = os.path.join(output_dir, f"test_{name}.jpg")
        img.save(filepath, quality=100)

        print(f"✓ Created: {filepath}")
        print(f"  Color: {name.upper()} RGB{rgb}")

    print()
    print("=" * 80)
    print("Next steps:")
    print("=" * 80)
    print()
    print("1. Upload each image to the photo frame")
    print("2. Note which colors display correctly:")
    print()
    print("   Color    | Expected | Actual Display")
    print("   ---------|----------|---------------")
    print("   Red      | Red      | ?")
    print("   Green    | Green    | ?")
    print("   Blue     | Blue     | ?")
    print("   Yellow   | Yellow   | ?")
    print("   Cyan     | Cyan     | ?")
    print("   Magenta  | Magenta  | ?")
    print()
    print("3. Report which colors are wrong")
    print()
    print("This will help identify the exact color mapping issue.")

def create_combined_test():
    """Create a single image with all colors"""

    img = Image.new('RGB', (800, 480), color='white')
    draw = ImageDraw.Draw(img)

    colors = [
        ("Red", (255, 0, 0)),
        ("Green", (0, 255, 0)),
        ("Blue", (0, 0, 255)),
        ("Yellow", (255, 255, 0)),
        ("Cyan", (0, 255, 255)),
        ("Magenta", (255, 0, 255)),
        ("Black", (0, 0, 0)),
        ("White", (255, 255, 255)),
    ]

    # Draw color swatches
    swatch_width = 190
    swatch_height = 110

    for idx, (name, color) in enumerate(colors):
        x = (idx % 4) * 200 + 5
        y = (idx // 4) * 120 + 5

        draw.rectangle([x, y, x + swatch_width, y + swatch_height], fill=color)

        # Text color
        text_color = (255, 255, 255) if sum(color) < 384 else (0, 0, 0)
        draw.text((x + 10, y + 10), name, fill=text_color)
        draw.text((x + 10, y + 30), f"RGB{color}", fill=text_color)

    filepath = "/tmp/color_tests/test_all_colors.jpg"
    img.save(filepath, quality=100)

    print()
    print(f"✓ Created combined test: {filepath}")
    print("  This image shows all colors in one view")

if __name__ == '__main__':
    create_color_test_images()
    create_combined_test()

    print()
    print("=" * 80)
    print("Files created in /tmp/color_tests/")
    print("=" * 80)
