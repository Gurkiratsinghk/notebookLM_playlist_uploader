# NotebookLM Playlist Uploader

This project automates the process of extracting YouTube video URLs from a playlist and uploading them to NotebookLM using Playwright and OpenCV.

## Features
- Extracts video titles and URLs from YouTube playlists.
- Downloads the data as a CSV file.
- Skips already processed URLs to avoid duplication.
- Logs processed URLs for future reference.
- Uploads YouTube URLs to NotebookLM using OCR and template matching.

## Things under work
- Launch NotebookLM automatically option does not work becasue google does not allow sign-in on chromium. (and I do not have a solution for this)
- Text based detection of 'Text field' does not work. Instead image detection is being used.


## Prerequisites
- Python 3.12 or higher
- Playwright
- OpenCV
- Tesseract OCR (install separately: https://github.com/tesseract-ocr/tesseract)

## Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/Gurkiratsinghk/notebookLM_playlist_uploader.git
   cd notebookLM_playlist_uploader

2. Set up a virtual environment:
   ```bash
   python -m venv noteLM
   source noteLM/Scripts/activate  # On Windows
3. Install dependencies:
   ```bash
   pip install -r requirements.txt

4. Install Playwright browsers:
   ```bash
   playwright install

5. Install Tesseract OCR:

On Windows: Download and install from https://github.com/UB-Mannheim/tesseract/wiki
On macOS/Linux: Install via package manager (e.g., `brew install tesseract` or `apt-get install tesseract-ocr`)

## Usage

1. Activate your virtual environment:
   ```bash
   source noteLM/Scripts/activate  # On Windows
   source noteLM/bin/activate      # On macOS/Linux
   ```

2. Run the script:
   ```bash
   # Option 1: Pass the YouTube playlist URL directly
   python main.py --url "https://www.youtube.com/playlist?list=YOUR_PLAYLIST_ID"

   # Option 2: Run interactively
   python main.py
   ```

3. The script will:
   - Open NotebookLM (if not already open)
   - Verify the NotebookLM interface is ready
   - Extract URLs from the YouTube playlist
   - Create a new notebook (if needed)
   - Upload each video URL to NotebookLM
   - Track progress and skip previously processed URLs

## Running Tests

1. Install test dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the test suite:
   ```bash
   python -m pytest tests/
   ```

3. For specific test files:
   ```bash
   python -m pytest tests/test_notebooklm.py
   python -m pytest tests/test_roi_button_click.py
   ```

## Project Structure

```
notebookLM_playlist_uploader/
├── notebooklm/                  # Main package directory
│   ├── core/                    # Core functionality
│   ├── utils/                   # Utility functions
│   │   ├── console.py          # Console output utilities
│   │   └── url.py              # URL validation utilities
│   ├── scripts/                 # Script modules
│   │   ├── notebook_2.py       # Main script logic
│   │   └── notebook_cv.py      # Computer vision functions
│   └── assets/                  # Image templates for CV
├── tests/                       # Test directory
│   └── debug_screenshots/       # Test artifacts
├── requirements.txt             # Project dependencies
├── setup.py                     # Package setup file
└── README.md                    # Project documentation
```

## Notes

1. **Browser Mode**:
   - Default: Headless mode for automated operation
   - Use `--show-browser` flag for visible browser (debugging)

2. **Error Handling**:
   - Failed URL uploads are logged in `logs/processed_links.log`
   - Screenshots of failures saved in `tests/debug_screenshots/`

3. **Template Images**:
   - Located in `notebooklm/assets/`
   - Update if NotebookLM interface changes

4. **Limitations**:
   - Requires stable internet connection
   - NotebookLM must be accessible
   - Screen resolution may affect template matching

5. **Troubleshooting**:
   - Check logs in `logs/processed_links.log`
   - Verify template images match your NotebookLM interface
   - Ensure Tesseract OCR is properly installed
   - Try running with visible browser for debugging



   