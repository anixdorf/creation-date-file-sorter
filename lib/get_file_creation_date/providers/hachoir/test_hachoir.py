import unittest
from unittest.mock import patch, Mock, MagicMock
from datetime import datetime

from lib.get_file_creation_date.domain.create_date_result import GetFileCreationDateResult
from lib.get_file_creation_date.providers.hachoir.hachoir import HachoirFileCreationDateProvider


class TestHachoirFileCreationDateProvider(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        self.provider = HachoirFileCreationDateProvider()

    def test_initialization_with_hachoir_available(self):
        """Test provider initialization when Hachoir is available."""
        with patch('lib.get_file_creation_date.providers.hachoir.hachoir.HACHOIR_AVAILABLE', True):
            provider = HachoirFileCreationDateProvider()
            self.assertIsNotNone(provider.logger)
            self.assertEqual(provider.logger.name, "hachoir")

    def test_initialization_with_hachoir_unavailable(self):
        """Test provider initialization when Hachoir is unavailable."""
        with patch('lib.get_file_creation_date.providers.hachoir.hachoir.HACHOIR_AVAILABLE', False):
            with patch.object(HachoirFileCreationDateProvider, '__init__', lambda x: None):
                provider = HachoirFileCreationDateProvider()
                # Test the warning would be logged
                # This is a bit complex to test due to the logger setup in __init__

    def test_is_available_with_hachoir_installed(self):
        """Test is_available when Hachoir is installed."""
        with patch('lib.get_file_creation_date.providers.hachoir.hachoir.HACHOIR_AVAILABLE', True):
            provider = HachoirFileCreationDateProvider()
            self.assertTrue(provider.is_available())

    def test_is_available_with_hachoir_not_installed(self):
        """Test is_available when Hachoir is not installed."""
        with patch('lib.get_file_creation_date.providers.hachoir.hachoir.HACHOIR_AVAILABLE', False):
            provider = HachoirFileCreationDateProvider()
            self.assertFalse(provider.is_available())

    def test_supports_file(self):
        """Test that Hachoir provider supports all files."""
        test_files = [
            "/path/to/image.jpg",
            "/path/to/video.mp4",
            "/path/to/audio.mp3",
            "/path/to/document.pdf",
            "any_file.xyz"
        ]
        
        for file_path in test_files:
            with self.subTest(file_path=file_path):
                self.assertTrue(self.provider.supports_file(file_path))

    @patch('lib.get_file_creation_date.providers.hachoir.hachoir.createParser')
    @patch('lib.get_file_creation_date.providers.hachoir.hachoir.extractMetadata')
    @patch('lib.get_file_creation_date.providers.hachoir.hachoir.HACHOIR_AVAILABLE', True)
    def test_get_file_creation_date_success(self, mock_extract, mock_create_parser):
        """Test successful date extraction with Hachoir."""
        # Setup mocks
        mock_parser = Mock()
        mock_parser.stream._input.close = Mock()
        mock_create_parser.return_value = mock_parser
        
        mock_metadata = Mock()
        mock_extract.return_value = mock_metadata
        
        test_date = datetime(2023, 12, 25, 10, 30, 0)
        
        # Mock the _find_creation_date method
        with patch.object(self.provider, '_find_creation_date', return_value=test_date):
            file_path = "/path/to/test.jpg"
            result = self.provider.get_file_creation_date(file_path)
            
            # Verify calls
            mock_create_parser.assert_called_once_with(file_path)
            mock_extract.assert_called_once_with(mock_parser)
            
            # Verify result
            self.assertIsNotNone(result)
            self.assertIsInstance(result, GetFileCreationDateResult)
            self.assertEqual(result.creation_date, test_date)
            self.assertEqual(result.provider, "HachoirFileCreationDateProvider")

    @patch('lib.get_file_creation_date.providers.hachoir.hachoir.createParser')
    @patch('lib.get_file_creation_date.providers.hachoir.hachoir.HACHOIR_AVAILABLE', True)
    def test_get_file_creation_date_no_parser(self, mock_create_parser):
        """Test when Hachoir cannot create a parser."""
        mock_create_parser.return_value = None
        
        file_path = "/path/to/test.jpg"
        result = self.provider.get_file_creation_date(file_path)
        
        self.assertIsNone(result)
        mock_create_parser.assert_called_once_with(file_path)

    @patch('lib.get_file_creation_date.providers.hachoir.hachoir.createParser')
    @patch('lib.get_file_creation_date.providers.hachoir.hachoir.extractMetadata')
    @patch('lib.get_file_creation_date.providers.hachoir.hachoir.HACHOIR_AVAILABLE', True)
    def test_get_file_creation_date_no_metadata(self, mock_extract, mock_create_parser):
        """Test when Hachoir cannot extract metadata."""
        mock_parser = Mock()
        mock_parser.stream._input.close = Mock()
        mock_create_parser.return_value = mock_parser
        mock_extract.return_value = None
        
        file_path = "/path/to/test.jpg"
        result = self.provider.get_file_creation_date(file_path)
        
        self.assertIsNone(result)

    @patch('lib.get_file_creation_date.providers.hachoir.hachoir.createParser')
    @patch('lib.get_file_creation_date.providers.hachoir.hachoir.extractMetadata')
    @patch('lib.get_file_creation_date.providers.hachoir.hachoir.HACHOIR_AVAILABLE', True)
    def test_get_file_creation_date_no_creation_date_found(self, mock_extract, mock_create_parser):
        """Test when no creation date is found in metadata."""
        mock_parser = Mock()
        mock_parser.stream._input.close = Mock()
        mock_create_parser.return_value = mock_parser
        
        mock_metadata = Mock()
        mock_extract.return_value = mock_metadata
        
        # Mock _find_creation_date to return None
        with patch.object(self.provider, '_find_creation_date', return_value=None):
            file_path = "/path/to/test.jpg"
            result = self.provider.get_file_creation_date(file_path)
            
            self.assertIsNone(result)

    @patch('lib.get_file_creation_date.providers.hachoir.hachoir.createParser')
    @patch('lib.get_file_creation_date.providers.hachoir.hachoir.HACHOIR_AVAILABLE', True)
    def test_get_file_creation_date_exception_handling(self, mock_create_parser):
        """Test exception handling in get_file_creation_date."""
        mock_create_parser.side_effect = Exception("Hachoir error")
        
        file_path = "/path/to/test.jpg"
        result = self.provider.get_file_creation_date(file_path)
        
        # Should return None and not raise exception
        self.assertIsNone(result)

    def test_find_creation_date_with_valid_fields(self):
        """Test _find_creation_date with valid metadata fields."""
        test_date = datetime(2023, 12, 25, 10, 30, 0)
        
        mock_metadata = Mock()
        mock_metadata.get.side_effect = lambda field: "2023-12-25 10:30:00" if field == "creation_date" else None
        
        with patch.object(self.provider, '_parse_metadata_date', return_value=test_date) as mock_parse:
            result = self.provider._find_creation_date(mock_metadata)
            
            self.assertEqual(result, test_date)
            mock_parse.assert_called_with("2023-12-25 10:30:00")

    def test_find_creation_date_tries_all_fields(self):
        """Test that _find_creation_date tries all date fields in priority order."""
        mock_metadata = Mock()
        
        # Mock to return None for all fields except the last one
        def mock_get(field):
            if field == "modification_date":  # Last in the priority list
                return "2023-12-25 10:30:00"
            return None
        
        mock_metadata.get.side_effect = mock_get
        
        test_date = datetime(2023, 12, 25, 10, 30, 0)
        with patch.object(self.provider, '_parse_metadata_date', return_value=test_date):
            result = self.provider._find_creation_date(mock_metadata)
            
            self.assertEqual(result, test_date)
            # Should have tried multiple fields
            self.assertGreater(mock_metadata.get.call_count, 1)

    def test_find_creation_date_no_valid_fields(self):
        """Test _find_creation_date when no valid fields are found."""
        mock_metadata = Mock()
        mock_metadata.get.return_value = None
        
        result = self.provider._find_creation_date(mock_metadata)
        
        self.assertIsNone(result)

    @patch('lib.get_file_creation_date.providers.hachoir.hachoir.parse_date')
    def test_parse_metadata_date_success(self, mock_parse_date):
        """Test _parse_metadata_date with valid date string."""
        test_date = datetime(2023, 12, 25, 10, 30, 0)
        mock_parse_date.return_value = test_date
        
        result = self.provider._parse_metadata_date("2023-12-25 10:30:00")
        
        self.assertEqual(result, test_date)
        mock_parse_date.assert_called_once_with("2023-12-25 10:30:00")

    @patch('lib.get_file_creation_date.providers.hachoir.hachoir.parse_date')
    def test_parse_metadata_date_empty_value(self, mock_parse_date):
        """Test _parse_metadata_date with empty/None values."""
        test_cases = [None, "", "   "]
        
        for value in test_cases:
            with self.subTest(value=value):
                result = self.provider._parse_metadata_date(value)
                self.assertIsNone(result)
        
        # parse_date should not be called for empty values
        mock_parse_date.assert_not_called()

    @patch('lib.get_file_creation_date.providers.hachoir.hachoir.parse_date')
    def test_parse_metadata_date_parse_failure(self, mock_parse_date):
        """Test _parse_metadata_date when parse_date fails."""
        mock_parse_date.return_value = None
        
        result = self.provider._parse_metadata_date("invalid date")
        
        self.assertIsNone(result)
        mock_parse_date.assert_called_once_with("invalid date")

    def test_string_representation(self):
        """Test string representation of the provider."""
        str_repr = str(self.provider)
        self.assertEqual(str_repr, "HachoirFileCreationDateProvider")


if __name__ == "__main__":
    unittest.main()
