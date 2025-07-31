import cv2
import numpy as np
import pyautogui
import keyboard
import time
from PIL import ImageGrab

# File paths for your template images
plus_template = "assets/add_source_button.png" 
plus_template_2 = "assets/add_source_button_alt.png"
youtube_template = "assets/youtube_button.png"
text_field_template = "assets/text_field_button.png"  # Use this if you have a distinct image for the text field
insert_template = "assets/insert_button.png"


def find_image_on_screen(template_path, confidence=0.9, grayscale=True):
    """
    Capture the screen and use template matching to find the given template image.
    Returns the center coordinates of the first matched location or None if not found.
    """
    # Load the template image
    template = cv2.imread(template_path, 0 if grayscale else 1)
    if template is None:
        print(f"Template not found: {template_path}")
        return None

    template_w, template_h = template.shape[::-1] if grayscale else (template.shape[1], template.shape[0])
    
    # Take a screenshot using pyautogui
    screenshot = pyautogui.screenshot()
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    
    # Convert screenshot to grayscale if needed
    if grayscale:
        screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
    else:
        screenshot_gray = screenshot
    
    # Use template matching
    res = cv2.matchTemplate(screenshot_gray, template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= confidence)
    points = list(zip(*loc[::-1]))
    
    if points:
        # Get the first matched position and compute its center
        pt = points[0]
        center_x = pt[0] + template_w // 2
        center_y = pt[1] + template_h // 2
        return center_x, center_y
    else:
        return None
    

def notebook_cv(youtube_urls: list[str]):

    for url in youtube_urls:
        # Step 1: Click the '+ Add Source' button
        time.sleep(6)  # Give some time for the UI to settle
        coords = find_image_on_screen(plus_template)
        coords_2 = find_image_on_screen(plus_template_2)

        if coords:
            pyautogui.moveTo(coords[0], coords[1], duration=0.5)
            pyautogui.click()
            print("Clicked '+ Add Source'")
        elif coords_2:
            pyautogui.moveTo(coords_2[0], coords_2[1], duration=0.5)
            pyautogui.click()
            print("Clicked '+ Add Source'")
        else:
            print("Could not find '+ Add Source' button.")
            continue  # Skip to next URL if not found

        # Step 2: In the popup, click the 'Youtube' button
        time.sleep(2)
        coords = find_image_on_screen(youtube_template)
        if coords:
            pyautogui.moveTo(coords[0], coords[1], duration=0.5)
            pyautogui.click()
            print("Clicked 'Youtube'")
        else:
            print("Could not find 'Youtube' button.")
            continue

        # Step 3: In the next popup, click the text field to focus it
        time.sleep(2)
        coords = find_image_on_screen(text_field_template)
        if coords:
            pyautogui.moveTo(coords[0], coords[1], duration=0.5)
            pyautogui.click()
            print("Clicked on the text field")
        else:
            print("Could not find the text field.")
            continue

        # Step 4: Type (paste) the URL into the field
        time.sleep(1)
        keyboard.write(url, delay=0.05)
        print(f"Typed URL: {url}")

        # Step 5: Click the 'Insert' button
        time.sleep(1)
        coords = find_image_on_screen(insert_template)
        if coords:
            pyautogui.moveTo(coords[0], coords[1], duration=0.5)
            pyautogui.click()
            print("Clicked 'Insert'")
        else:
            print("Could not find 'Insert' button.")
            continue

        # Wait a moment before processing the next URL
        time.sleep(5)
