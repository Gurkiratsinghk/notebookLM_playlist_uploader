import unittest
import os
import tempfile
from notebooklm.scripts.notebook_2 import load_processed_links, process_csv_file

class TestNotebookLM(unittest.TestCase):
    def setUp(self):
        # Create temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        
        # Set up log file path
        self.log_file = os.path.join(self.test_dir, "processed_links.log")
        with open(self.log_file, "w", encoding="utf-8") as f:
            f.write("2025-07-31 12:00:00,000 - INFO - New URL found: https://www.youtube.com/watch?v=Nkg1uIXZwko\n")

        # Set up CSV file path
        self.csv_file = os.path.join(self.test_dir, "test_my_data.csv")
        with open(self.csv_file, "w", encoding="utf-8") as f:
            f.write("Test Video;https://www.youtube.com/watch?v=Nkg1uIXZwko\n")
            f.write("Another Video;https://www.youtube.com/watch?v=different123\n")

    def tearDown(self):
        # Remove temporary files after tests
        if os.path.exists(self.log_file):
            os.remove(self.log_file)
        if os.path.exists(self.csv_file):
            os.remove(self.csv_file)

    def test_load_processed_links(self):
        # Override LOG_FILE path for testing
        import notebooklm.scripts.notebook_2 as notebook2
        original_log_file = notebook2.LOG_FILE
        notebook2.LOG_FILE = self.log_file
        
        try:
            processed_links = load_processed_links()
            self.assertIn("https://www.youtube.com/watch?v=Nkg1uIXZwko", processed_links)
        finally:
            # Restore original LOG_FILE path
            notebook2.LOG_FILE = original_log_file

    def test_process_csv_file(self):
        # Start with empty set of processed links
        processed_links = set()
        new_urls = process_csv_file(self.csv_file, processed_links)
        
        # Both URLs should be in new_urls since none were in processed_links
        self.assertIn("https://www.youtube.com/watch?v=Nkg1uIXZwko", new_urls)
        self.assertIn("https://www.youtube.com/watch?v=different123", new_urls)
        self.assertEqual(len(new_urls), 2)

if __name__ == "__main__":
    unittest.main()
