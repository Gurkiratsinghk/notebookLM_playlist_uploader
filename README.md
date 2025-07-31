# NotebookLM Playlist Uploader

This project automates the process of extracting YouTube video URLs from a playlist and processing them using Playwright and OpenCV.

## Features
- Extracts video titles and URLs from YouTube playlists.
- Downloads the data as a CSV file.
- Skips already processed URLs to avoid duplication.
- Logs processed URLs for future reference.
- Processes new URLs using OpenCV or other automation tools.

## Prerequisites
- Python 3.12 or higher
- Playwright
- OpenCV

## Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/Gurkiratsinghk/notebookLM_playlist_uploader.git
   cd notebookLM_playlist_uploader
   ```

2. Set up a virtual environment:
   ```bash
   python -m venv noteLM
   source noteLM/Scripts/activate  # On Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Install Playwright browsers:
   ```bash
   playwright install
   ```

## Usage
1. Run the script with the following command:
   ```bash
   python notebooklm/scripts/notebook_2.py --url "<YouTube Playlist URL>"
   ```

2. The script will process the playlist and display progress in the terminal.

## Folder Structure
```
notebookLM_playlist_uploader/
├── LICENSE
├── README.md
├── notebooklm/
│   ├── notebook.py
│   ├── notebook_2.py
│   ├── processed_links.log
│   └── ...
├── noteLM/
│   ├── Scripts/
│   ├── Lib/
│   └── ...
```

## Contributing
Contributions are welcome! Please fork the repository and submit a pull request.

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.
