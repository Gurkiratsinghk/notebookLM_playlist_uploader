import unittest
from notebooklm.scripts.notebook_2 import load_processed_links, process_csv_file
import os

class TestNotebookLM(unittest.TestCase):

    def setUp(self):
        # Create a temporary log file for testing
        self.log_file = "test_processed_links.log"
        with open(self.log_file, "w", encoding="utf-8") as f:
            f.write("INFO - https://www.youtube.com/watch?v=Nkg1uIXZwko\n")

        # Create a temporary CSV file for testing
        self.csv_file = "test_my_data.csv"
        with open(self.csv_file, "w", encoding="utf-8") as f:
            f.write("Title1;https://www.youtube.com/watch?v=Nkg1uIXZwko\n")
            f.write("Title2;https://www.youtube.com/watch?v=Nkg1uIXZwko\n")

    def tearDown(self):
        # Remove temporary files after tests
        if os.path.exists(self.log_file):
            os.remove(self.log_file)
        if os.path.exists(self.csv_file):
            os.remove(self.csv_file)

    # Test the function that loads processed links from the log file
    def test_load_processed_links(self):
        processed_links = load_processed_links()
        self.assertIn("https://www.youtube.com/watch?v=Nkg1uIXZwko", processed_links)

    # Test the function that processes the CSV file and extracts new URLs
    def test_process_csv_file(self):
        processed_links = {"https://www.youtube.com/watch?v=Nkg1uIXZwko"}
        new_urls = process_csv_file(self.csv_file, processed_links)
        self.assertIn("https://www.youtube.com/watch?v=Nkg1uIXZwko", new_urls)
        self.assertNotIn("https://www.youtube.com/watch?v=Nkg1uIXZwko", new_urls)

if __name__ == "__main__":
    unittest.main()
