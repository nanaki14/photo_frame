#!/usr/bin/env python3
"""
Waveshare 7.3inch e-Paper Display Manager
For Raspberry Pi Zero 2 WH with Waveshare 7.3inch e-Paper HAT

This module provides display management for the photo frame application.
It handles image display, optimization for e-ink characteristics, and display lifecycle.
"""

import sys
import os
import time
import logging
from PIL import Image, ImageDraw, ImageFont
from typing import Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/display_manager.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Waveshare 7.3inch e-Paper display specifications
DISPLAY_WIDTH = 800
DISPLAY_HEIGHT = 480

# Performance optimizations for Pi Zero 2 WH
import platform
import psutil

def get_system_info():
    """Get system information for performance optimization"""
    is_pi = 'arm' in platform.machine().lower() or 'aarch' in platform.machine().lower()
    memory_mb = psutil.virtual_memory().total // (1024 * 1024)
    cpu_count = psutil.cpu_count()
    
    return {
        'is_pi': is_pi,
        'memory_mb': memory_mb,
        'cpu_count': cpu_count,
        'is_low_memory': memory_mb < 1024  # Less than 1GB RAM
    }

SYSTEM_INFO = get_system_info()

class MockEPD:
    """Mock e-Paper display class for development/testing"""
    def __init__(self):
        self.width = DISPLAY_WIDTH
        self.height = DISPLAY_HEIGHT
        logger.info("Mock e-Paper display initialized")
    
    def init(self):
        logger.info("Mock display initialized")
        return 0
    
    def display(self, image):
        logger.info("Mock display updated with new image")
        # Save to file for testing
        if image:
            image.save("/tmp/current_display.png")
            logger.info("Display image saved to /tmp/current_display.png")
    
    def sleep(self):
        logger.info("Mock display entered sleep mode")
    
    def Clear(self):
        logger.info("Mock display cleared")

def get_epd_instance():
    """Get e-Paper display instance, with fallback to mock for development

    Supports:
    - Waveshare 7.3inch e-Paper HAT (E) - E Ink Spectra 6 (6-color)
    - epd7in3f.py module (6-color: black, white, red, yellow, green, blue)
    """
    # Check for mock mode override
    use_mock_mode = os.environ.get('MOCK_DISPLAY', '').lower() in ('true', '1', 'yes')

    if use_mock_mode:
        logger.info("Mock display mode enabled via MOCK_DISPLAY environment variable")
        return MockEPD()

    try:
        # Check for environment variable override for library path
        env_path = os.environ.get('WAVESHARE_LIB_PATH')

        # Check for environment variable to select display model
        display_model = os.environ.get('WAVESHARE_MODEL', 'epd7in3f').lower()
        logger.info(f"Target display model: {display_model}")

        # Try multiple possible paths for Waveshare library
        possible_paths = []

        if env_path:
            possible_paths.append(env_path)
            logger.info(f"Using WAVESHARE_LIB_PATH from environment: {env_path}")

        possible_paths.extend([
            # Home directory based (dynamic)
            os.path.expanduser('~/e-Paper/RaspberryPi_JetsonNano/python/lib'),
            # Absolute paths
            '/home/pi/e-Paper/RaspberryPi_JetsonNano/python/lib',
            '/root/e-Paper/RaspberryPi_JetsonNano/python/lib',
            # System-wide installation
            '/usr/local/lib/python3/dist-packages',
        ])

        # Try to add valid paths to sys.path
        for path in possible_paths:
            expanded_path = os.path.expanduser(path)
            if os.path.isdir(expanded_path) and expanded_path not in sys.path:
                sys.path.insert(0, expanded_path)
                logger.info(f"Added to sys.path: {expanded_path}")

        # Try to import the Waveshare library module
        logger.info(f"Attempting to import waveshare_epd.{display_model}")
        if display_model == 'epd7in3f':
            from waveshare_epd import epd7in3f
            epd_module = epd7in3f
        elif display_model == 'epd7in3b':
            from waveshare_epd import epd7in3b
            epd_module = epd7in3b
        elif display_model == 'epd7in3c':
            from waveshare_epd import epd7in3c
            epd_module = epd7in3c
        else:
            # Default to epd7in3f (7-color Spectra 6)
            from waveshare_epd import epd7in3f
            epd_module = epd7in3f
            logger.info(f"Unknown model {display_model}, defaulting to epd7in3f")

        logger.info("Waveshare library imported successfully")

        # Try to initialize the hardware
        try:
            epd = epd_module.EPD()
            logger.info(f"Waveshare 7.3inch e-Paper display ({display_model}) hardware initialized")
            return epd
        except OSError as e:
            # Hardware not available (GPIO/SPI not accessible)
            logger.warning(f"Hardware not available: {e}")
            logger.warning("Using mock display (hardware not connected or SPI/GPIO not enabled)")
            return MockEPD()

    except ImportError as e:
        logger.warning(f"Waveshare library not found (ImportError: {e}), using mock display")
        logger.info(f"Searched paths: {[os.path.expanduser(p) for p in possible_paths]}")
        return MockEPD()
    except Exception as e:
        logger.error(f"Error loading Waveshare library: {e}")
        logger.warning("Falling back to mock display")
        return MockEPD()

