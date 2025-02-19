from playwright.sync_api import sync_playwright

def add_youtube_source(page, url):
    # Wait for and click the '+ Add Source' button
    page.wait_for_selector("text='+ Add Source'", timeout=20000)
    page.click("text='+ Add Source'")
    
    # Wait for the pop-up that contains the 'Youtube' button and click it
    page.wait_for_selector("text='Youtube'", timeout=5000)
    page.click("text='Youtube'")
    
    # Wait for the next pop-up with the URL input field.
    # Adjust the selector if the input has a unique attribute or placeholder.
    page.wait_for_selector("input[type='text']", timeout=5000)
    
    # Fill in the URL into the text field
    page.fill("input[type='text']", url)
    
    # Wait for and click the 'Insert' button
    page.wait_for_selector("text='Insert'", timeout=10000)
    page.click("text='Insert'")
    
    # Optionally, wait for the pop-up to close or for the action to complete
    page.wait_for_timeout(1000)  # Wait 1 second

def run(playwright):
    user_data_dir = "./my_profile"
    # Custom arguments and user agent to reduce automation signals.
    args = [
        "--disable-blink-features=AutomationControlled",
        "--disable-infobars",
        # Set a common user agent string to mimic a real browser.
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/90.0.4430.93 Safari/537.36"
    ]
    
    # Launch a persistent context so you only sign in once.
    context = playwright.chromium.launch_persistent_context(
        user_data_dir,
        headless=False,
        args=args
    )
    page = context.new_page()
    
    # Directly navigate to Google's sign-in page
    page.goto("https://accounts.google.com/signin")
    
    # Allow time for you to sign in manually (if needed).
    # After a successful sign-in, the session data will be saved.
    page.wait_for_timeout(30000)  # Wait 30 seconds or adjust as needed.
    
    # After signing in manually, navigate to your target NotebookLM page.
    page.goto("https://notebooklm.google.com/notebook/c1a09f50-862c-4207-9dcd-7e2eba435fe8")
    page.wait_for_load_state("networkidle")
    
    # Array of YouTube URLs to add
    youtube_urls = [
        'https://www.youtube.com/watch?v=K5tUbZzcOEc',
        'https://www.youtube.com/watch?v=nG47fQ-aiHw',
        'https://www.youtube.com/watch?v=w6R6V1Mpz7s',
        'https://www.youtube.com/watch?v=So_UGo4dSJs',
        'https://www.youtube.com/watch?v=H8U0a9bwxqc',
        'https://www.youtube.com/watch?v=uL8C9wQrk3g',
        'https://www.youtube.com/watch?v=EFONLmsmVFw',
        'https://www.youtube.com/watch?v=Ih92AK1D-2M',
        'https://www.youtube.com/watch?v=AGj73UQN-K0',
        'https://www.youtube.com/watch?v=nTq-OKy5kHs',
        'https://www.youtube.com/watch?v=ikaTTZEY5VE',
        'https://www.youtube.com/watch?v=lRtTS1PNFik',
        'https://www.youtube.com/watch?v=V-mbUZhovOo',
        'https://www.youtube.com/watch?v=WJNPGXivqew',
        'https://www.youtube.com/watch?v=HWnEifmgAdU',
        'https://www.youtube.com/watch?v=OVZPEUzXbqM',
        'https://www.youtube.com/watch?v=Zh4eqhcZjcg',
        'https://www.youtube.com/watch?v=CKncVaiv_08',
        'https://www.youtube.com/watch?v=jcE-Ue83P7U',
        'https://www.youtube.com/watch?v=4VztgBcVH5Q',
        'https://www.youtube.com/watch?v=7FhXh4yXUao',
        'https://www.youtube.com/watch?v=BryipFEiIiE',
        'https://www.youtube.com/watch?v=teW8gmpKQcI',
        'https://www.youtube.com/watch?v=TDZVCli3bEs',
        'https://www.youtube.com/watch?v=TtItFQTNMA4'
    ]
    
    # Loop through each URL and add it as a source
    for url in youtube_urls:
        add_youtube_source(page, url)
    
    # Wait to observe the results before closing
    page.wait_for_timeout(5000)
    context.close()

with sync_playwright() as playwright:
    run(playwright)