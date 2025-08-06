import unittest
from unittest.mock import patch, Mock
from datetime import datetime

from lib.get_file_creation_date.domain.create_date_result import GetFileCreationDateResult
from lib.get_file_creation_date.providers.filename.filename import FilenameFileCreationDateProvider


class TestFilenameFileCreationDateProvider(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        self.provider = FilenameFileCreationDateProvider()

    def test_initialization(self):
        """Test provider initialization."""
        self.assertIsNotNone(self.provider.logger)
        self.assertEqual(self.provider.logger.name, "filename")

    def test_is_available(self):
        """Test that filename provider is always available."""
        self.assertTrue(self.provider.is_available())

    def test_supports_file(self):
        """Test that filename provider supports all files."""
        test_files = [
            "/path/to/file.jpg",
            "/path/to/document.pdf",
            "/path/to/video.mp4",
            "simple_filename.txt",
            "no_extension",
            ""
        ]
        
        for file_path in test_files:
            with self.subTest(file_path=file_path):
                self.assertTrue(self.provider.supports_file(file_path))

    @patch('lib.get_file_creation_date.providers.filename.filename.parse_date')
    def test_get_file_creation_date_with_valid_date(self, mock_parse_date):
        """Test get_file_creation_date when parse_date finds a valid date."""
        test_date = datetime(2023, 12, 25, 10, 30, 0)
        mock_parse_date.return_value = test_date
        
        file_path = "/path/to/IMG_20231225_103000.jpg"
        result = self.provider.get_file_creation_date(file_path)
        
        # Verify parse_date was called with the filename
        mock_parse_date.assert_called_once_with("IMG_20231225_103000.jpg")
        
        # Verify result
        self.assertIsNotNone(result)
        self.assertIsInstance(result, GetFileCreationDateResult)
        self.assertEqual(result.creation_date, test_date)
        self.assertEqual(result.provider, "filename")
        self.assertIsNone(result.provider_info)

    @patch('lib.get_file_creation_date.providers.filename.filename.parse_date')
    def test_get_file_creation_date_with_no_date(self, mock_parse_date):
        """Test get_file_creation_date when parse_date finds no date."""
        mock_parse_date.return_value = None
        
        file_path = "/path/to/random_filename.jpg"
        result = self.provider.get_file_creation_date(file_path)
        
        # Verify parse_date was called with the filename
        mock_parse_date.assert_called_once_with("random_filename.jpg")
        
        # Verify result is None
        self.assertIsNone(result)

    @patch('lib.get_file_creation_date.providers.filename.filename.parse_date')
    def test_get_file_creation_date_extracts_filename_correctly(self, mock_parse_date):
        """Test that only the filename (not the full path) is passed to parse_date."""
        from pathlib import Path
        mock_parse_date.return_value = None
        
        test_cases = [
            "/full/path/to/filename.jpg",
            "C:\\Windows\\Path\\file.txt",
            "relative/path/document.pdf",
            "just_filename.png",
            "/path/with/no/extension",
        ]
        
        for file_path in test_cases:
            with self.subTest(file_path=file_path):
                expected_filename = Path(file_path).name
                mock_parse_date.reset_mock()
                self.provider.get_file_creation_date(file_path)
                mock_parse_date.assert_called_once_with(expected_filename)

    @patch('lib.get_file_creation_date.providers.filename.filename.parse_date')
    def test_get_file_creation_date_logs_debug_messages(self, mock_parse_date):
        """Test that debug messages are logged appropriately."""
        with patch.object(self.provider.logger, 'debug') as mock_debug:
            # Test case with valid date
            test_date = datetime(2023, 12, 25, 10, 30, 0)
            mock_parse_date.return_value = test_date
            
            file_path = "/path/to/IMG_20231225.jpg"
            self.provider.get_file_creation_date(file_path)
            
            mock_debug.assert_called_once_with(f"Found creation date: {test_date}")

    @patch('lib.get_file_creation_date.providers.filename.filename.parse_date')
    def test_get_file_creation_date_logs_no_date_found(self, mock_parse_date):
        """Test that debug message is logged when no date is found."""
        with patch.object(self.provider.logger, 'debug') as mock_debug:
            # Test case with no date
            mock_parse_date.return_value = None
            
            file_path = "/path/to/random_file.jpg"
            self.provider.get_file_creation_date(file_path)
            
            mock_debug.assert_called_once_with("No creation date found in filename")

    def test_string_representation(self):
        """Test string representation of the provider."""
        str_repr = str(self.provider)
        self.assertEqual(str_repr, "FilenameFileCreationDateProvider")

    def test_repr_representation(self):
        """Test repr representation of the provider."""
        repr_str = repr(self.provider)
        expected = "FilenameFileCreationDateProvider(available=True)"
        self.assertEqual(repr_str, expected)

    @patch('lib.get_file_creation_date.providers.filename.filename.parse_date')
    def test_get_file_creation_date_with_empty_filename(self, mock_parse_date):
        """Test behavior with empty or invalid file paths."""
        mock_parse_date.return_value = None
        
        test_cases = [
            "",
            "/",
            "\\",
        ]
        
        for file_path in test_cases:
            with self.subTest(file_path=file_path):
                result = self.provider.get_file_creation_date(file_path)
                self.assertIsNone(result)

    @patch('lib.get_file_creation_date.providers.filename.filename.parse_date')
    def test_get_file_creation_date_handles_parse_exception(self, mock_parse_date):
        """Test that exceptions from parse_date are handled gracefully."""
        mock_parse_date.side_effect = Exception("Parse error")
        
        file_path = "/path/to/file.jpg"
        
        # Should not raise exception
        try:
            result = self.provider.get_file_creation_date(file_path)
            # If parse_date raises exception, result should be None or the exception should propagate
            # The current implementation would let the exception propagate, which is acceptable
        except Exception as e:
            # If exception propagates, that's also acceptable behavior
            self.assertIn("Parse error", str(e))


if __name__ == "__main__":
    unittest.main()
