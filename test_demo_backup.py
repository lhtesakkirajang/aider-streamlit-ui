# --- Add these imports at the top of the file ---
import io
import queue
import threading
import time
import unittest

# Import the function you want to test from demo_backup.py.
from demo_backup import read_output

# --- Define a fake process class to simulate subprocess behavior ---
class FakeProcess:
    def __init__(self, output):
        # Use StringIO to simulate stdout stream.
        self.stdout = io.StringIO(output)
    def poll(self):
        # If current read pointer is at the end, simulate process finished.
        if self.stdout.tell() >= len(self.stdout.getvalue()):
            return 0
        return None

# --- Write the test cases ---
class TestDemoBackup(unittest.TestCase):
    def test_read_output_complete_lines(self):
        # Prepare dummy output with complete lines.
        dummy_output = "Line 1\nLine 2\n"
        fake_proc = FakeProcess(dummy_output)
        complete_log_queue = queue.Queue()
        partial_log_queue = queue.Queue()
        stop_event = threading.Event()

        # Run read_output in a background thread.
        reader_thread = threading.Thread(
            target=read_output,
            args=(fake_proc, complete_log_queue, partial_log_queue, stop_event)
        )
        reader_thread.start()
        # Wait for the thread to finish.
        reader_thread.join(timeout=2)

        # Extract all complete lines.
        complete_logs = []
        while not complete_log_queue.empty():
            complete_logs.append(complete_log_queue.get())
        
        # Assert that the complete lines are correctly added.
        self.assertIn("Line 1", complete_logs)
        self.assertIn("Line 2", complete_logs)
        # Also, final session ended message should be present.
        self.assertIn("🔚 Aider session ended.", complete_logs)

    def test_read_output_partial_line(self):
        # Provide an output that does not end with a newline.
        dummy_output = "Partial line without newline"
        fake_proc = FakeProcess(dummy_output)
        complete_log_queue = queue.Queue()
        partial_log_queue = queue.Queue()
        stop_event = threading.Event()

        reader_thread = threading.Thread(
            target=read_output,
            args=(fake_proc, complete_log_queue, partial_log_queue, stop_event)
        )
        reader_thread.start()
        reader_thread.join(timeout=2)

        # Since no newline is encountered, the complete log may not include the text.
        # Check that the partial log has the expected text.
        partial_logs = []
        while not partial_log_queue.empty():
            partial_logs.append(partial_log_queue.get())

        self.assertIn("Partial line without newline", partial_logs)
        # Also ensure the termination message is added.
        complete_logs = []
        while not complete_log_queue.empty():
            complete_logs.append(complete_log_queue.get())
        self.assertIn("🔚 Aider session ended.", complete_logs)

if __name__ == "__main__":
    unittest.main()
