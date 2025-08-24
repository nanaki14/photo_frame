#!/usr/bin/env python3
"""
Update Display Script
Called by the web server when a new photo is uploaded to immediately update the e-ink display.
"""

import sys
import os
import json
import time
import logging
from pathlib import Path

# Add the display module to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from display_manager import DisplayManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/update_display.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def update_display_status(status: str, photo_path: str = None, error: str = None):
    """Update the display status file"""
    status_file = Path(__file__).parent.parent / 'storage' / 'config' / 'display_status.json'
    
    try:
        # Ensure directory exists
        status_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing status or create new
        try:
            with open(status_file, 'r') as f:
                status_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            status_data = {}
        
        # Update status
        status_data.update({
            'isUpdating': status == 'updating',
            'lastUpdate': time.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            'status': status,
        })
        
        if photo_path:
            status_data['currentPhoto'] = photo_path
        
        if error:
            status_data['error'] = error
        elif 'error' in status_data:
            del status_data['error']
        
        # Save status
        with open(status_file, 'w') as f:
            json.dump(status_data, f, indent=2)
        
        logger.info(f"Display status updated: {status}")
    
    except Exception as e:
        logger.error(f"Failed to update display status: {e}")

def main():
    """Main function to update the display with a new photo"""
    if len(sys.argv) != 2:
        print("Usage: python update_display.py <image_path>")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    # Validate image path
    if not os.path.exists(image_path):
        error_msg = f"Image file not found: {image_path}"
        logger.error(error_msg)
        update_display_status('error', error=error_msg)
        print(f"ERROR: {error_msg}")
        sys.exit(1)
    
    # Update status to indicate updating
    update_display_status('updating', image_path)
    
    try:
        # Initialize display manager
        display = DisplayManager()
        
        logger.info(f"Updating display with image: {image_path}")
        
        # Display the image
        success = display.display_image(image_path)
        
        if success:
            # Update status to active
            update_display_status('active', image_path)
            logger.info("Display updated successfully")
            print("SUCCESS: Display updated")
        else:
            error_msg = "Failed to display image"
            update_display_status('error', error=error_msg)
            logger.error(error_msg)
            print(f"ERROR: {error_msg}")
            sys.exit(1)
    
    except Exception as e:
        error_msg = f"Exception during display update: {str(e)}"
        logger.error(error_msg)
        update_display_status('error', error=error_msg)
        print(f"ERROR: {error_msg}")
        sys.exit(1)

if __name__ == "__main__":
    main()