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


def find_image_on_screen(template_paths, confidence=0.6, grayscale=True, roi=None):
    """
    Searches for one of the given template images on the screen using template matching.

    Args:
        template_paths (list[str]): List of file paths to template images.
        confidence (float): Minimum confidence threshold for a match (default 0.9).
        grayscale (bool): Whether to convert images to grayscale (default True).
        roi (tuple[int, int, int, int] or None): Optional region of interest as (x, y, width, height).

    Returns:
        tuple[int, int] or None: Center coordinates (x, y) of the best match, or None if not found.
    """
    screenshot = pyautogui.screenshot()
    screenshot = np.array(screenshot)
    roi_x, roi_y = 0, 0
    if roi:
        roi_x, roi_y, roi_w, roi_h = roi
        screenshot = screenshot[roi_y:roi_y+roi_h, roi_x:roi_x+roi_w]
        if screenshot.size == 0:
            print_error("Invalid ROI dimensions")
            return None

    if grayscale:
        screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
    else:
        screenshot_gray = screenshot

    best_match = None
    highest_conf = -1
    best_template = None

    for template_path in template_paths:
        template = cv2.imread(template_path, 0 if grayscale else 1)
        if template is None:
            print_error(f"Template not found: {template_path}")
            continue

        template_w, template_h = template.shape[1], template.shape[0]
        res = cv2.matchTemplate(screenshot_gray, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

        if max_val >= confidence and max_val > highest_conf:
            highest_conf = max_val
            center_x = max_loc[0] + template_w // 2 + roi_x
            center_y = max_loc[1] + template_h // 2 + roi_y
            best_match = (center_x, center_y)
            best_template = template_path
            print_info(f"Detected template {template_path} at ({center_x}, {center_y}) with confidence {max_val}")

    if best_match:
        print_info(f"Selected best match for {best_template} at {best_match} with confidence {highest_conf}")
        return best_match
    else:
        print_warning(f"No match found for any template with confidence >= {confidence}")
        return None


def find_text_on_screen(text, roi=None, confidence=0.6):
    """
    Searches for the specified text on the screen using OCR.

    Args:
        text (str): The text string to search for.
        roi (tuple, optional): A region of interest as (x, y, width, height).
        confidence (float, optional): Minimum confidence threshold (0.0 to 1.0).

    Returns:
        tuple or None: (center_x, center_y) coordinates of the best match, or None if not found.
    """
    screenshot = pyautogui.screenshot()
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    
    x_offset, y_offset = 0, 0
    if roi:
        x, y, w, h = roi
        screenshot = screenshot[y:y+h, x:x+w]
        x_offset, y_offset = x, y
    
    pil_image = Image.fromarray(screenshot)
    ocr_data = pytesseract.image_to_data(pil_image, output_type=pytesseract.Output.DICT)
    
    best_match = None
    highest_conf = -1
    for i, detected_text in enumerate(ocr_data["text"]):
        try:
            conf_val = float(ocr_data["conf"][i])
        except (ValueError, TypeError):
            conf_val = -1
        if detected_text.lower() == text.lower() and conf_val >= confidence * 100:
            center_x = ocr_data["left"][i] + ocr_data["width"][i] // 2 + x_offset
            center_y = ocr_data["top"][i] + ocr_data["height"][i] // 2 + y_offset
            if conf_val > highest_conf:
                highest_conf = conf_val
                best_match = (center_x, center_y)
            print_info(f"Detected '{detected_text}' at ({center_x}, {center_y}) with confidence {conf_val}")
    
    if best_match:
        print_info(f"Selected best match for '{text}' at {best_match} with confidence {highest_conf}")
        return best_match
    else:
        print_warning(f"No match found for '{text}' with confidence >= {confidence}")
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


def get_dynamic_roi(element_type="default", width_ratio=0.5, height_ratio=0.35):
    """
    Calculates a dynamic ROI based on the current screen size and element type.
    """
    screen_width, screen_height = pyautogui.size()
    
    roi_configs = {
            "add_source": (0.0, 0.15, 0.25, 0.25),    # Left panel for "+ Add" button
            "create_notebook": (0.06, 0.66, 0.3, 0.25), # Bottom-center for "Create new notebook"
            "youtube": (0.25, 0.45, 0.5, 0.35),       # Center of Add Sources popup for "YouTube"
            "text_field": (0.05, 0.31, 0.75, 0.25),   # Center of YouTube popup for text field
            "insert": (0.55, 0.65, 0.35, 0.25)        # Bottom-right of YouTube popup for "Insert"
        }
    
    x_ratio, y_ratio, w_ratio, h_ratio = roi_configs.get(element_type, (0.0, 0.0, width_ratio, height_ratio))
    x = int(screen_width * x_ratio)
    y = int(screen_height * y_ratio)
    w = int(screen_width * w_ratio)
    h = int(screen_height * h_ratio)
    return (x, y, w, h)


def notebook_cv(youtube_urls: list[str]):
    """
    Automates the process of adding YouTube URLs as sources to a notebook by interacting with the UI.
    """
    for url in youtube_urls:
        print_progress(f"Processing URL: {url}")
        
        # Step 1: Click "+ Add" to open the Add Sources popup
        max_retries = 3
        for attempt in range(max_retries):
            coords = find_text_on_screen("+ Add", roi=get_dynamic_roi("add_source"), confidence=0.9)
            if not coords:
                coords = find_image_on_screen([add_source_path, add_source_alt_path], confidence=0.9, roi=get_dynamic_roi("add_source"))
            if coords:
                pyautogui.moveTo(coords[0], coords[1], duration=0.5)
                pyautogui.click()
                print_info("Clicked '+ Add'")
                time.sleep(2)
                break
            else:
                print_warning(f"Attempt {attempt + 1}: Could not find '+ Add' button")
                time.sleep(1)
        else:
            print_error("Failed to find '+ Add' button after retries, skipping URL")
            continue

        # Step 2: Click "YouTube" in the Add Sources popup
        for attempt in range(max_retries):
            coords = find_text_on_screen("YouTube", roi=get_dynamic_roi("youtube"), confidence=0.9)
            if not coords:
                coords = find_image_on_screen([youtube_path], confidence=0.7, roi=get_dynamic_roi("youtube"))
            if coords:
                pyautogui.moveTo(coords[0], coords[1], duration=0.5)
                pyautogui.click()
                print_info("Clicked 'YouTube'")
                time.sleep(2)
                break
            else:
                print_warning(f"Attempt {attempt + 1}: Could not find 'YouTube' button")
                time.sleep(1)
        else:
            print_error("Failed to find 'YouTube' button after retries, skipping URL")
            continue

        # Step 3: Click text field and type URL
        for attempt in range(max_retries):
            text_variations = ["Paste YouTube URL", "YouTube URL", "Paste YouTube", "URL"]
            coords = None
            for variation in text_variations:
                coords = find_text_on_screen(variation, roi=get_dynamic_roi("text_field"), confidence=0.7)
                if coords:
                    break
            if not coords:
                coords = find_image_on_screen([text_field_path], confidence=0.7, roi=get_dynamic_roi("text_field"))
            if coords:
                pyautogui.moveTo(coords[0], coords[1], duration=0.5)
                pyautogui.click()
                print_info("Clicked text field")
                time.sleep(0.5)
                keyboard.write(url, delay=0.05)
                print_progress(f"Typed URL: {url}")
                break
            else:
                print_warning(f"Attempt {attempt + 1}: Could not find 'Paste YouTube URL*'")
                time.sleep(1)
        else:
            print_error("Failed to find 'Paste YouTube URL*' after retries, skipping URL")
            continue

        # Step 4: Click "Insert"
        for attempt in range(max_retries):
            coords = find_image_on_screen([insert_path], confidence=0.9, roi=get_dynamic_roi("insert"))
            if coords:
                pyautogui.moveTo(coords[0], coords[1], duration=0.5)
                pyautogui.click()
                print_info("Clicked 'Insert'")
                time.sleep(5)
                break
            else:
                print_warning(f"Attempt {attempt + 1}: Could not find 'Insert' button")
                time.sleep(1)
        else:
            print_error("Failed to find 'Insert' button after retries, skipping URL")
            continue
        
        time.sleep(5)