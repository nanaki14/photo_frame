#!/usr/bin/env python3
"""
Display Test Script
Tests the e-ink display functionality for the photo frame.
"""

import sys
import os
import time
import logging
from pathlib import Path

# Add the display module to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from display_manager import DisplayManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_display_initialization():
    """Test display initialization"""
    print("Testing display initialization...")
    display = DisplayManager()
    
    if display.initialize():
        print("✓ Display initialized successfully")
        return display
    else:
        print("✗ Display initialization failed")
        return None

def test_display_message(display):
    """Test displaying a text message"""
    print("Testing message display...")
    
    if display.display_message("Photo Frame Test", 32):
        print("✓ Message displayed successfully")
        time.sleep(2)
        return True
    else:
        print("✗ Message display failed")
        return False

def test_display_clear(display):
    """Test clearing the display"""
    print("Testing display clear...")
    
    if display.clear_display():
        print("✓ Display cleared successfully")
        time.sleep(1)
        return True
    else:
        print("✗ Display clear failed")
        return False

def test_display_status(display):
    """Test getting display status"""
    print("Testing display status...")
    
    try:
        status = display.get_status()
        print(f"✓ Display status: {status}")
        return True
    except Exception as e:
        print(f"✗ Display status failed: {e}")
        return False

def create_test_image():
    """Create a simple test image"""
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Create a test image
        img = Image.new('RGB', (400, 300), 'white')
        draw = ImageDraw.Draw(img)
        
        # Draw some test content
        draw.rectangle([50, 50, 350, 250], outline='black', width=3)
        draw.text((100, 130), "Test Image", fill='black')
        draw.text((100, 160), "Photo Frame", fill='black')
        
        # Save test image
        test_image_path = '/tmp/test_image.png'
        img.save(test_image_path)
        print(f"✓ Test image created: {test_image_path}")
        return test_image_path
    
    except Exception as e:
        print(f"✗ Test image creation failed: {e}")
        return None

def test_image_display(display, image_path):
    """Test displaying an image"""
    print(f"Testing image display: {image_path}")
    
    if display.display_image(image_path):
        print("✓ Image displayed successfully")
        return True
    else:
        print("✗ Image display failed")
        return False

def test_sleep_mode(display):
    """Test sleep mode"""
    print("Testing sleep mode...")
    
    if display.sleep():
        print("✓ Sleep mode activated successfully")
        return True
    else:
        print("✗ Sleep mode failed")
        return False

def run_full_test():
    """Run all display tests"""
    print("=" * 50)
    print("E-ink Display Test Suite")
    print("=" * 50)
    
    # Initialize display
    display = test_display_initialization()
    if not display:
        print("Cannot continue tests without display initialization")
        return False
    
    tests_passed = 0
    total_tests = 6
    
    # Test status
    if test_display_status(display):
        tests_passed += 1
    
    # Test message display
    if test_display_message(display):
        tests_passed += 1
    
    # Test clear
    if test_display_clear(display):
        tests_passed += 1
    
    # Test image creation and display
    test_image_path = create_test_image()
    if test_image_path:
        if test_image_display(display, test_image_path):
            tests_passed += 1
        
        # Clean up test image
        try:
            os.remove(test_image_path)
        except:
            pass
    
    # Test another message
    if display.display_message("Test Complete!", 24):
        print("✓ Final message displayed")
        tests_passed += 1
    
    # Test sleep mode
    time.sleep(1)
    if test_sleep_mode(display):
        tests_passed += 1
    
    # Summary
    print("=" * 50)
    print(f"Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("✓ All tests passed! Display is working correctly.")
        return True
    else:
        print(f"✗ {total_tests - tests_passed} tests failed.")
        return False

def main():
    """Main test function"""
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        # Quick test - just initialization and status
        print("Running quick display test...")
        display = test_display_initialization()
        if display and test_display_status(display):
            print("✓ Quick test passed")
            sys.exit(0)
        else:
            print("✗ Quick test failed")
            sys.exit(1)
    else:
        # Full test suite
        success = run_full_test()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()