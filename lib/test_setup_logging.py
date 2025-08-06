import logging
import os
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

from lib.setup_logging import setup_logging


class TestSetupLogging(unittest.TestCase):
    def setUp(self):
        """Set up test environment."""
        # Clear any existing handlers
        logger = logging.getLogger()
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
        # Create temporary directory for log files
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir.name)

    def tearDown(self):
        """Clean up test environment."""
        # Clear handlers again
        logger = logging.getLogger()
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)
        
        # Reset logger level
        logger.setLevel(logging.WARNING)
        
        # Return to original directory and cleanup
        os.chdir(self.original_cwd)
        self.temp_dir.cleanup()

    def test_setup_logging_creates_handlers(self):
        """Test that setup_logging creates the expected handlers."""
        setup_logging("test_app")
        
        logger = logging.getLogger()
        
        # Should have 2 handlers: stdout and file
        self.assertEqual(len(logger.handlers), 2)
        
        # Check handler types
        handler_types = [type(handler).__name__ for handler in logger.handlers]
        self.assertIn("StreamHandler", handler_types)
        self.assertIn("FileHandler", handler_types)

    def test_setup_logging_creates_log_file(self):
        """Test that setup_logging creates a log file."""
        app_name = "test_app"
        setup_logging(app_name)
        
        expected_log_file = f"{app_name}-debug.txt"
        self.assertTrue(os.path.exists(expected_log_file))

    def test_setup_logging_sets_logger_level(self):
        """Test that setup_logging sets the root logger level to DEBUG."""
        setup_logging("test_app")
        
        logger = logging.getLogger()
        self.assertEqual(logger.level, logging.DEBUG)

    def test_setup_logging_default_stdout_level(self):
        """Test that stdout handler has INFO level by default."""
        setup_logging("test_app")
        
        logger = logging.getLogger()
        stdout_handler = None
        
        for handler in logger.handlers:
            if isinstance(handler, logging.StreamHandler) and hasattr(handler, 'stream'):
                if handler.stream.name == '<stdout>':
                    stdout_handler = handler
                    break
        
        self.assertIsNotNone(stdout_handler)
        self.assertEqual(stdout_handler.level, logging.INFO)

    def test_setup_logging_custom_stdout_level(self):
        """Test that stdout handler level can be customized."""
        setup_logging("test_app", stdout_level=logging.WARNING)
        
        logger = logging.getLogger()
        stdout_handler = None
        
        for handler in logger.handlers:
            if isinstance(handler, logging.StreamHandler) and hasattr(handler, 'stream'):
                if handler.stream.name == '<stdout>':
                    stdout_handler = handler
                    break
        
        self.assertIsNotNone(stdout_handler)
        self.assertEqual(stdout_handler.level, logging.WARNING)

    def test_setup_logging_file_handler_level(self):
        """Test that file handler has DEBUG level."""
        setup_logging("test_app")
        
        logger = logging.getLogger()
        file_handler = None
        
        for handler in logger.handlers:
            if isinstance(handler, logging.FileHandler):
                file_handler = handler
                break
        
        self.assertIsNotNone(file_handler)
        self.assertEqual(file_handler.level, logging.DEBUG)

    def test_setup_logging_formatter(self):
        """Test that handlers have the expected formatter."""
        setup_logging("test_app")
        
        logger = logging.getLogger()
        expected_format = "%(asctime)s | %(process)d | %(levelname)s | %(name)s | %(message)s"
        
        for handler in logger.handlers:
            self.assertIsNotNone(handler.formatter)
            self.assertEqual(handler.formatter._fmt, expected_format)

    def test_setup_logging_sets_dateparser_level(self):
        """Test that dateparser logger level is set to INFO."""
        setup_logging("test_app")
        
        dateparser_logger = logging.getLogger("lib.dateparser.dateparser")
        self.assertEqual(dateparser_logger.level, logging.INFO)

    def test_setup_logging_writes_to_file(self):
        """Test that log messages are written to the file."""
        app_name = "test_app"
        setup_logging(app_name)
        
        # Log a test message
        test_logger = logging.getLogger("test")
        test_message = "This is a test debug message"
        test_logger.debug(test_message)
        
        # Check that the message was written to the file
        log_file_path = f"{app_name}-debug.txt"
        with open(log_file_path, 'r', encoding='utf-8') as f:
            log_content = f.read()
        
        self.assertIn(test_message, log_content)
        self.assertIn("DEBUG", log_content)
        self.assertIn("test", log_content)

    @patch('sys.stdout')
    def test_setup_logging_writes_to_stdout(self, mock_stdout):
        """Test that appropriate log messages are written to stdout."""
        setup_logging("test_app", stdout_level=logging.INFO)
        
        # Log an info message
        test_logger = logging.getLogger("test")
        test_message = "This is a test info message"
        test_logger.info(test_message)
        
        # Check that write was called on stdout
        mock_stdout.write.assert_called()


if __name__ == "__main__":
    unittest.main()
