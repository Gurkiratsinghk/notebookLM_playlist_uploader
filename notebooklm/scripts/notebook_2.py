# import os
# import csv
# import logging
# import time
# from typing import Set, List
# from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
# import pyautogui
# from .notebook_cv import notebook_cv, find_image_on_screen  # Local import
# import argparse
# from ..utils.console import (
#     print_error, print_info, print_progress,
#     print_warning, print_header
# )
# from ..utils.url import validate_url, clean_url
# from tqdm import tqdm

# # Configure logging with a more detailed format
# LOG_FILE = os.path.join(os.path.dirname(__file__), "..", "logs", "processed_links.log")
# os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

# logging.basicConfig(
#     filename=LOG_FILE,
#     level=logging.INFO,
#     format='%(asctime)s - %(levelname)s - %(message)s',
# )

# def load_processed_links() -> Set[str]:
#     """
#     Load previously processed YouTube URLs from the log file.
    
#     Returns:
#         Set[str]: A set of unique URLs that have already been processed
#     """
#     processed = set()
#     try:
#         if os.path.exists(LOG_FILE):
#             with open(LOG_FILE, "r", encoding="utf-8") as f:
#                 processed = {line.split(' - ')[-1].strip() for line in f if ' - ' in line}
#         return processed
#     except Exception as e:
#         logging.error(f"Error loading processed links: {e}")
#         return set()

# def run_js_to_download_csv(page) -> None:
#     """
#     Execute JavaScript on the page to collect YouTube video information.
    
#     The script:
#     1. Scrolls the page to load more videos
#     2. Extracts video titles and URLs
#     3. Creates and downloads a CSV file
    
#     Args:
#         page: Playwright page object
#     """
#     js_code = r'''
#     // Scroll down for 5 seconds to load more videos
#     let goToBottom = setInterval(() => window.scrollBy(0, 400), 1000);
#     setTimeout(() => {
#         clearInterval(goToBottom);
#         let arrayVideos = [];
#         const links = document.querySelectorAll('a#video-title');
        
#         links.forEach(link => {
#             // Remove playlist parameter from URL
#             const cleanUrl = link.href.split('&list=')[0];
#             if (cleanUrl) {
#                 arrayVideos.push(`${link.title};${cleanUrl}`);
#             }
#         });

#         // Create and download CSV
#         const csvContent = arrayVideos.join('\n');
#         const blob = new Blob([csvContent], {type: 'text/csv'});
#         const elem = window.document.createElement('a');
#         elem.href = window.URL.createObjectURL(blob);
#         elem.download = 'my_data.csv';
#         document.body.appendChild(elem);
#         elem.click();
#         document.body.removeChild(elem);
#     }, 5000);
#     '''
#     page.evaluate(js_code)

# def process_csv_file(csv_path: str, processed_links: Set[str]) -> List[str]:
#     """
#     Process the downloaded CSV file and extract new YouTube URLs.
    
#     Args:
#         csv_path (str): Path to the CSV file
#         processed_links (Set[str]): Set of already processed URLs
    
#     Returns:
#         List[str]: List of new YouTube URLs to process
#     """
#     youtube_urls = []
#     try:
#         with open(csv_path, "r", encoding="utf-8") as csvfile:
#             reader = csv.reader(csvfile, delimiter=";")
#             for row in reader:
#                 if len(row) >= 2:
#                     title, url = row[0].strip(), row[1].strip()
#                     # Only add URLs that haven't been processed
#                     if url and url not in processed_links:
#                         youtube_urls.append(url)
#                         processed_links.add(url)  # Add to set before logging
#                         logging.info(f"New URL found: {url}")
#     except Exception as e:
#         logging.error(f"Error processing CSV file: {e}")
#     return youtube_urls

# def check_notebooklm_homepage() -> bool:
#     """
#     Check if the NotebookLM homepage matches the expected layout.
    
#     Returns:
#         bool: True if all expected elements are found, False otherwise
#     """
#     print_progress("Checking NotebookLM homepage consistency...")
    
#     # Check for "create_new_notebook"
#     coords = find_image_on_screen("assets/create_new_notebook.png")
#     if not coords:
#         print_error("Could not find 'create_new_notebook' button")
#         return False
#     print_info("Found 'create_new_notebook' button")
#     pyautogui.click(coords)
#     time.sleep(2)
    
