# import cv2
# import numpy as np
# import pyautogui
# import keyboard
# import time
# from PIL import ImageGrab

# # File paths for your template images
# plus_template = "assets/add_source_button.png" 
# plus_template_2 = "assets/add_source_button_alt.png"
# youtube_template = "assets/youtube_button.png"
# text_field_template = "assets/text_field_button.png"  # Use this if you have a distinct image for the text field
# insert_template = "assets/insert_button.png"


# def find_image_on_screen(template_path, confidence=0.6, grayscale=True):
#     """
#     Capture the screen and use template matching to find the given template image.
#     Returns the center coordinates of the first matched location or None if not found.
#     """
#     # Load the template image
#     template = cv2.imread(template_path, 0 if grayscale else 1)
#     if template is None:
#         print(f"Template not found: {template_path}")
#         return None

#     template_w, template_h = template.shape[::-1] if grayscale else (template.shape[1], template.shape[0])
    
#     # Take a screenshot using pyautogui
#     screenshot = pyautogui.screenshot()
#     screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    
#     # Convert screenshot to grayscale if needed
#     if grayscale:
#         screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
#     else:
#         screenshot_gray = screenshot
    
#     # Use template matching
#     res = cv2.matchTemplate(screenshot_gray, template, cv2.TM_CCOEFF_NORMED)
#     loc = np.where(res >= confidence)
#     points = list(zip(*loc[::-1]))
    
#     if points:
#         # Get the first matched position and compute its center
#         pt = points[0]
#         center_x = pt[0] + template_w // 2
#         center_y = pt[1] + template_h // 2
#         return center_x, center_y
#     else:
#         return None
    

# def notebook_cv(youtube_urls: list[str]):

#     for url in youtube_urls:
#         # Step 1: Click the '+ Add Source' button
#         time.sleep(6)  # Give some time for the UI to settle
#         coords = find_image_on_screen(plus_template)
#         coords_2 = find_image_on_screen(plus_template_2)

#         if coords:
#             pyautogui.moveTo(coords[0], coords[1], duration=0.5)
#             pyautogui.click()
#             print("Clicked '+ Add Source'")
#         elif coords_2:
#             pyautogui.moveTo(coords_2[0], coords_2[1], duration=0.5)
#             pyautogui.click()
#             print("Clicked '+ Add Source'")
#         else:
#             print("Could not find '+ Add Source' button.")
#             continue  # Skip to next URL if not found

#         # Step 2: In the popup, click the 'Youtube' button
#         time.sleep(2)
#         coords = find_image_on_screen(youtube_template)
#         if coords:
#             pyautogui.moveTo(coords[0], coords[1], duration=0.5)
#             pyautogui.click()
#             print("Clicked 'Youtube'")
#         else:
#             print("Could not find 'Youtube' button.")
#             continue

#         # Step 3: In the next popup, click the text field to focus it
#         time.sleep(2)
#         coords = find_image_on_screen(text_field_template)
#         if coords:
#             pyautogui.moveTo(coords[0], coords[1], duration=0.5)
#             pyautogui.click()
#             print("Clicked on the text field")
#         else:
#             print("Could not find the text field.")
#             continue

#         # Step 4: Type (paste) the URL into the field
#         time.sleep(1)
#         keyboard.write(url, delay=0.05)
#         print(f"Typed URL: {url}")

#         # Step 5: Click the 'Insert' button
#         time.sleep(1)
#         coords = find_image_on_screen(insert_template)
#         if coords:
#             pyautogui.moveTo(coords[0], coords[1], duration=0.5)
#             pyautogui.click()
#             print("Clicked 'Insert'")
#         else:
#             print("Could not find 'Insert' button.")
#             continue

#         # Wait a moment before processing the next URL
#         time.sleep(5)






import time
import os
import cv2
import numpy as np
import pyautogui
import keyboard # Import keyboard for typing
import pytesseract
from PIL import Image
from ..utils.console import (
    print_error, print_info, print_progress,
    print_warning, print_header
)
from .path import path  # Import the path variable from the path module


pytesseract.pytesseract.tesseract_cmd = path  # Set the path to the Tesseract executable

script_dir = os.path.dirname(__file__)
assets_dir = os.path.normpath(os.path.join(script_dir, "..", "assets"))
    
