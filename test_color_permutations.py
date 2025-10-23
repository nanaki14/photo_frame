#!/usr/bin/env python3
"""
Test all color channel permutations to identify correct mapping for Waveshare.

Current status:
- Red (255, 0, 0) displays correctly ✓
- Blue (0, 0, 255) appears yellowish ✗

This suggests the channel mapping might not be simple BGR.
Let's test all 6 possible permutations: RGB, RBG, GRB, GBR, BRG, BGR
"""

from PIL import Image, ImageDraw

def create_test_image_with_permutations():
    """Create a test image showing all 6 channel permutations"""

    # Test colors
    test_colors = [
        ("Red", (255, 0, 0)),
        ("Green", (0, 255, 0)),
        ("Blue", (0, 0, 255)),
        ("Yellow", (255, 255, 0)),
        ("Cyan", (0, 255, 255)),
        ("Magenta", (255, 0, 255)),
        ("White", (255, 255, 255)),
        ("Black", (0, 0, 0)),
    ]

    # All possible channel permutations
    permutations = [
        ("RGB (Original)", lambda r, g, b: (r, g, b)),
        ("RBG", lambda r, g, b: (r, b, g)),
        ("GRB", lambda r, g, b: (g, r, b)),
        ("GBR", lambda r, g, b: (g, b, r)),
        ("BRG", lambda r, g, b: (b, r, g)),
        ("BGR (Current)", lambda r, g, b: (b, g, r)),
    ]

    print("\n" + "="*80)
    print("COLOR CHANNEL PERMUTATION TEST")
    print("="*80)
    print("\nTesting all 6 possible channel orders to find the correct mapping.")
    print("Current implementation uses BGR, but blue appears yellowish.\n")

    # Create test images for each permutation
    for perm_name, perm_func in permutations:
        img = Image.new('RGB', (800, 480), color='white')
        draw = ImageDraw.Draw(img)

        # Draw color swatches in a grid
        swatch_width = 180
        swatch_height = 100

        for idx, (color_name, (r, g, b)) in enumerate(test_colors):
            x = (idx % 4) * 200 + 10
            y = (idx // 4) * 120 + 10

            # Apply the permutation
            new_r, new_g, new_b = perm_func(r, g, b)
            new_color = (new_r, new_g, new_b)

            # Draw swatch
            draw.rectangle([x, y, x + swatch_width, y + swatch_height], fill=new_color)

            # Text color (contrasting)
            text_color = (255, 255, 255) if sum(new_color) < 384 else (0, 0, 0)
            draw.text((x + 5, y + 5), color_name, fill=text_color)
            draw.text((x + 5, y + 25), f"RGB{(r,g,b)}", fill=text_color, font=None)
            draw.text((x + 5, y + 40), f"→{new_color}", fill=text_color, font=None)

        # Save the test image
        filename = f"/tmp/test_permutation_{perm_name.replace(' ', '_').replace('(', '').replace(')', '')}.jpg"
        img.save(filename, quality=100)

        print(f"✓ Created: {filename}")
        print(f"  Permutation: {perm_name}")

    print("\n" + "="*80)
    print("DIAGNOSTIC INSTRUCTIONS")
    print("="*80)
    print("\nUpload each test image to the photo frame and note the results:\n")

    for perm_name, _ in permutations:
        clean_name = perm_name.replace(' ', '_').replace('(', '').replace(')', '')
        print(f"{perm_name:20} → /tmp/test_permutation_{clean_name}.jpg")

    print("\n" + "="*80)
    print("WHAT TO LOOK FOR")
    print("="*80)
    print("""
The CORRECT permutation is the one where:
1. Red swatch displays as RED on the e-ink
2. Green swatch displays as GREEN on the e-ink
3. Blue swatch displays as BLUE on the e-ink
4. Yellow swatch displays as YELLOW on the e-ink
5. All other colors are as close as possible to expected

Current status:
- BGR: Red ✓, Blue appears yellowish ✗

Expected findings:
- If blue appears yellowish, it might be getting swapped with yellow
- Yellow is (255, 255, 0) in RGB
- This suggests B and R channels might both be involved in the issue
""")

def analyze_current_results():
    """Analyze the current BGR results to predict the correct permutation"""

    print("\n" + "="*80)
    print("ANALYZING CURRENT RESULTS")
    print("="*80)

    print("\nCurrent permutation: BGR")
    print("\nObserved results:")
    print("  Red (255,0,0) → BGR (0,0,255) → displays as RED ✓")
    print("  Blue (0,0,255) → BGR (255,0,0) → displays as YELLOWISH ✗")

    print("\nAnalysis:")
    print("  If Blue → BGR(255,0,0) appears yellowish, not red,")
    print("  this suggests the hardware might be interpreting colors differently.")

    print("\nPossible explanations:")
    print("  1. The channel order is not BGR")
    print("  2. Waveshare getbuffer() does additional color remapping")
    print("  3. The 6-color palette quantization is causing unexpected mapping")

    print("\nThe 6-color Spectra palette:")
    spectra_colors = {
        "Black": (0, 0, 0),
        "White": (255, 255, 255),
        "Red": (255, 0, 0),
        "Yellow": (255, 255, 0),
        "Green": (0, 128, 0),  # Note: NOT (0, 255, 0)
        "Blue": (0, 0, 255),
    }

    for name, rgb in spectra_colors.items():
        print(f"  {name:10} RGB{rgb}")

    print("\nKey insight:")
    print("  If BGR(255,0,0) appears yellowish instead of red,")
    print("  the hardware might be seeing it closer to Yellow (255,255,0)")
    print("  than to Red (255,0,0).")
    print("\n  This could mean:")
    print("    - Additional color remapping inside getbuffer()")
    print("    - Different color order than BGR")
    print("    - Floyd-Steinberg dithering creating yellow appearance")

def create_simple_color_test():
    """Create simple solid color test images for direct testing"""

    print("\n" + "="*80)
    print("CREATING SIMPLE COLOR TESTS")
    print("="*80)

    # Test the 6 Spectra colors directly
    spectra_colors = [
        ("red", (255, 0, 0)),
        ("yellow", (255, 255, 0)),
        ("green", (0, 128, 0)),
        ("blue", (0, 0, 255)),
        ("black", (0, 0, 0)),
        ("white", (255, 255, 255)),
    ]

    print("\nCreating solid color test images (NO conversion)...")
    print("These use RGB directly to test hardware interpretation:\n")

    for name, color in spectra_colors:
        img = Image.new('RGB', (800, 480), color=color)
        draw = ImageDraw.Draw(img)

        # Add label
        text_color = (255, 255, 255) if sum(color) < 384 else (0, 0, 0)
        draw.text((50, 50), f"{name.upper()}\nRGB{color}", fill=text_color)

        filename = f"/tmp/test_simple_{name}.jpg"
        img.save(filename, quality=100)

        print(f"✓ {name:10} RGB{str(color):20} → {filename}")

    print("\n" + "="*80)
    print("TEST THESE IMAGES")
    print("="*80)
    print("""
Upload these simple images (in order) and note what color appears:

1. test_simple_red.jpg → Should appear RED
2. test_simple_blue.jpg → Should appear BLUE (currently appears yellowish?)
3. test_simple_green.jpg → Should appear GREEN
4. test_simple_yellow.jpg → Should appear YELLOW

Report the actual display colors to identify the exact mapping issue.
""")

def main():
    """Run all diagnostic tests"""

    print("\n" + "="*80)
    print("WAVESHARE COLOR MAPPING DIAGNOSTIC")
    print("="*80)
    print("\nGoal: Identify the correct color channel order for Waveshare display.")

    # Analyze current results
    analyze_current_results()

    # Create simple tests
    create_simple_color_test()

    # Create permutation tests
    create_test_image_with_permutations()

    print("\n" + "="*80)
    print("NEXT STEPS")
    print("="*80)
    print("""
1. Start with the simple color tests:
   - Upload test_simple_red.jpg → What color appears?
   - Upload test_simple_blue.jpg → What color appears?
   - Upload test_simple_green.jpg → What color appears?
   - Upload test_simple_yellow.jpg → What color appears?

2. If the simple tests don't reveal the pattern, try the permutation tests:
   - Test each permutation image
   - Identify which permutation shows all colors correctly

3. Report the results back so we can update the code with the correct mapping.
""")

if __name__ == '__main__':
    main()