#     # Check for "add_sources"
#     add_sources_coords = find_image_on_screen("assets/add_source_button.png")
#     if not add_sources_coords:
#         print_error("Could not find 'add_sources' button")
#         return False
#     print_info("Found 'add_sources' button")
    
#     # Check for "youtube_button"
#     youtube_coords = find_image_on_screen("assets/youtube_button.png")
#     if not youtube_coords:
#         print_error("Could not find 'youtube_button'")
#         return False
#     print_info("Found 'youtube_button'")
    
#     return True

# def main() -> None:
#     print_header("NotebookLM Playlist Uploader")
    
#     # Prompt user to open or launch NotebookLM
#     print("Please choose an option:")
#     print("1. Open NotebookLM manually")
#     print("2. Launch NotebookLM automatically")
#     choice = input("Enter your choice (1 or 2): ")
    
#     if choice == "1":
#         print_info("Please open NotebookLM manually.")
#         input("Press Enter when NotebookLM is open...")
#         # Get the directory of the current script
#         script_dir = os.path.dirname(__file__)

#         # Define the assets directory (assuming assets are in notebooklm/assets/)
#         assets_dir = os.path.join(script_dir, "..", "assets")
#         assets_dir = os.path.normpath(assets_dir)

#         # Construct full paths for each template
#         create_new_notebook_path = os.path.join(assets_dir, "create_new_notebook.png")
#         add_source_path = os.path.join(assets_dir, "add_source_button.png")
#         add_source_alt_path = os.path.join(assets_dir, "add_source_button_alt.png")

#         # Optional: Check if the files exist to catch path errors early
#         for path in [create_new_notebook_path, add_source_path, add_source_alt_path]:
#             if not os.path.exists(path):
#                 print(f"Error: File not found at {path}")
#         if ( find_image_on_screen([create_new_notebook_path]) or  find_image_on_screen([add_source_path]) or  find_image_on_screen([add_source_alt_path])):
#             print_error("NotebookLM not detected on screen.")
#             return
#     elif choice == "2":
#         print_progress("Launching NotebookLM...")
#         with sync_playwright() as p:
#             browser = p.chromium.launch(headless=False)
#             page = browser.new_page()
#             page.goto("https://notebooklm.google.com")  # Replace with actual URL if different
#             with tqdm(total=100, desc="Loading NotebookLM", bar_format="{l_bar}{bar}| {elapsed}") as pbar:
#                 page.wait_for_load_state("networkidle")
#                 for _ in range(10):  # Simulate loading progress
#                     time.sleep(0.3)
#                     pbar.update(10)
#             coords = find_image_on_screen("assets/create_new_notebook.png")
#             if not coords:
#                 print_error("Could not find 'create_new_notebook' after launch")
#                 browser.close()
#                 return
#             print_info("Found 'create_new_notebook' button")
#             time.sleep(3)
#             youtube_coords = find_image_on_screen("assets/youtube_button.png")
#             if not youtube_coords:
#                 print_error("Could not find 'youtube_button' after launch")
#                 browser.close()
#                 return
#             print_info("NotebookLM launched and verified")
#             browser.close()
#     else:
#         print_error("Invalid choice")
#         return
    
#     # Verify NotebookLM homepage consistency
#     if not check_notebooklm_homepage():
#         print_error("NotebookLM homepage does not match expected layout.")
#         print_warning("Please update the asset images in the 'assets' folder to match the current UI.")
#         return
    
#     parser = argparse.ArgumentParser(description="Upload YouTube playlist videos to NotebookLM")
#     parser.add_argument("--url", type=str, help="YouTube Playlist URL (e.g., https://www.youtube.com/playlist?list=...)")
#     args = parser.parse_args()

#     # Get URL from argument or prompt
#     ytPlaylist = args.url
#     if not ytPlaylist:
#         ytPlaylist = input("Enter YouTube Playlist URL: ")

#     if not validate_url(ytPlaylist):
#         print_error("Invalid YouTube playlist URL. URL must contain 'youtube.com' and 'playlist'")
#         return