# Define template paths
create_new_notebook_path = os.path.join(assets_dir, "create_new_notebook.png")
add_source_path = os.path.join(assets_dir, "add_source_button.png")
add_source_alt_path = os.path.join(assets_dir, "add_source_button_alt.png")
youtube_path = os.path.join(assets_dir, "youtube_button.png")
text_field_path = os.path.join(assets_dir, "text_field_button.png")
insert_path = os.path.join(assets_dir, "insert_button.png")


def find_image_on_screen(template_paths, confidence=0.8, grayscale=True, roi=None):
    """
    Searches for one of the given template images on the screen using template matching.

    Args:
        template_paths (list[str]): List of file paths to template images.
        confidence (float): Minimum confidence threshold for a match (default 0.8).
        grayscale (bool): Whether to convert images to grayscale before matching (default True).
        roi (tuple[int, int, int, int] or None): Optional region of interest as (x, y, width, height).

    Returns:
        tuple[int, int] or None: Center coordinates (x, y) of the first matched template, or None if not found.
    """
    screenshot = pyautogui.screenshot()
    screenshot = np.array(screenshot)
    roi_x, roi_y = 0, 0 # Initialize ROI offset
    if roi:
        roi_x, roi_y, roi_w, roi_h = roi
        screenshot = screenshot[roi_y:roi_y+roi_h, roi_x:roi_x+roi_w]
        if screenshot.size == 0:
            print_error("Invalid ROI dimensions")
            return None  # Return None if ROI is empty

    if grayscale:
        screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
    else:
        screenshot_gray = screenshot

    for template_path in template_paths:
        template = cv2.imread(template_path, 0 if grayscale else 1)
        if template is None:
            print_error(f"Template not found: {template_path}")
            continue

        template_w, template_h = template.shape[1], template.shape[0]
        res = cv2.matchTemplate(screenshot_gray, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

        if max_val >= confidence:
            center_x = max_loc[0] + template_w // 2 + (roi_x if roi else 0)
            center_y = max_loc[1] + template_h // 2 + (roi_y if roi else 0)
            print_info(f"Found template {template_path} at ({center_x}, {center_y})")
            return center_x, center_y
    return None


def find_text_on_screen(text, roi=None, confidence=0.8):
    """
    Searches for the specified text on the screen using OCR.

    Args:
        text (str): The text string to search for.
        roi (tuple, optional): A region of interest as (x, y, width, height) to limit the search area.
        confidence (float, optional): Minimum confidence threshold (0.0 to 1.0) for text detection.

    Returns:
        tuple or None: (center_x, center_y) coordinates of the detected text center, or None if not found.
    """
    screenshot = pyautogui.screenshot()
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    
    x_offset, y_offset = 0, 0 # Initialize x_offset, y_offset for ROI offset

    if roi:
        x, y, w, h = roi
        screenshot = screenshot[y:y+h, x:x+w]
    
    pil_image = Image.fromarray(screenshot)
    ocr_data = pytesseract.image_to_data(pil_image, output_type=pytesseract.Output.DICT)
    
    for i, detected_text in enumerate(ocr_data["text"]):
        try:
            conf_val = float(ocr_data["conf"][i])
        except (ValueError, TypeError):
            conf_val = -1  # Treat as low confidence if parsing fails
        if detected_text.lower() == text.lower() and conf_val >= confidence * 100:
            center_x = ocr_data["left"][i] + ocr_data["width"][i] // 2 + (roi[0] if roi else 0)
            center_y = ocr_data["top"][i] + ocr_data["height"][i] // 2 + (roi[1] if roi else 0)
            print_info(f"Found text '{detected_text}' at ({center_x}, {center_y})")
            return center_x, center_y
    return None


def youtube_button_click(): 
    """
    Checks and Clicks the YouTube button in the notebook UI.
    
    Returns:
        None if the button is not found.
    """
    # Check for "YouTube" button first
    coords = find_text_on_screen("YouTube", confidence=0.6)
    if not coords:
        # Fallback to image matching
        coords = find_image_on_screen([youtube_path], confidence=0.6)
    if coords:
        pyautogui.moveTo(coords[0], coords[1], duration=0.5)
        pyautogui.click()
        print_info("Clicked 'YouTube'")
    if not coords:
        print_warning("Could not find 'YouTube' button")
    return None


def add_source_button_click():
    """
    Checks and Clicks the Add Source button in the notebook UI.
    Returns:
        None if the button is not found.
    """
    # Check for "YouTube" button first
    coords = find_text_on_screen("Add", confidence=0.6)
    if not coords:
        # Fallback to image matching
        coords = find_image_on_screen([add_source_path, add_source_alt_path], confidence=0.6)
    if coords:
        pyautogui.moveTo(coords[0], coords[1], duration=0.5)
        pyautogui.click()
        print_info("Clicked '+ Add'")
    if not coords:
        print_warning("Could not find '+ Add' button")
    return None



def get_dynamic_roi(width_ratio=0.5, height_ratio=0.15, x_offset_ratio=0.0, y_offset_ratio=0.0):
    """
    Calculates a dynamic ROI based on the current screen size and provided ratios.
    Returns a tuple (x, y, w, h).
    """
    screen_width, screen_height = pyautogui.size()
    x = int(screen_width * x_offset_ratio)
    y = int(screen_height * y_offset_ratio)
    w = int(screen_width * width_ratio)
    h = int(screen_height * height_ratio)
    coords = find_image_on_screen([create_new_notebook_path], confidence=0.6, roi=(0, 0, 800, 200))
def notebook_cv(youtube_urls: list[str]):
    """
    Automates the process of adding YouTube URLs as sources to a notebook by interacting with the UI using image recognition and OCR.

    Args:
        youtube_urls (list[str]): A list of YouTube video URLs to be added as sources.
    """
    roi = get_dynamic_roi()  # Calculate ROI dynamically based on screen size
    for url in youtube_urls:
        # Try OCR first for "Create New Notebook"
        coords = find_text_on_screen("Create New Notebook", roi=roi, confidence=0.8)
        if not coords:
            # Fallback to template matching
            coords = find_image_on_screen([create_new_notebook_path], confidence=0.6, roi=roi)
        if coords:
            pyautogui.moveTo(coords[0], coords[1], duration=0.5)
            pyautogui.click()
            print_info("Clicked 'Create New Notebook'")
            coords = find_image_on_screen([text_field_path], confidence=0.6, roi=(0, 0, 800, 200))
            continue
        
        # First, try clicking the "YouTube" button in case the "Add Source" window is already open.
        time.sleep(2)
        youtube_button_click()
        
        # Always attempt to click the "+ Add" button, regardless of previous result
        add_source_button_click()
        
        # Wait for the "Add Source" window to appear, then click the "YouTube" button again.
        time.sleep(2)
        youtube_button_click()
        
        # Text field
        coords = find_image_on_screen(
                [insert_path],
                confidence=0.6,
                roi=(0, 0, 800, 200)
            )
        if coords:
            pyautogui.moveTo(coords[0], coords[1], duration=0.5)
            pyautogui.click()
            print_info("Clicked text field")
            keyboard.write(url, delay=0.05)
        if coords:
            pyautogui.moveTo(coords[0], coords[1], duration=0.5)
            pyautogui.click()
            print_info("Clicked text field")
            # Verify focus by checking if the text field is still present after click, retry if not
            max_retries = 3
            for attempt in range(max_retries):
                time.sleep(0.5)
                # Optionally, check if the text field is still present (OCR or template)
                verify_coords = find_text_on_screen("Paste YouTube URL*", roi=roi, confidence=0.6)
                if not verify_coords:
                    verify_coords = find_image_on_screen([text_field_path], confidence=0.6, roi=roi)
                if verify_coords:
                    keyboard.write(url, delay=0.05)
                    print_progress(f"Typed URL: {url}")
                    break
                else:
                    pyautogui.click()  # Try clicking again
                    print_warning("Retrying click on text field")
            else:
                print_error("Failed to focus text field after retries, skipping URL")
                continue
        else:
            print_warning("Could not find text field")
            continue
            # Fallback to template matching
            coords = find_image_on_screen(
                [insert_path],
                confidence=0.6,
                roi=roi
            )
        if coords:
            pyautogui.moveTo(coords[0], coords[1], duration=0.5)
            pyautogui.click()
            print_info("Clicked 'Insert'")
        else:
            print_warning("Could not find 'Insert' button")
            continue
        
        time.sleep(5)