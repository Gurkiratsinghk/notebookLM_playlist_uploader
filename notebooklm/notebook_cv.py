import cv2
import numpy as np
import pyautogui
import keyboard
import time

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

# List of YouTube URLs to add
youtube_urls = [
        # 'https://www.youtube.com/watch?v=K5tUbZzcOEc',
        # 'https://www.youtube.com/watch?v=nG47fQ-aiHw',
        # 'https://www.youtube.com/watch?v=w6R6V1Mpz7s',
        # 'https://www.youtube.com/watch?v=So_UGo4dSJs',
        # 'https://www.youtube.com/watch?v=H8U0a9bwxqc',
        # 'https://www.youtube.com/watch?v=uL8C9wQrk3g',
        # 'https://www.youtube.com/watch?v=EFONLmsmVFw',
        # 'https://www.youtube.com/watch?v=Ih92AK1D-2M',
        # 'https://www.youtube.com/watch?v=AGj73UQN-K0',
        # 'https://www.youtube.com/watch?v=nTq-OKy5kHs',
        # 'https://www.youtube.com/watch?v=ikaTTZEY5VE',
        # 'https://www.youtube.com/watch?v=lRtTS1PNFik',
        # 'https://www.youtube.com/watch?v=V-mbUZhovOo',
        # 'https://www.youtube.com/watch?v=WJNPGXivqew',
        # 'https://www.youtube.com/watch?v=HWnEifmgAdU',
        # 'https://www.youtube.com/watch?v=OVZPEUzXbqM',
        # 'https://www.youtube.com/watch?v=Zh4eqhcZjcg',
        # 'https://www.youtube.com/watch?v=CKncVaiv_08',
        # 'https://www.youtube.com/watch?v=jcE-Ue83P7U',
        # 'https://www.youtube.com/watch?v=4VztgBcVH5Q',
        'https://www.youtube.com/watch?v=7FhXh4yXUao',
        'https://www.youtube.com/watch?v=BryipFEiIiE',
        'https://www.youtube.com/watch?v=teW8gmpKQcI',
        'https://www.youtube.com/watch?v=TDZVCli3bEs',
        'https://www.youtube.com/watch?v=TtItFQTNMA4'
    ]

# File paths for your template images
plus_template = "plus_add_source.png" 
plus_template_2 = "plus_add_source_2.png"
youtube_template = "youtube_button.png"
text_field_template = "text_field.png"  # Use this if you have a distinct image for the text field
insert_template = "insert_button.png"

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