#     processed_links = load_processed_links()
#     youtube_urls = []

#     try:
#         print_progress("Initializing browser for playlist processing...")
#         with sync_playwright() as p:
#             browser = p.chromium.launch(headless=True)
#             context = browser.new_context(accept_downloads=True)
#             page = context.new_page()

#             # Navigate to YouTube playlist with loading bar
#             try:
#                 print_info(f"Processing playlist: {ytPlaylist}")
#                 with tqdm(total=100, desc="Loading Playlist", bar_format="{l_bar}{bar}| {elapsed}") as pbar:
#                     page.goto(ytPlaylist, timeout=30000)
#                     page.wait_for_load_state("networkidle", timeout=30000)
#                     time.sleep(2)  # Allow dynamic content to load
#                     pbar.update(100)
#                 print_info("Playlist loaded successfully")
#             except PlaywrightTimeout:
#                 print_error("Timeout while loading YouTube playlist")
#                 print_warning("Please check your internet connection, the playlist URL, and ensure it's not private.")
#                 return
#             except Exception as e:
#                 print_error("Failed to load playlist")
#                 print_warning(f"Error details: {str(e)}")
#                 return

#             # Extract video information with loading bar
#             try:
#                 run_js_to_download_csv(page)
#                 with tqdm(total=100, desc="Downloading CSV", bar_format="{l_bar}{bar}| {elapsed}") as pbar:
#                     download = page.wait_for_event("download", timeout=30000)
#                     csv_path = os.path.join(os.getcwd(), "my_data.csv")
#                     download.save_as(csv_path)
#                     pbar.update(100)
#                 print_info(f"CSV downloaded successfully to: {csv_path}")

#                 # Process CSV after ensuring it's fully written
#                 time.sleep(2)
#                 youtube_urls = process_csv_file(csv_path, processed_links)
#                 if youtube_urls:
#                     print_info(f"Found {len(youtube_urls)} new videos to process.")
#                     with tqdm(youtube_urls, desc="Uploading Videos") as pbar:
#                         for url in pbar:
#                             notebook_cv([url])
#                 else:
#                     print_info("No new videos to process.")
#             except PlaywrightTimeout:
#                 print_error("Timeout while waiting for CSV download.")
#             except Exception as e:
#                 print_error(f"Error during CSV processing: {e}")
#             finally:
#                 context.close()
#                 browser.close()

#     except Exception as e:
#         print_error(f"Unexpected error: {e}")

# if __name__ == "__main__":
#     main()




import os
import csv
import logging
import time
from typing import Set, List
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
import pyautogui
from .notebook_cv import notebook_cv, find_image_on_screen, find_text_on_screen  # Local import
import argparse
from ..utils.console import (
    print_error, print_info, print_progress,
    print_warning, print_header
)
from ..utils.url import validate_url, clean_url
from tqdm import tqdm

# Configure logging
LOG_FILE = os.path.join(os.path.dirname(__file__), "..", "logs", "processed_links.log")
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)

def load_processed_links() -> Set[str]:
    processed = set()
    try:
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                processed = {line.split(' - ')[-1].strip() for line in f if ' - ' in line}
        return processed
    except Exception as e:
        logging.error(f"Error loading processed links: {e}")
        return set()

def run_js_to_download_csv(page) -> None:
    js_code = r'''
    let goToBottom = setInterval(() => window.scrollBy(0, 400), 1000);
    setTimeout(() => {
        clearInterval(goToBottom);
        let arrayVideos = [];
        const links = document.querySelectorAll('a#video-title');
        links.forEach(link => {
            const cleanUrl = link.href.split('&list=')[0];
            if (cleanUrl) {
                arrayVideos.push(`${link.title};${cleanUrl}`);
            }
        });
        const csvContent = arrayVideos.join('\n');
        const blob = new Blob([csvContent], {type: 'text/csv'});
        const elem = window.document.createElement('a');
        elem.href = window.URL.createObjectURL(blob);
        elem.download = 'my_data.csv';
        document.body.appendChild(elem);
        elem.click();
        document.body.removeChild(elem);
    }, 5000);
    '''
    page.evaluate(js_code)

