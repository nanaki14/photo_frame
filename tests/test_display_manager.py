#!/usr/bin/env python3
"""
Unit tests for display_manager.py
Tests the critical display functionality without requiring actual hardware
"""

import unittest
import tempfile
import os
import sys
from unittest.mock import patch, MagicMock
from PIL import Image

# Add display directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'display'))

from display_manager import DisplayManager, MockEPD, get_epd_instance

class TestDisplayManager(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.display_manager = DisplayManager()
        
    def test_display_manager_initialization(self):
        """Test that DisplayManager initializes correctly"""
        self.assertIsNotNone(self.display_manager)
        self.assertEqual(self.display_manager.display_width, 800)
        self.assertEqual(self.display_manager.display_height, 480)
        self.assertFalse(self.display_manager.is_initialized)
    
    def test_mock_epd_functionality(self):
        """Test that MockEPD works correctly"""
        mock_epd = MockEPD()
        self.assertEqual(mock_epd.width, 800)
        self.assertEqual(mock_epd.height, 480)
        
        # Test initialization
        result = mock_epd.init()
        self.assertEqual(result, 0)
        
        # Test display method doesn't crash
        test_image = Image.new('RGB', (800, 480), 'white')
        mock_epd.display(test_image)
        
        # Test clear and sleep methods
        mock_epd.Clear()
        mock_epd.sleep()
    
    def test_image_optimization(self):
        """Test image optimization for e-ink display"""
        # Create a test image
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
            test_image = Image.new('RGB', (1600, 1200), 'blue')
            test_image.save(tmp.name, 'JPEG')
            tmp_path = tmp.name
        
        try:
            # Test image optimization
            optimized = self.display_manager.optimize_image_for_eink(tmp_path)
            
            self.assertIsNotNone(optimized)
            self.assertEqual(optimized.size, (800, 480))
            self.assertEqual(optimized.mode, 'L')  # Grayscale
            
        finally:
            os.unlink(tmp_path)
    
    def test_image_optimization_with_invalid_file(self):
        """Test image optimization with invalid file"""
        result = self.display_manager.optimize_image_for_eink('nonexistent.jpg')
        self.assertIsNone(result)
    
    def test_display_initialization(self):
        """Test display initialization"""
        # This should work with MockEPD
        result = self.display_manager.initialize()
        self.assertTrue(result)
        self.assertTrue(self.display_manager.is_initialized)
    
    def test_display_image_workflow(self):
        """Test complete image display workflow"""
        # Create a test image
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
            test_image = Image.new('RGB', (400, 300), 'red')
            test_image.save(tmp.name, 'JPEG')
            tmp_path = tmp.name
        
        try:
            # Test image display
            result = self.display_manager.display_image(tmp_path)
            self.assertTrue(result)
            
        finally:
            os.unlink(tmp_path)
    
    def test_display_message(self):
        """Test text message display"""
        result = self.display_manager.display_message("Test Message")
        self.assertTrue(result)
    
    def test_clear_display(self):
        """Test display clearing"""
        result = self.display_manager.clear_display()
        self.assertTrue(result)
    
    def test_get_status(self):
        """Test status retrieval"""
        status = self.display_manager.get_status()
        
        self.assertIsInstance(status, dict)
        self.assertIn('initialized', status)
        self.assertIn('width', status)
        self.assertIn('height', status)
        self.assertIn('type', status)
        self.assertIn('last_update', status)
        
        self.assertEqual(status['width'], 800)
        self.assertEqual(status['height'], 480)
    
    def test_epd_instance_creation(self):
        """Test EPD instance creation (should return MockEPD)"""
        epd = get_epd_instance()
        self.assertIsInstance(epd, MockEPD)

class TestPerformanceOptimizations(unittest.TestCase):
    """Test performance optimization features"""
    
    def test_system_info_detection(self):
        """Test system information detection"""
        # Import the system info detection
        from display_manager import SYSTEM_INFO
        
        self.assertIsInstance(SYSTEM_INFO, dict)
        self.assertIn('is_pi', SYSTEM_INFO)
        self.assertIn('memory_mb', SYSTEM_INFO)
        self.assertIn('cpu_count', SYSTEM_INFO)
        self.assertIn('is_low_memory', SYSTEM_INFO)
    
    def test_memory_optimization_path(self):
        """Test that memory optimization paths work"""
        display_manager = DisplayManager()
        
        # Create a large test image to trigger optimization
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
            test_image = Image.new('RGB', (3000, 2000), 'green')
            test_image.save(tmp.name, 'JPEG')
            tmp_path = tmp.name
        
        try:
            # This should work even with large images
            optimized = display_manager.optimize_image_for_eink(tmp_path)
            self.assertIsNotNone(optimized)
            self.assertEqual(optimized.size, (800, 480))
            
        finally:
            os.unlink(tmp_path)

if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)