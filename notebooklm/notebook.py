import os
import csv
import logging
import time
from playwright.sync_api import sync_playwright
from notebook_cv import notebook_cv

# Set up logging so that each processed URL is logged (one per line)
LOG_FILE = "processed_links.log"
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
)

def load_processed_links():
    """Load already-processed links from the log file into a set."""
    processed = set()
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            for line in f:
                processed.add(line.strip())
    return processed

def run_js_to_download_csv(page):
    """
    Inject your JavaScript code into the page.
    This code scrolls, gathers video data, creates a CSV blob, and clicks to download it.
    """
    js_code = r'''
    // Scroll down for 5 seconds to load more videos.
    let goToBottom = setInterval(() => window.scrollBy(0, 400), 1000);
    setTimeout(() => {
        clearInterval(goToBottom);
        let arrayVideos = [];
        console.log('\n'.repeat(50));
        const links = document.querySelectorAll('a');
        for (const link of links) {
            if (link.id === "video-title") {
                link.href = link.href.split('&list=')[0];
                arrayVideos.push(link.title + ';' + link.href);
                console.log(link.title + '\t' + link.href);
            }
        }
        let data = arrayVideos.join('\n');
        let blob = new Blob([data], {type: 'text/csv'});
        let elem = window.document.createElement('a');
        elem.href = window.URL.createObjectURL(blob);
        elem.download = 'my_data.csv';
        document.body.appendChild(elem);
        elem.click();
        document.body.removeChild(elem);
    }, 5000);
    '''
    page.evaluate(js_code)

def main():
    # Load already processed URLs from the log
    processed_links = load_processed_links()
    youtube_urls = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        # Enable downloads by setting accept_downloads=True in context options.
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()

        ytPlaylist = "https://www.youtube.com/playlist?list=PL9B24A6A9D5754E70"

        # Navigate to your target YouTube page or playlist.
        # Replace with the actual URL you want to scrape.
        page.goto(ytPlaylist)
        page.wait_for_load_state("networkidle")
        time.sleep(2)  # Ensure the page is fully ready

        # Run the JavaScript to scroll & scrape videos.
        run_js_to_download_csv(page)

        # Wait for the CSV download to start.
        try:
            download = page.wait_for_event("download", timeout=30000)  # wait up to 30 sec
        except Exception as e:
            print("Download did not start:", e)
            context.close()
            browser.close()
            return

        # Save the downloaded CSV to a known file name.
        csv_path = os.path.join(os.getcwd(), "my_data.csv")
        download.save_as(csv_path)
        print("CSV downloaded and saved to:", csv_path)

        # Wait a bit to ensure the file is fully written.
        time.sleep(2)

        # Read the CSV file and build your array of YouTube URLs,
        # skipping any URL that has already been processed.
        with open(csv_path, "r", encoding="utf-8") as csvfile:
            reader = csv.reader(csvfile, delimiter=';')
            for row in reader:
                if len(row) >= 2:
                    title, url = row[0].strip(), row[1].strip()
                    if url and url not in processed_links:
                        youtube_urls.append(url)
                        # Log the new URL so that we don't process it next time.
                        logging.info(url)
                    else:
                        print("Skipping already processed URL:", url)
        print("New YouTube URLs found:", youtube_urls)

        # At this point, you can call your automation (e.g., with OpenCV/pyautogui)
        # to process each new URL. For demonstration, we just print them.
        #
        # Example:
        # for url in youtube_urls:
        #     add_youtube_source(url)
        #
        # (Assuming add_youtube_source() is your automation function.)

        notebook_cv(youtube_urls)

        # Cleanup
        context.close()
        browser.close()

if __name__ == "__main__":
    main()