def process_csv_file(csv_path: str, processed_links: Set[str]) -> List[str]:
    youtube_urls = []
    try:
        with open(csv_path, "r", encoding="utf-8") as csvfile:
            reader = csv.reader(csvfile, delimiter=';')
            for row in reader:
                if len(row) >= 2:
                    title, url = row[0].strip(), row[1].strip()
                    if url and url not in processed_links:
                        youtube_urls.append(url)
                        processed_links.add(url)
                        logging.info(f"New URL found: {url}")
    except Exception as e:
        logging.error(f"Error processing CSV file: {e}")
    return youtube_urls

def check_notebooklm_homepage() -> bool:
    print_progress("Checking NotebookLM homepage consistency...")
    script_dir = os.path.dirname(__file__)
    assets_dir = os.path.normpath(os.path.join(script_dir, "..", "assets"))
    set_create_new_notebook_button = False
    set_add_source_button = False
    set_youtube_button = False
    
    # Define template paths
    create_new_notebook_path = os.path.join(assets_dir, "create_new_notebook.png")
    add_source_path = os.path.join(assets_dir, "add_source_button.png")
    add_source_alt_path = os.path.join(assets_dir, "add_source_button_alt.png")
    youtube_path = os.path.join(assets_dir, "youtube_button.png")
    
    # Check if files exist
    for path in [create_new_notebook_path, add_source_path, add_source_alt_path, youtube_path]:
        if not os.path.exists(path):
            print_error(f"Template file missing: {path}")
            return False
    
    # Check for "Create New Notebook" (try OCR first, then template)
    coords = find_text_on_screen("Create New Notebook", roi=(0, 0, 800, 200), confidence=0.8)
    if not coords:
        coords = find_image_on_screen([create_new_notebook_path], confidence=0.8, roi=(0, 0, 800, 200))
    if not coords:
        print_warning("Could not find 'Create New Notebook' button or text")
        set_create_new_notebook_button = False
    else:
        set_create_new_notebook_button = True
        print_info("Found 'Create New Notebook'")
        pyautogui.moveTo(coords[0], coords[1], duration=0.5)
        pyautogui.click()
        time.sleep(2)
    
    # Check for "+ Add" (either variant)
    coords = find_text_on_screen("Add", confidence=0.6)
    if not coords:
        coords = find_image_on_screen([add_source_path, add_source_alt_path], confidence=0.8, roi=(0, 0, 800, 400))
    if not coords:
        print_warning("Could not find '+ Add' button")
        set_add_source_button = False
    else:
        set_add_source_button = True
        print_info("Found '+ Add'")
    
    # Check for "YouTube" button
    coords = find_text_on_screen("YouTube", confidence=0.6)
    if not coords:
        coords = find_image_on_screen([youtube_path], confidence=0.8, roi=(0, 0, 800, 600))
    if not coords:
        print_warning("Could not find 'YouTube' button")
        set_youtube_button = False
    else:        
        set_youtube_button = True
        print_info("Found 'YouTube' button")
    
    if set_create_new_notebook_button or set_add_source_button or set_youtube_button:
        return True
    else:
        return False
    

