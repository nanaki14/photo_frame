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
      Uses epd7in3e.py module with Floyd-Steinberg dithering
    - Colors: Black, White, Red, Yellow, Green, Blue
    - Display time: 30-40 seconds for full color on Raspberry Pi Zero
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
        if display_model == 'epd7in3e':
            from waveshare_epd import epd7in3e
            epd_module = epd7in3e
            logger.info("Using epd7in3e (HAT (E) - Spectra 6)")
        elif display_model == 'epd7in3f':
            from waveshare_epd import epd7in3f
            epd_module = epd7in3f
            logger.info("Using epd7in3f (7-color Spectra)")
        elif display_model == 'epd7in3b':
            from waveshare_epd import epd7in3b
            epd_module = epd7in3b
            logger.info("Using epd7in3b (Red/Black/White)")
        elif display_model == 'epd7in3c':
            from waveshare_epd import epd7in3c
            epd_module = epd7in3c
            logger.info("Using epd7in3c (Red/Black/White variant)")
        else:
            # Default to epd7in3e (HAT (E) - Spectra 6)
            from waveshare_epd import epd7in3e
            epd_module = epd7in3e
            logger.info(f"Unknown model {display_model}, defaulting to epd7in3e")

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

            # Apply E Ink Spectra 6 (6-color) optimizations with aggressive color enhancement
            # Strategy: Simple, direct color enhancement without LAB conversion
            logger.info("Optimizing image for E Ink Spectra 6 with aggressive color enhancement")

            # Save before enhancement for diagnostics
            background.save("/tmp/01_before_enhancement.png")
            logger.info("Saved diagnostic: /tmp/01_before_enhancement.png")

            # Step 1: Apply simple but aggressive color enhancement
            # Avoid complex LAB conversion that may lose color information
            logger.info("Step 1: Applying direct color enhancement")

            from PIL import ImageEnhance

            # Enhance saturation moderately to compensate for 6-color limitation
            # Note: Excessive saturation destroys skin tones and natural colors
            # 2.5x was causing skin tones to become red-black artifacts
            enhancer = ImageEnhance.Color(background)
            background = enhancer.enhance(1.5)  # 150% saturation (moderate boost)
            logger.info("Color saturation enhanced by 150%")
            background.save("/tmp/02_after_saturation.png")

            # Enhance contrast moderately to preserve dark colors
            # Note: 1.8x was crushing dark blues to black/very dark
            # Reduced to 1.3x to maintain color information
            enhancer = ImageEnhance.Contrast(background)
            background = enhancer.enhance(1.3)  # 30% contrast boost
            logger.info("Contrast enhanced by 30%")
            background.save("/tmp/03_after_contrast.png")

            # Enhance brightness slightly for visibility
            enhancer = ImageEnhance.Brightness(background)
            background = enhancer.enhance(1.1)  # 10% brightness boost
            logger.info("Brightness enhanced by 10%")
            background.save("/tmp/04_after_brightness.png")

            # Step 2: Direct 6-color mapping without palette quantize
            # CRITICAL: PIL quantize() was destroying color information
            # Use direct color mapping to the 6 core colors instead
            logger.info("Step 2: Applying direct 6-color mapping")

            # E Ink Spectra 6 core colors - per Waveshare HAT (E) specifications
            # Reference: Official Waveshare quantization example
            core_colors = [
                (0, 0, 0),          # Black
                (255, 255, 255),    # White
                (255, 0, 0),        # Red
                (255, 255, 0),      # Yellow
                (0, 128, 0),        # Green - Official Waveshare value
                (0, 0, 255),        # Blue
            ]

            logger.info(f"Core colors: {core_colors}")

            # Convert image to array for pixel-by-pixel processing
            img_array = background.load()
            width, height = background.size

            # Create output image
            output = Image.new('RGB', (width, height))
            out_array = output.load()

            # Function to find closest color using Euclidean distance
            def find_closest_color(r, g, b):
                """Find closest core color to given RGB value"""
                min_distance = float('inf')
                closest = core_colors[0]

                for color in core_colors:
                    # Euclidean distance in RGB space
                    distance = (r - color[0])**2 + (g - color[1])**2 + (b - color[2])**2
                    if distance < min_distance:
                        min_distance = distance
                        closest = color

                return closest

            # Map each pixel to closest core color
            logger.info("Mapping pixels to 6 core colors...")
            processed_count = 0
            for y in range(height):
                for x in range(width):
                    pixel = img_array[x, y]

                    # Handle both RGB tuples and single values
                    if isinstance(pixel, tuple):
                        r, g, b = pixel[:3]
                    else:
                        r = g = b = pixel

                    # Find and assign closest color
                    closest = find_closest_color(r, g, b)
                    out_array[x, y] = closest
                    processed_count += 1

                    # Log progress every 10000 pixels
                    if processed_count % 100000 == 0:
                        logger.info(f"Processed {processed_count}/{width*height} pixels...")

            final_image = output
            logger.info(f"Direct 6-color mapping complete: {processed_count} pixels processed")

            # Save diagnostic images
            final_image.save("/tmp/05_after_dithering.png")
            logger.info("Saved diagnostic: /tmp/05_after_dithering.png")
            final_image.save("/tmp/06_final_6color_mapped.png")
            logger.info("Saved diagnostic: /tmp/06_final_6color_mapped.png")

            # CRITICAL: Log pixel colors to verify color information is preserved
            sample_pixels = [
                final_image.getpixel((10, 10)),
                final_image.getpixel((100, 100)),
                final_image.getpixel((400, 240)),
            ]
            logger.info(f"Final image pixel samples: {sample_pixels}")

            logger.info(f"Image optimized for E Ink Spectra 6: size={final_image.size}, mode={final_image.mode}")
            logger.info("Color enhancement complete: direct 6-color nearest-neighbor mapping")
            return final_image
            
        except Exception as e:
            logger.error(f"Error optimizing image: {e}")
            return None
    
    def display_image(self, image_path: str) -> bool:
        """
        Display an image on the E Ink Spectra 6 display.

        Process (following official Waveshare method):
        1. Initialize display
        2. Load and resize image to display size
        3. Optimize with Floyd-Steinberg dithering to 6 colors
        4. Convert to buffer using epd.getbuffer()
        5. Display buffer using epd.display()
        6. Put display to sleep

        Note: Full color display takes 30-40 seconds on Raspberry Pi Zero.
        """
        try:
            if not self.is_initialized:
                logger.info("Initializing E Ink Spectra 6 display...")
                if not self.initialize():
                    logger.error("Failed to initialize display")
                    return False

            logger.info(f"Processing image: {image_path}")

            # Optimize image for E Ink Spectra 6
            # This includes resize, center, and Floyd-Steinberg dithering
            optimized_image = self.optimize_image_for_eink(image_path)
            if not optimized_image:
                logger.error("Failed to optimize image for display")
                return False

            logger.info(f"Image ready for display: size={optimized_image.size}, mode={optimized_image.mode}")

            # CRITICAL: Log pixel values before getbuffer()
            sample_pixel = optimized_image.getpixel((10, 10))
            logger.info(f"BEFORE getbuffer() - Sample pixel at (10,10): {sample_pixel}")

            # CRITICAL: Pass the 6-color mapped image directly to getbuffer()
            # Don't re-quantize - the colors are already mapped to the 6 core colors
            logger.info("Using direct 6-color mapped image for display")
            display_image = optimized_image

            logger.info("Displaying image (this may take 30-40 seconds on Raspberry Pi Zero)...")

            # The image is already 6-color mapped in optimize_image_for_eink()
            # Just use official getbuffer() to convert to hardware buffer format
            logger.info("Using official getbuffer() on pre-mapped image...")

            # Record start time for performance monitoring
            start_time = time.time()

            # Use official getbuffer() method
            buffer = self.epd.getbuffer(display_image)
            logger.info(f"Buffer created by getbuffer(): {len(buffer)} bytes")

            self.epd.display(buffer)

            # Record display time
            end_time = time.time()
            display_time = end_time - start_time

            logger.info(f"Image displayed successfully in {display_time:.1f} seconds")
            logger.info(f"Successfully displayed image: {image_path}")

            # DIAGNOSTIC: Check what was actually sent to display
            logger.info(f"Buffer sent to display: {len(buffer)} bytes")
            logger.info(f"First 100 bytes of buffer: {buffer[:100]}")

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