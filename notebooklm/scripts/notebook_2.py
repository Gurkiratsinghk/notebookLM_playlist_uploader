import os
import csv
import logging
import time
from typing import Set, List
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from .notebook_cv import notebook_cv  # Local import
import argparse
from ..utils.console import (
    print_error, print_info, print_progress,
    print_warning, print_header
)
from ..utils.url import validate_url, clean_url

# Configure logging with a more detailed format
LOG_FILE = os.path.join(os.path.dirname(__file__), "..", "logs", "processed_links.log")
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)

def load_processed_links() -> Set[str]:
    """
    Load previously processed YouTube URLs from the log file.
    
    Returns:
        Set[str]: A set of unique URLs that have already been processed
    """
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
    """
    Execute JavaScript on the page to collect YouTube video information.
    
    The script:
    1. Scrolls the page to load more videos
    2. Extracts video titles and URLs
    3. Creates and downloads a CSV file
    
    Args:
        page: Playwright page object
    """
    js_code = r'''
    // Scroll down for 5 seconds to load more videos
    let goToBottom = setInterval(() => window.scrollBy(0, 400), 1000);
    setTimeout(() => {
        clearInterval(goToBottom);
        let arrayVideos = [];
        const links = document.querySelectorAll('a#video-title');
        
        links.forEach(link => {
            // Remove playlist parameter from URL
            const cleanUrl = link.href.split('&list=')[0];
            if (cleanUrl) {
                arrayVideos.push(`${link.title};${cleanUrl}`);
            }
        });

        // Create and download CSV
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
    """
    Process the downloaded CSV file and extract new YouTube URLs.
    
    Args:
        csv_path (str): Path to the CSV file
        processed_links (Set[str]): Set of already processed URLs
    
    Returns:
        List[str]: List of new YouTube URLs to process
    """
    youtube_urls = []
    try:
        with open(csv_path, "r", encoding="utf-8") as csvfile:
            reader = csv.reader(csvfile, delimiter=';')
            for row in reader:
                if len(row) >= 2:
                    title, url = row[0].strip(), row[1].strip()
                    # Only add URLs that haven't been processed
                    if url and url not in processed_links:
                        youtube_urls.append(url)
                        processed_links.add(url)  # Add to set before logging
                        logging.info(f"New URL found: {url}")
    except Exception as e:
        logging.error(f"Error processing CSV file: {e}")
    return youtube_urls

def main() -> None:
    print_header("NotebookLM Playlist Uploader")
    
    parser = argparse.ArgumentParser(description="Upload YouTube playlist videos to NotebookLM")
    parser.add_argument("--url", type=str, help="YouTube Playlist URL (e.g., https://www.youtube.com/playlist?list=...)")
    args = parser.parse_args()

    # Get URL from argument or prompt
    ytPlaylist = args.url
    if not ytPlaylist:
        ytPlaylist = input("Enter YouTube Playlist URL: ")

    if not validate_url(ytPlaylist):
        print_error("Invalid YouTube playlist URL. URL must contain 'youtube.com' and 'playlist'")
        return

    processed_links = load_processed_links()
    youtube_urls = []

    try:
        print_progress("Initializing browser...")
        print_info(f"Processing playlist: {ytPlaylist}")
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(accept_downloads=True)
            page = context.new_page()

            # Navigate to YouTube playlist
            try:
                print_progress("Loading playlist...")
                page.goto(ytPlaylist, timeout=30000)
                page.wait_for_load_state("networkidle", timeout=30000)
                time.sleep(2)  # Allow dynamic content to load
                print_info("Playlist loaded successfully")
            except PlaywrightTimeout:
                print_error("Timeout while loading YouTube playlist")
                print_warning("Please check:")
                print(" - Your internet connection")
                print(" - The playlist URL is correct and accessible")
                print(" - The playlist is not private")
                return
            except Exception as e:
                print_error("Failed to load playlist")
                print_warning(f"Error details: {str(e)}")
                return

            # Extract video information
            try:
                run_js_to_download_csv(page)
                download = page.wait_for_event("download", timeout=30000)
                csv_path = os.path.join(os.getcwd(), "my_data.csv")
                download.save_as(csv_path)
                print_info(f"CSV downloaded successfully to: {csv_path}")

                # Process CSV after ensuring it's fully written
                time.sleep(2)
                youtube_urls = process_csv_file(csv_path, processed_links)
                if youtube_urls:
                    print_info(f"Found {len(youtube_urls)} new videos to process.")
                    notebook_cv(youtube_urls)
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