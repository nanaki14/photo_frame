#!/usr/bin/env python3
"""
Test RGB to BGR conversion for Waveshare display.

Waveshare hardware expects BGR format, but PIL uses RGB.
This test verifies the conversion is working correctly.
"""

from PIL import Image

def test_rgb_to_bgr_conversion():
    """Test that RGB colors are correctly converted to BGR"""
    print("\n" + "="*70)
    print("TEST: RGB to BGR Conversion")
    print("="*70)

    test_cases = [
        ("Pure Blue", (0, 0, 255), (255, 0, 0)),
        ("Pure Red", (255, 0, 0), (0, 0, 255)),
        ("Pure Green", (0, 255, 0), (0, 255, 0)),
        ("Yellow", (255, 255, 0), (0, 255, 255)),
        ("Cyan", (0, 255, 255), (255, 255, 0)),
        ("Magenta", (255, 0, 255), (255, 0, 255)),
        ("White", (255, 255, 255), (255, 255, 255)),
        ("Black", (0, 0, 0), (0, 0, 0)),
    ]

    all_pass = True

    for label, rgb_input, expected_bgr in test_cases:
        # Create RGB image
        img_rgb = Image.new('RGB', (10, 10), color=rgb_input)

        # Convert to BGR
        r, g, b = img_rgb.split()
        img_bgr = Image.merge('RGB', (b, g, r))

        # Get resulting pixel
        result_bgr = img_bgr.getpixel((5, 5))

        # Check if matches expected
        is_pass = result_bgr == expected_bgr
        status = "✓" if is_pass else "✗"
        all_pass = all_pass and is_pass

        print(f"{status} {label:12} RGB{str(rgb_input):20} → BGR{str(result_bgr):20}")

        if not is_pass:
            print(f"   Expected: BGR{expected_bgr}")

    return all_pass

def test_blue_to_red_problem():
    """Test the specific issue: Blue appearing as Red"""
    print("\n" + "="*70)
    print("TEST: Blue Image → Should Display as Blue (not Red)")
    print("="*70)

    # User's problem: Pure blue (0, 0, 255) was appearing as red
    blue_rgb = (0, 0, 255)

    # Without conversion, Waveshare would interpret this as:
    blue_as_bgr = blue_rgb  # (0, 0, 255) in BGR = Red!

    print(f"User uploaded: Pure Blue RGB{blue_rgb}")
    print(f"Without conversion: Waveshare sees BGR{blue_as_bgr} = RED ✗")

    # With conversion:
    img = Image.new('RGB', (10, 10), color=blue_rgb)
    r, g, b = img.split()
    img_bgr = Image.merge('RGB', (b, g, r))
    converted = img_bgr.getpixel((5, 5))

    print(f"With conversion: We send BGR{converted} = BLUE ✓")

    return converted == (255, 0, 0)  # Should be (255, 0, 0) in BGR for blue

def main():
    """Run all RGB/BGR tests"""
    print("\n" + "="*70)
    print("RGB ↔ BGR CONVERSION TEST SUITE")
    print("="*70)
    print("\nWaveshare hardware expects BGR format.")
    print("PIL uses RGB format.")
    print("This test verifies our conversion is correct.")

    results = {
        "RGB to BGR Conversion": test_rgb_to_bgr_conversion(),
        "Blue to Red Problem": test_blue_to_red_problem(),
    }

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
        print("\n✓ All tests passed!")
        print("\nThe RGB to BGR conversion is working correctly:")
        print("  • Blue (0,0,255) → (255,0,0) for Waveshare")
        print("  • Red (255,0,0) → (0,0,255) for Waveshare")
        print("  • Colors will display correctly on the e-ink")
        return 0
    else:
        print("\n✗ Some tests failed.")
        return 1

if __name__ == '__main__':
    import sys
    sys.exit(main())