def main() -> None:
    print_header("NotebookLM Playlist Uploader")
    
    # Prompt user to open or launch NotebookLM
    print("Please choose an option:")
    print("1. Open NotebookLM manually")
    print("2. Launch NotebookLM automatically")
    choice = input("Enter your choice (1 or 2): ")
    
    script_dir = os.path.dirname(__file__)
    assets_dir = os.path.normpath(os.path.join(script_dir, "..", "assets"))
    create_new_notebook_path = os.path.join(assets_dir, "create_new_notebook.png")
    youtube_path = os.path.join(assets_dir, "youtube_button.png")
    add_source_path = os.path.join(assets_dir, "add_source_button.png")
    add_source_alt_path = os.path.join(assets_dir, "add_source_button_alt.png")
    
    if choice == "1":
        print_info("Please open NotebookLM manually.")
        input("Press Enter when NotebookLM is open...")
        coords = find_text_on_screen("Create New Notebook", confidence=0.6)
        if coords:
            coords = find_image_on_screen([create_new_notebook_path], confidence=0.6)
        if coords:
            print_warning("Create New Notebook not found... Looking for '+ Add' button.")
            coords = find_text_on_screen("Add", confidence=0.6)
        if coords:
            coords = find_image_on_screen([add_source_path, add_source_alt_path], confidence=0.6)
        if coords:
            print_error("NotebookLM not detected on screen (Create New Notebook or Add not found).")
            return
        print_info("NotebookLM detected")
    elif choice == "2":
        print_progress("Launching NotebookLM...")
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto("https://notebooklm.google.com")
            with tqdm(total=100, desc="Loading NotebookLM", bar_format="{l_bar}{bar}| {elapsed}") as pbar:
                page.wait_for_load_state("networkidle")
                for _ in range(10):
                    time.sleep(0.3)
                    pbar.update(10)
            coords = find_text_on_screen("Create New Notebook", roi=(0, 0, 800, 200), confidence=0.8)
            if not coords:
                coords = find_image_on_screen([create_new_notebook_path], confidence=0.8, roi=(0, 0, 800, 200))
            if not coords:
                print_error("Could not find 'Create New Notebook' after launch")
                browser.close()
                return
            print_info("Found 'Create New Notebook'")
            time.sleep(3)
            coords = find_image_on_screen([youtube_path], confidence=0.8, roi=(0, 0, 800, 600))
            if not coords:
                print_error("Could not find 'YouTube' button after launch")
                browser.close()
                return
            print_info("NotebookLM launched and verified")
            browser.close()
    else:
        print_error("Invalid choice")
        return
    
    if not check_notebooklm_homepage():
        print_error("NotebookLM homepage does not match expected layout.")
        print_warning("Please update the template images in the 'assets' folder to match the current UI.")
        return
    
    parser = argparse.ArgumentParser(description="Upload YouTube playlist videos to NotebookLM")
    parser.add_argument("--url", type=str, help="YouTube Playlist URL (e.g., https://www.youtube.com/playlist?list=...)")
    args = parser.parse_args()

    ytPlaylist = args.url
    if not ytPlaylist:
        ytPlaylist = input("Enter YouTube Playlist URL: ")

    if not validate_url(ytPlaylist):
        print_error("Invalid YouTube playlist URL. URL must contain 'youtube.com' and 'playlist'")
        return

    processed_links = load_processed_links()
    youtube_urls = []

    try:
        print_progress("Initializing browser for playlist processing...")
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(accept_downloads=True)
            page = context.new_page()

            try:
                print_info(f"Processing playlist: {ytPlaylist}")
                with tqdm(total=100, desc="Loading Playlist", bar_format="{l_bar}{bar}| {elapsed}") as pbar:
                    page.goto(ytPlaylist, timeout=30000)
                    page.wait_for_load_state("networkidle", timeout=30000)
                    time.sleep(2)
                    pbar.update(100)
                print_info("Playlist loaded successfully")
            except PlaywrightTimeout:
                print_error("Timeout while loading YouTube playlist")
                print_warning("Please check your internet connection, the playlist URL, and ensure it's not private.")
                return
            except Exception as e:
                print_error("Failed to load playlist")
                print_warning(f"Error details: {str(e)}")
                return

            try:
                run_js_to_download_csv(page)
                with tqdm(total=100, desc="Downloading CSV", bar_format="{l_bar}{bar}| {elapsed}") as pbar:
                    download = page.wait_for_event("download", timeout=30000)
                    csv_path = os.path.join(os.getcwd(), "my_data.csv")
                    download.save_as(csv_path)
                    pbar.update(100)
                print_info(f"CSV downloaded successfully to: {csv_path}")

                time.sleep(2)
                youtube_urls = process_csv_file(csv_path, processed_links)
                if youtube_urls:
                    print_info(f"Found {len(youtube_urls)} new videos to process.")
                    with tqdm(youtube_urls, desc="Uploading Videos") as pbar:
                        for url in pbar: # Iterate through the URLs
                            notebook_cv([url])
                else:
                    print_info("No new videos to process.")
            except PlaywrightTimeout:
                print_error("Timeout while waiting for CSV download.")
            except Exception as e:
                print_error(f"Error during CSV processing: {e}")
            finally:
                context.close()
                browser.close()

    except Exception as e:
        print_error(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()