class DisplayManager:
    """Main display manager for the e-ink photo frame"""
    
    def __init__(self):
        self.epd = get_epd_instance()
        self.display_width = DISPLAY_WIDTH
        self.display_height = DISPLAY_HEIGHT
        self.is_initialized = False
        
    def initialize(self) -> bool:
        """Initialize the e-Paper display"""
        try:
            logger.info("Initializing e-Paper display...")
            result = self.epd.init()
            if result == 0:
                self.is_initialized = True
                logger.info("e-Paper display initialized successfully")
                return True
            else:
                logger.error(f"Failed to initialize display, error code: {result}")
                return False
        except Exception as e:
            logger.error(f"Error initializing display: {e}")
            return False
    
    def optimize_image_for_eink(self, image_path: str) -> Optional[Image.Image]:
        """
        Optimize image for E Ink Spectra 6 (6-color) e-Paper display.

        E Ink Spectra 6 supports 6 colors:
        - Black: RGB(0, 0, 0)
        - White: RGB(255, 255, 255)
        - Red: RGB(255, 0, 0)
        - Yellow: RGB(255, 255, 0)
        - Green: RGB(0, 128, 0)
        - Blue: RGB(0, 0, 255)
        """
        try:
            # Load image with memory optimization for Pi Zero
            if SYSTEM_INFO['is_low_memory']:
                # Use lazy loading for low memory systems
                img = Image.open(image_path)
                img.draft('RGB', (self.display_width, self.display_height))
            else:
                img = Image.open(image_path)

            logger.info(f"Loaded image: {img.size}")

            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Calculate scaling to fit display while maintaining aspect ratio
            img_width, img_height = img.size
            scale_w = self.display_width / img_width
            scale_h = self.display_height / img_height
            scale = min(scale_w, scale_h)
            
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)
            
            # Use different resampling algorithms based on system capability
            if SYSTEM_INFO['is_pi'] and SYSTEM_INFO['is_low_memory']:
                # Use faster, less memory-intensive algorithm on Pi Zero
                resample_method = Image.Resampling.NEAREST
            else:
                resample_method = Image.Resampling.LANCZOS
            
            # Resize image
            img = img.resize((new_width, new_height), resample_method)
            
            # Create a white background with display dimensions
            # Keep RGB for Waveshare 7.3inch color display support
            background = Image.new('RGB', (self.display_width, self.display_height), 'white')

            # Center the image on the background
            x_offset = (self.display_width - new_width) // 2
            y_offset = (self.display_height - new_height) // 2
            background.paste(img, (x_offset, y_offset))

            # Apply E Ink Spectra 6 (6-color) optimizations
            # The display supports: Black, White, Red, Yellow, Green, Blue
            # These colors are defined in the waveshare_epd module as constants
            logger.info("Applying E Ink Spectra 6 (6-color) optimizations")

            # Official E Ink Spectra 6 color palette
            # The Waveshare library internally uses these colors
            SPECTRA_PALETTE = [
                (0, 0, 0),        # Black
                (255, 255, 255),  # White
                (255, 0, 0),      # Red
                (255, 255, 0),    # Yellow
                (0, 128, 0),      # Green
                (0, 0, 255),      # Blue
            ]

            def quantize_to_nearest_color(r, g, b):
                """
                Quantize RGB color to the nearest E Ink Spectra 6 color.
                Uses Euclidean distance in RGB color space.
                """
                min_distance = float('inf')
                closest_color = SPECTRA_PALETTE[0]

                for color in SPECTRA_PALETTE:
                    # Euclidean distance: sqrt((r-cr)^2 + (g-cg)^2 + (b-cb)^2)
                    # We use squared distance to avoid sqrt for performance
                    distance = (r - color[0])**2 + (g - color[1])**2 + (b - color[2])**2
                    if distance < min_distance:
                        min_distance = distance
                        closest_color = color

                return closest_color

            # Process image pixels and quantize to palette
            # This converts the full RGB image to the limited 6-color palette
            pixels = background.load()
            for y in range(background.height):
                for x in range(background.width):
                    r, g, b = pixels[x, y]
                    # Quantize to nearest color in Spectra 6 palette
                    quantized = quantize_to_nearest_color(r, g, b)
                    pixels[x, y] = quantized

            logger.info(f"Image optimized for E Ink Spectra 6 display (6-color quantized): {background.size}")
            return background
            
        except Exception as e:
            logger.error(f"Error optimizing image: {e}")
            return None
    
    def display_image(self, image_path: str) -> bool:
        """
        Display an image on the e-ink screen.

        Process:
        1. Optimize image for E Ink Spectra 6 (resize, center, quantize to 6 colors)
        2. Convert to buffer format using epd.getbuffer()
        3. Display buffer on screen using epd.display()
        """
        try:
            if not self.is_initialized:
                if not self.initialize():
                    logger.error("Failed to initialize display")
                    return False

            logger.info(f"Processing image: {image_path}")

            # Optimize image for E Ink Spectra 6
            optimized_image = self.optimize_image_for_eink(image_path)
            if not optimized_image:
                logger.error("Failed to optimize image for display")
                return False

            logger.info(f"Image optimized, size: {optimized_image.size}, mode: {optimized_image.mode}")

            # Convert to display buffer format
            # The Waveshare getbuffer() method handles the color-to-buffer conversion
            if hasattr(self.epd, 'getbuffer'):
                logger.info("Using epd.getbuffer() for buffer conversion")
                buffer = self.epd.getbuffer(optimized_image)
                self.epd.display(buffer)
                logger.info("Image displayed successfully via getbuffer()")
            else:
                # Fallback for mock display
                logger.info("Direct display (mock mode or legacy library)")
                self.epd.display(optimized_image)

            logger.info(f"Successfully displayed image: {image_path}")
            return True

        except Exception as e:
            logger.error(f"Error displaying image: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    def clear_display(self) -> bool:
        """Clear the e-ink display"""
        try:
            if not self.is_initialized:
                if not self.initialize():
                    return False
            
            self.epd.Clear()
            logger.info("Display cleared")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing display: {e}")
            return False
    
    def display_message(self, message: str, font_size: int = 24) -> bool:
        """Display a text message on the screen"""
        try:
            if not self.is_initialized:
                if not self.initialize():
                    return False
            
            # Create image with white background
            img = Image.new('RGB', (self.display_width, self.display_height), 'white')
            draw = ImageDraw.Draw(img)
            
            # Try to load a font, fallback to default if not available
            try:
                font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', font_size)
            except:
                font = ImageFont.load_default()
            
            # Calculate text position (centered)
            bbox = draw.textbbox((0, 0), message, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            x = (self.display_width - text_width) // 2
            y = (self.display_height - text_height) // 2
            
            # Draw text
            draw.text((x, y), message, fill='black', font=font)
            
            # Convert to grayscale
            img = img.convert('L')
            
            # Display
            if hasattr(self.epd, 'getbuffer'):
                buffer = self.epd.getbuffer(img)
                self.epd.display(buffer)
            else:
                self.epd.display(img)
            
            logger.info(f"Displayed message: {message}")
            return True
            
        except Exception as e:
            logger.error(f"Error displaying message: {e}")
            return False
    
    def sleep(self) -> bool:
        """Put the display into sleep mode to save power"""
        try:
            if self.is_initialized:
                self.epd.sleep()
                logger.info("Display entered sleep mode")
            return True
        except Exception as e:
            logger.error(f"Error putting display to sleep: {e}")
            return False
    
    def get_status(self) -> dict:
        """Get display status information"""
        return {
            'initialized': self.is_initialized,
            'width': self.display_width,
            'height': self.display_height,
            'type': 'Waveshare 7.3inch e-Paper',
            'last_update': time.time()
        }

def main():
    """Command line interface for display operations"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python display_manager.py display <image_path>")
        print("  python display_manager.py clear")
        print("  python display_manager.py message <text>")
        print("  python display_manager.py test")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    display = DisplayManager()
    
    if command == "display" and len(sys.argv) >= 3:
        image_path = sys.argv[2]
        if not os.path.exists(image_path):
            print(f"Error: Image file not found: {image_path}")
            sys.exit(1)
        
        success = display.display_image(image_path)
        if success:
            print("Image displayed successfully")
        else:
            print("Failed to display image")
            sys.exit(1)
    
    elif command == "clear":
        success = display.clear_display()
        if success:
            print("Display cleared successfully")
        else:
            print("Failed to clear display")
            sys.exit(1)
    
    elif command == "message" and len(sys.argv) >= 3:
        message = " ".join(sys.argv[2:])
        success = display.display_message(message)
        if success:
            print("Message displayed successfully")
        else:
            print("Failed to display message")
            sys.exit(1)
    
    elif command == "test":
        print("Testing display...")
        if display.initialize():
            display.display_message("Photo Frame Ready", 32)
            print("Test completed successfully")
        else:
            print("Display test failed")
            sys.exit(1)
    
    else:
        print("Invalid command or missing arguments")
        sys.exit(1)

if __name__ == "__main__":
    main()