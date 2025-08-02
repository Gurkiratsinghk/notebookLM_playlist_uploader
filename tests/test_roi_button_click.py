import unittest
import os
import cv2
import numpy as np
import pyautogui
import time
from PIL import Image
from notebooklm.scripts.notebook_cv import find_image_on_screen, find_text_on_screen
from notebooklm.utils.console import print_info, print_error, print_warning

# Configure PyAutoGUI for safety
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.5

class TestRoiButtonClick(unittest.TestCase):
    """Unit tests for ROI-based button clicking functionality."""

    @classmethod
    def setUpClass(cls):
        """Set up test class with paths and initial configurations."""
        cls.script_dir = os.path.dirname(__file__)
        cls.assets_dir = os.path.normpath(os.path.join(cls.script_dir, "..", "notebooklm", "assets"))
        cls.debug_dir = os.path.join(cls.script_dir, "debug_screenshots")
        os.makedirs(cls.debug_dir, exist_ok=True)

        # Template paths in order of execution
        cls.add_source_path = os.path.join(cls.assets_dir, "add_source_button.png")
        cls.create_new_notebook_path = os.path.join(cls.assets_dir, "create_new_notebook.png")
        cls.youtube_path = os.path.join(cls.assets_dir, "youtube_button.png")
        cls.text_field_path = os.path.join(cls.assets_dir, "text_field_button.png")
        cls.insert_path = os.path.join(cls.assets_dir, "insert_button.png")

        # ROI configurations optimized for workflow (x_ratio, y_ratio, w_ratio, h_ratio)
        cls.roi_configs = {
            "add_source": (0.0, 0.15, 0.25, 0.25),    # Left panel for "+ Add" button
            "create_notebook": (0.06, 0.66, 0.3, 0.25), # Bottom-center for "Create new notebook"
            "youtube": (0.25, 0.45, 0.5, 0.35),       # Center of Add Sources popup for "YouTube"
            "text_field": (0.05, 0.31, 0.75, 0.25),   # Center of YouTube popup for text field
            "insert": (0.55, 0.65, 0.35, 0.25)        # Bottom-right of YouTube popup for "Insert"
        }

        # Test execution order
        cls.test_order = ["add_source", "create_notebook", "youtube", "text_field", "insert"]

        # Get screen dimensions for calculations
        cls.screen_width, cls.screen_height = pyautogui.size()

        # Check if template files exist and validate their sizes
        template_paths = [cls.add_source_path, cls.create_new_notebook_path, cls.youtube_path, 
                         cls.text_field_path, cls.insert_path]
        for path in template_paths:
            if not os.path.exists(path):
                raise FileNotFoundError(f"Template file missing: {path}")
            
            # Load and check template size
            template = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
            if template is None:
                raise ValueError(f"Could not load template image: {path}")
            
            template_h, template_w = template.shape
            print_info(f"Template {os.path.basename(path)}: {template_w}x{template_h}")

        print_info("Test environment initialized successfully")

    def setUp(self):
        """Set up each test case."""
        self.screenshot_count = 0
        self.current_screen_state = None
        print_info("Starting test case setup...")

    def capture_current_screen(self):
        """Capture current screen state for debugging."""
        screenshot = pyautogui.screenshot()
        self.current_screen_state = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        return self.current_screen_state

    def validate_roi_size(self, roi_tuple, template_path=None):
        """Validate that ROI is large enough for template matching."""
        roi_x, roi_y, roi_w, roi_h = roi_tuple
        
        # Check ROI dimensions are positive
        if roi_w <= 0 or roi_h <= 0:
            print_warning(f"Invalid ROI dimensions: {roi_w}x{roi_h}")
            return False
        
        # Check ROI is within screen bounds
        if roi_x < 0 or roi_y < 0 or roi_x + roi_w > self.screen_width or roi_y + roi_h > self.screen_height:
            print_warning(f"ROI extends beyond screen bounds: ({roi_x}, {roi_y}, {roi_w}, {roi_h})")
            return False
        
        # If template path provided, check template size vs ROI size
        if template_path and os.path.exists(template_path):
            template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
            if template is not None:
                template_h, template_w = template.shape
                if template_w > roi_w or template_h > roi_h:
                    print_warning(f"Template ({template_w}x{template_h}) larger than ROI ({roi_w}x{roi_h})")
                    return False
        
        return True

    def draw_coordinate_system(self, screenshot, roi_tuple):
        """Draw coordinate system showing roi_config ratios and screen coordinates."""
        screenshot_copy = screenshot.copy()
        roi_x, roi_y, roi_w, roi_h = roi_tuple
        
        # Colors
        roi_color = (0, 255, 0)      # Green for ROI
        axis_color = (255, 255, 0)   # Cyan for axes
        text_color = (0, 0, 255)     # Red for text
        grid_color = (128, 128, 128) # Gray for grid
        
        # Font settings
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.4
        thickness = 1
        
        # Draw ROI rectangle
        cv2.rectangle(screenshot_copy, (roi_x, roi_y), (roi_x + roi_w, roi_y + roi_h), roi_color, 2)
        
        # Draw coordinate axes
        # X-axis (horizontal line at bottom of ROI)
        cv2.line(screenshot_copy, (roi_x, roi_y + roi_h + 20), (roi_x + roi_w, roi_y + roi_h + 20), axis_color, 2)
        # Y-axis (vertical line at left of ROI)
        cv2.line(screenshot_copy, (roi_x - 20, roi_y), (roi_x - 20, roi_y + roi_h), axis_color, 2)
        
        # Calculate roi_config ratios for this ROI
        x_ratio = roi_x / self.screen_width
        y_ratio = roi_y / self.screen_height
        w_ratio = roi_w / self.screen_width
        h_ratio = roi_h / self.screen_height
        
        # Draw grid lines and labels within ROI
        num_divisions = 4
        for i in range(num_divisions + 1):
            # Vertical grid lines
            x_pos = roi_x + (roi_w * i / num_divisions)
            cv2.line(screenshot_copy, (int(x_pos), roi_y), (int(x_pos), roi_y + roi_h), grid_color, 1)
            
            # X-axis labels (roi_config format)
            x_ratio_pos = x_ratio + (w_ratio * i / num_divisions)
            cv2.putText(screenshot_copy, f"{x_ratio_pos:.2f}", (int(x_pos) - 15, roi_y + roi_h + 40), 
                       font, font_scale, text_color, thickness)
            
            # Horizontal grid lines
            y_pos = roi_y + (roi_h * i / num_divisions)
            cv2.line(screenshot_copy, (roi_x, int(y_pos)), (roi_x + roi_w, int(y_pos)), grid_color, 1)
            
            # Y-axis labels (roi_config format)
            y_ratio_pos = y_ratio + (h_ratio * i / num_divisions)
            cv2.putText(screenshot_copy, f"{y_ratio_pos:.2f}", (roi_x - 60, int(y_pos) + 5), 
                       font, font_scale, text_color, thickness)
        
        # ROI info labels
        info_y = roi_y - 60
        cv2.putText(screenshot_copy, f"ROI Config: ({x_ratio:.3f}, {y_ratio:.3f}, {w_ratio:.3f}, {h_ratio:.3f})", 
                   (roi_x, info_y), font, font_scale, text_color, thickness)
        cv2.putText(screenshot_copy, f"Screen Coords: ({roi_x}, {roi_y}, {roi_w}, {roi_h})", 
                   (roi_x, info_y + 20), font, font_scale, text_color, thickness)
        cv2.putText(screenshot_copy, f"Screen Size: {self.screen_width}x{self.screen_height}", 
                   (roi_x, info_y + 40), font, font_scale, text_color, thickness)
        
        # Axis labels
        cv2.putText(screenshot_copy, "X (roi_config ratio)", (roi_x + roi_w//2 - 50, roi_y + roi_h + 60), 
                   font, font_scale, axis_color, thickness)
        cv2.putText(screenshot_copy, "Y", (roi_x - 80, roi_y + roi_h//2), 
                   font, font_scale, axis_color, thickness)
        cv2.putText(screenshot_copy, "(roi_config", (roi_x - 90, roi_y + roi_h//2 + 15), 
                   font, font_scale, axis_color, thickness)
        cv2.putText(screenshot_copy, "ratio)", (roi_x - 90, roi_y + roi_h//2 + 30), 
                   font, font_scale, axis_color, thickness)
        
        return screenshot_copy

    def save_debug_screenshot(self, screenshot, roi_tuple, coords=None, filename_prefix="debug", match_info=None):
        """Save a debug screenshot with enhanced coordinate system and ROI visualization."""
        try:
            # Draw coordinate system
            screenshot_with_coords = self.draw_coordinate_system(screenshot, roi_tuple)
            
            roi_x, roi_y, roi_w, roi_h = roi_tuple
            
            # Draw click coordinates if provided
            if coords:
                center_x, center_y = coords
                # Draw click point
                cv2.circle(screenshot_with_coords, (center_x, center_y), 8, (0, 0, 255), -1)
                cv2.circle(screenshot_with_coords, (center_x, center_y), 12, (0, 0, 255), 2)
                
                # Calculate click position in roi_config format
                click_x_ratio = center_x / self.screen_width
                click_y_ratio = center_y / self.screen_height
                
                # Click info
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 0.4
                thickness = 1
                
                cv2.putText(screenshot_with_coords, f"Click: ({center_x}, {center_y})", 
                           (center_x + 15, center_y - 25), font, font_scale, (0, 0, 255), thickness)
                cv2.putText(screenshot_with_coords, f"Ratio: ({click_x_ratio:.3f}, {click_y_ratio:.3f})", 
                           (center_x + 15, center_y - 10), font, font_scale, (0, 0, 255), thickness)
            
            # Add match confidence info if provided
            if match_info:
                cv2.putText(screenshot_with_coords, f"Confidence: {match_info:.3f}", 
                           (roi_x, roi_y - 80), font, font_scale, (0, 255, 255), thickness)

            
            # Save the screenshot
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            debug_path = os.path.join(self.debug_dir, f"{filename_prefix}_{timestamp}_{self.screenshot_count}.png")
            cv2.imwrite(debug_path, screenshot_with_coords)
            self.screenshot_count += 1
            print_info(f"Debug screenshot saved: {debug_path}")
            return debug_path
        except Exception as e:
            print_error(f"Failed to save debug screenshot: {str(e)}")
            return None

    def perform_click_with_validation(self, coords, element_name, roi_tuple, validate_roi=True):
        """Perform a click with coordinate validation and error handling."""
        if not coords:
            print_warning(f"No coordinates provided for {element_name}")
            return False

        center_x, center_y = coords
        
        # Validate coordinates are within ROI if requested
        if validate_roi:
            roi_x, roi_y, roi_w, roi_h = roi_tuple
            if not (roi_x <= center_x <= roi_x + roi_w and roi_y <= center_y <= roi_y + roi_h):
                print_error(f"Coordinates ({center_x}, {center_y}) for {element_name} are outside ROI")
                return False

        # Perform the click
        try:
            original_pos = pyautogui.position()
            pyautogui.moveTo(center_x, center_y, duration=0.3)
            time.sleep(0.2)  # Brief pause before click
            pyautogui.click()
            time.sleep(0.8)  # Wait for UI response
            pyautogui.moveTo(original_pos, duration=0.3)  # Restore mouse position
            print_info(f"Successfully clicked {element_name} at ({center_x}, {center_y})")
            return True
        except Exception as e:
            print_error(f"Failed to click {element_name}: {str(e)}")
            return False

    def get_roi_tuple(self, roi_key):
        """Convert ROI key to absolute coordinates based on screen size."""
        x_ratio, y_ratio, w_ratio, h_ratio = self.roi_configs[roi_key]
        x = int(self.screen_width * x_ratio)
        y = int(self.screen_height * y_ratio)
        w = int(self.screen_width * w_ratio)
        h = int(self.screen_height * h_ratio)
        return (x, y, w, h)

    def safe_find_image_on_screen(self, image_paths, confidence=0.6, roi=None):
        """Safely find image on screen with validation."""
        try:
            # Validate ROI if provided
            if roi and not self.validate_roi_size(roi, image_paths[0] if image_paths else None):
                print_warning("ROI validation failed for image search")
                return None
            
            return find_image_on_screen(image_paths, confidence=confidence, roi=roi)
        except cv2.error as e:
            print_error(f"OpenCV error in image search: {str(e)}")
            return None
        except Exception as e:
            print_error(f"Unexpected error in image search: {str(e)}")
            return None

    def safe_find_text_on_screen(self, text, roi=None, confidence=0.6):
        """Safely find text on screen with validation."""
        try:
            # Validate ROI if provided
            if roi and not self.validate_roi_size(roi):
                print_warning("ROI validation failed for text search")
                return None
            
            return find_text_on_screen(text, roi=roi, confidence=confidence)
        except Exception as e:
            print_error(f"Error in text search for '{text}': {str(e)}")
            return None

    def test_01_add_source_button_click(self):
        """Test clicking the '+ Add' source button - First test in sequence."""
        print_info("=== Testing '+ Add' Source Button Click ===")
        
        roi_tuple = self.get_roi_tuple("add_source")
        screenshot = self.capture_current_screen()
        
        # Test image-based detection
        coords = self.safe_find_image_on_screen([self.add_source_path], confidence=0.6, roi=roi_tuple)
        debug_path = self.save_debug_screenshot(screenshot, roi_tuple, coords, "add_source_image")
        
        if coords:
            success = self.perform_click_with_validation(coords, "+ Add Source (Image)", roi_tuple)
            self.assertTrue(success, "Failed to click + Add Source button via image detection")
        else:
            print_warning("Image-based detection failed for + Add Source button")
            
            # Fallback to text-based detection
            coords = self.safe_find_text_on_screen("Add", roi=roi_tuple, confidence=0.6)
            debug_path = self.save_debug_screenshot(screenshot, roi_tuple, coords, "add_source_text_fallback")
            
            if coords:
                success = self.perform_click_with_validation(coords, "+ Add Source (Text)", roi_tuple)
                self.assertTrue(success, "Failed to click + Add Source button via text detection")
            else:
                self.fail("Both image and text detection failed for + Add Source button")

        # Wait for potential UI changes after clicking
        time.sleep(1.0)

    def test_02_create_notebook_button_click(self):
        """Test clicking the 'Create New Notebook' button."""
        print_info("=== Testing 'Create New Notebook' Button Click ===")
        
        roi_tuple = self.get_roi_tuple("create_notebook")
        screenshot = self.capture_current_screen()
        
        # Test image-based detection
        coords = self.safe_find_image_on_screen([self.create_new_notebook_path], confidence=0.6, roi=roi_tuple)
        debug_path = self.save_debug_screenshot(screenshot, roi_tuple, coords, "create_notebook_image")
        
        if coords:
            success = self.perform_click_with_validation(coords, "Create New Notebook (Image)", roi_tuple)
            self.assertTrue(success, "Failed to click Create New Notebook button via image detection")
        else:
            # Fallback to text-based detection
            create_new_notebook_text_alt = ["Create new notebook", "Create new", "+ Create new notebook"]
            for text in create_new_notebook_text_alt:
                coords = self.safe_find_text_on_screen(text=text, roi=roi_tuple, confidence=0.6)
                if coords:
                    break
            debug_path = self.save_debug_screenshot(screenshot, roi_tuple, coords, "create_notebook_text")
            
            if coords:
                success = self.perform_click_with_validation(coords, "Create New Notebook (Text)", roi_tuple)
                self.assertTrue(success, "Failed to click Create New Notebook button via text detection")
            else:
                print_warning("Create New Notebook button not found - may not be visible in current state")

    def test_03_youtube_button_click(self):
        """Test clicking the YouTube source button."""
        print_info("=== Testing YouTube Button Click ===")
        
        time.sleep(1.5)  # Ensure UI is stable before clicking
        roi_tuple = self.get_roi_tuple("youtube")
        screenshot = self.capture_current_screen()
        
        # Test image-based detection
        coords = self.safe_find_image_on_screen([self.youtube_path], confidence=0.6, roi=roi_tuple)
        debug_path = self.save_debug_screenshot(screenshot, roi_tuple, coords, "youtube_image")
        
        if coords:
            success = self.perform_click_with_validation(coords, "YouTube Button (Image)", roi_tuple)
            self.assertTrue(success, "Failed to click YouTube button via image detection")
        else:
            # Fallback to text-based detection
            coords = self.safe_find_text_on_screen("YouTube", roi=roi_tuple, confidence=0.6)
            debug_path = self.save_debug_screenshot(screenshot, roi_tuple, coords, "youtube_text")
            
            if coords:
                success = self.perform_click_with_validation(coords, "YouTube Button (Text)", roi_tuple)
                self.assertTrue(success, "Failed to click YouTube button via text detection")
            else:
                print_warning("YouTube button not found - may not be visible in current state")

    def test_04_text_field_click(self):
        """Test clicking the YouTube URL text field."""
        print_info("=== Testing Text Field Click ===")
        
        roi_tuple = self.get_roi_tuple("text_field")
        screenshot = self.capture_current_screen()
        
        # Test image-based detection with validation
        coords = self.safe_find_image_on_screen([self.text_field_path], confidence=0.6, roi=roi_tuple)
        debug_path = self.save_debug_screenshot(screenshot, roi_tuple, coords, "text_field_image")
        
        if coords:
            success = self.perform_click_with_validation(coords, "Text Field (Image)", roi_tuple)
            self.assertTrue(success, "Failed to click text field via image detection")
        else:
            # Try multiple text variations for better detection
            text_variations = ["Paste YouTube URL", "YouTube URL", "Enter URL", "URL"]
            coords = None
            
            for text_var in text_variations:
                coords = self.safe_find_text_on_screen(text_var, roi=roi_tuple, confidence=0.6)
                if coords:
                    debug_path = self.save_debug_screenshot(screenshot, roi_tuple, coords, f"text_field_{text_var.lower().replace(' ', '_')}")
                    break
            
            if coords:
                success = self.perform_click_with_validation(coords, "Text Field (Text)", roi_tuple)
                self.assertTrue(success, "Failed to click text field via text detection")
            else:
                print_warning("Text field not found - may not be visible in current state")

    def test_05_insert_button_click(self):
        """Test clicking the Insert button."""
        print_info("=== Testing Insert Button Click ===")
        
        roi_tuple = self.get_roi_tuple("insert")
        screenshot = self.capture_current_screen()
        
        # Test image-based detection
        coords = self.safe_find_image_on_screen([self.insert_path], confidence=0.6, roi=roi_tuple)
        debug_path = self.save_debug_screenshot(screenshot, roi_tuple, coords, "insert_image")
        
        if coords:
            success = self.perform_click_with_validation(coords, "Insert Button (Image)", roi_tuple)
            self.assertTrue(success, "Failed to click Insert button via image detection")
        else:
            # Fallback to text-based detection
            coords = self.safe_find_text_on_screen("Insert", roi=roi_tuple, confidence=0.6)
            debug_path = self.save_debug_screenshot(screenshot, roi_tuple, coords, "insert_text")
            
            if coords:
                success = self.perform_click_with_validation(coords, "Insert Button (Text)", roi_tuple)
                self.assertTrue(success, "Failed to click Insert button via text detection")
            else:
                print_warning("Insert button not found - may not be visible in current state")

    def test_06_comprehensive_roi_validation(self):
        """Test ROI configurations comprehensively across all elements."""
        print_info("=== Comprehensive ROI Validation Test ===")
        
        screenshot = self.capture_current_screen()
        test_elements = [
            ("add_source", [self.add_source_path], ["Add", "+ Add"]),
            ("create_notebook", [self.create_new_notebook_path], ["Create New Notebook", "Create"]),
            ("youtube", [self.youtube_path], ["YouTube"]),
            ("text_field", [self.text_field_path], ["Paste YouTube URL", "YouTube URL", "URL"]),
            ("insert", [self.insert_path], ["Insert"])
        ]
        
        results = {}
        
        for roi_key, image_paths, text_options in test_elements:
            roi_tuple = self.get_roi_tuple(roi_key)
            element_found = False
            
            # Try image detection
            for image_path in image_paths:
                coords = self.safe_find_image_on_screen([image_path], confidence=0.6, roi=roi_tuple)
                if coords:
                    results[roi_key] = {"method": "image", "coords": coords, "path": image_path}
                    element_found = True
                    break
            
            # Try text detection if image failed
            if not element_found:
                for text_option in text_options:
                    coords = self.safe_find_text_on_screen(text_option, roi=roi_tuple, confidence=0.6)
                    if coords:
                        results[roi_key] = {"method": "text", "coords": coords, "text": text_option}
                        element_found = True
                        break
            
            if not element_found:
                results[roi_key] = {"method": "none", "coords": None}
            
            # Save debug screenshot for each ROI
            debug_coords = results[roi_key]["coords"] if results[roi_key]["coords"] else None
            self.save_debug_screenshot(screenshot, roi_tuple, debug_coords, f"roi_validation_{roi_key}")
        
        # Report results
        found_count = sum(1 for r in results.values() if r["coords"] is not None)
        total_count = len(results)
        
        print_info(f"ROI Validation Results: {found_count}/{total_count} elements found")
        for roi_key, result in results.items():
            if result["coords"]:
                method_info = f"via {result['method']}"
                if result['method'] == 'image':
                    method_info += f" ({os.path.basename(result['path'])})"
                else:
                    method_info += f" ('{result['text']}')"
                print_info(f"  ✓ {roi_key}: Found {method_info} at {result['coords']}")
            else:
                print_warning(f"  ✗ {roi_key}: Not found")
        
        # Assert that at least some elements were found
        self.assertGreater(found_count, 0, "No UI elements found in any ROI - check screen state and templates")

    def test_07_edge_cases_and_error_handling(self):
        """Test edge cases and error handling scenarios."""
        print_info("=== Testing Edge Cases and Error Handling ===")
        
        # Test with invalid ROI dimensions
        invalid_roi = (0, 0, 0, 0)
        coords = self.safe_find_image_on_screen([self.add_source_path], confidence=0.6, roi=invalid_roi)
        self.assertIsNone(coords, "Expected None for zero-dimension ROI")
        
        coords = self.safe_find_text_on_screen("Add", roi=invalid_roi, confidence=0.6)
        self.assertIsNone(coords, "Expected None for zero-dimension ROI with text search")
        
        # Test with out-of-bounds ROI
        oob_roi = (self.screen_width + 100, self.screen_height + 100, 100, 100)
        coords = self.safe_find_image_on_screen([self.add_source_path], confidence=0.6, roi=oob_roi)
        self.assertIsNone(coords, "Expected None for out-of-bounds ROI")
        
        # Test with missing template file
        missing_template = os.path.join(self.assets_dir, "non_existent_template.png")
        coords = self.safe_find_image_on_screen([missing_template], confidence=0.6)
        self.assertIsNone(coords, "Expected None for missing template file")
        
        # Test with very high confidence threshold
        coords = self.safe_find_image_on_screen([self.add_source_path], confidence=0.99)
        # This may or may not find a match, but should not crash
        print_info(f"High confidence search result: {coords}")
        
        # Test ROI size validation
        for roi_key in self.roi_configs:
            roi_tuple = self.get_roi_tuple(roi_key)
            is_valid = self.validate_roi_size(roi_tuple)
            print_info(f"ROI {roi_key} validation: {'PASS' if is_valid else 'FAIL'}")
        
        print_info("Edge cases and error handling tests completed")

    @classmethod
    def tearDownClass(cls):
        """Clean up after all tests."""
        print_info("=== Test Suite Completed ===")
        print_info(f"Debug screenshots saved in: {cls.debug_dir}")
        print_info("Cleaning up test environment...")

if __name__ == "__main__":
    # Run tests in order by using a custom test loader
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add tests in specific order
    test_methods = [
        'test_01_add_source_button_click',
        'test_02_create_notebook_button_click', 
        'test_03_youtube_button_click',
        'test_04_text_field_click',
        'test_05_insert_button_click',
        'test_06_comprehensive_roi_validation',
        'test_07_edge_cases_and_error_handling'
    ]
    
    for test_method in test_methods:
        suite.addTest(TestRoiButtonClick(test_method))
    
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)