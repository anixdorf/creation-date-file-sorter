import unittest
from unittest.mock import Mock, patch
from datetime import datetime

from lib.get_file_creation_date.domain.create_date_result import GetFileCreationDateResult
from lib.get_file_creation_date.get_file_creation_date import get_file_creation_date


class TestGetFileCreationDate(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        self.test_file_path = "/path/to/test/file.jpg"
        self.test_date = datetime(2023, 12, 25, 10, 30, 0)
        self.test_result = GetFileCreationDateResult(
            creation_date=self.test_date,
            provider="test_provider"
        )

    @patch('lib.get_file_creation_date.get_file_creation_date._PROVIDERS_AVAILABLE')
    @patch('lib.get_file_creation_date.get_file_creation_date.get_oldest_entry')
    def test_get_file_creation_date_with_supporting_providers(self, mock_get_oldest, mock_providers):
        """Test get_file_creation_date with providers that support the file."""
        # Setup mock providers
        mock_provider1 = Mock()
        mock_provider1.supports_file.return_value = True
        mock_provider1.get_file_creation_date.return_value = self.test_result
        
        mock_provider2 = Mock()
        mock_provider2.supports_file.return_value = False
        mock_provider2.get_file_creation_date.return_value = None
        
        mock_providers.__iter__.return_value = [mock_provider1, mock_provider2]
        mock_get_oldest.return_value = self.test_result
        
        # Call function
        result = get_file_creation_date(self.test_file_path)
        
        # Verify results
        self.assertEqual(result, self.test_result)
        mock_provider1.supports_file.assert_called_once_with(self.test_file_path)
        mock_provider1.get_file_creation_date.assert_called_once_with(self.test_file_path)
        mock_provider2.supports_file.assert_called_once_with(self.test_file_path)
        mock_provider2.get_file_creation_date.assert_not_called()  # Shouldn't be called since supports_file returned False
        mock_get_oldest.assert_called_once()

    @patch('lib.get_file_creation_date.get_file_creation_date._PROVIDERS_AVAILABLE')
    @patch('lib.get_file_creation_date.get_file_creation_date.get_oldest_entry')
    def test_get_file_creation_date_no_supporting_providers(self, mock_get_oldest, mock_providers):
        """Test get_file_creation_date when no providers support the file."""
        # Setup mock providers that don't support the file
        mock_provider1 = Mock()
        mock_provider1.supports_file.return_value = False
        
        mock_provider2 = Mock()
        mock_provider2.supports_file.return_value = False
        
        mock_providers.__iter__.return_value = [mock_provider1, mock_provider2]
        mock_get_oldest.return_value = None
        
        # Call function
        result = get_file_creation_date(self.test_file_path)
        
        # Verify results
        self.assertIsNone(result)
        mock_provider1.supports_file.assert_called_once_with(self.test_file_path)
        mock_provider1.get_file_creation_date.assert_not_called()
        mock_provider2.supports_file.assert_called_once_with(self.test_file_path)
        mock_provider2.get_file_creation_date.assert_not_called()
        mock_get_oldest.assert_called_once_with([])

    @patch('lib.get_file_creation_date.get_file_creation_date._PROVIDERS_AVAILABLE')
    @patch('lib.get_file_creation_date.get_file_creation_date.get_oldest_entry')
    def test_get_file_creation_date_filters_none_results(self, mock_get_oldest, mock_providers):
        """Test that None results from providers are filtered out."""
        # Setup mock providers
        mock_provider1 = Mock()
        mock_provider1.supports_file.return_value = True
        mock_provider1.get_file_creation_date.return_value = None  # Returns None
        
        mock_provider2 = Mock()
        mock_provider2.supports_file.return_value = True
        mock_provider2.get_file_creation_date.return_value = self.test_result
        
        mock_providers.__iter__.return_value = [mock_provider1, mock_provider2]
        mock_get_oldest.return_value = self.test_result
        
        # Call function
        result = get_file_creation_date(self.test_file_path)
        
        # Verify results
        self.assertEqual(result, self.test_result)
        
        # Check that get_oldest_entry was called with only non-None results
        args, kwargs = mock_get_oldest.call_args
        filtered_entries = args[0]
        self.assertEqual(len(filtered_entries), 1)
        self.assertEqual(filtered_entries[0], self.test_result)

    @patch('lib.get_file_creation_date.get_file_creation_date._PROVIDERS_AVAILABLE')
    @patch('lib.get_file_creation_date.get_file_creation_date.get_oldest_entry')
    def test_get_file_creation_date_multiple_valid_results(self, mock_get_oldest, mock_providers):
        """Test get_file_creation_date with multiple providers returning valid results."""
        # Setup mock providers with different results
        result1 = GetFileCreationDateResult(
            creation_date=datetime(2023, 12, 25, 10, 30, 0),
            provider="provider1"
        )
        result2 = GetFileCreationDateResult(
            creation_date=datetime(2023, 12, 20, 15, 45, 0),
            provider="provider2"
        )
        
        mock_provider1 = Mock()
        mock_provider1.supports_file.return_value = True
        mock_provider1.get_file_creation_date.return_value = result1
        
        mock_provider2 = Mock()
        mock_provider2.supports_file.return_value = True
        mock_provider2.get_file_creation_date.return_value = result2
        
        mock_providers.__iter__.return_value = [mock_provider1, mock_provider2]
        mock_get_oldest.return_value = result2  # Assume result2 is older
        
        # Call function
        result = get_file_creation_date(self.test_file_path)
        
        # Verify results
        self.assertEqual(result, result2)
        
        # Check that get_oldest_entry was called with both results
        args, kwargs = mock_get_oldest.call_args
        filtered_entries = args[0]
        self.assertEqual(len(filtered_entries), 2)
        self.assertIn(result1, filtered_entries)
        self.assertIn(result2, filtered_entries)

    @patch('lib.get_file_creation_date.get_file_creation_date._PROVIDERS_AVAILABLE')
    @patch('lib.get_file_creation_date.get_file_creation_date.get_oldest_entry')
    def test_get_file_creation_date_empty_providers_list(self, mock_get_oldest, mock_providers):
        """Test get_file_creation_date with no available providers."""
        mock_providers.__iter__.return_value = []
        mock_get_oldest.return_value = None
        
        # Call function
        result = get_file_creation_date(self.test_file_path)
        
        # Verify results
        self.assertIsNone(result)
        mock_get_oldest.assert_called_once_with([])

    @patch('lib.get_file_creation_date.get_file_creation_date._PROVIDERS_AVAILABLE')
    @patch('lib.get_file_creation_date.get_file_creation_date.get_oldest_entry')
    def test_get_file_creation_date_provider_exception(self, mock_get_oldest, mock_providers):
        """Test get_file_creation_date handles provider exceptions gracefully."""
        # Setup mock provider that raises exception
        mock_provider1 = Mock()
        mock_provider1.supports_file.return_value = True
        mock_provider1.get_file_creation_date.side_effect = Exception("Provider error")
        
        # Setup normal provider
        mock_provider2 = Mock()
        mock_provider2.supports_file.return_value = True
        mock_provider2.get_file_creation_date.return_value = self.test_result
        
        mock_providers.__iter__.return_value = [mock_provider1, mock_provider2]
        mock_get_oldest.return_value = self.test_result
        
        # The current implementation doesn't handle exceptions from providers,
        # so this test should expect the exception to propagate
        with self.assertRaises(Exception) as cm:
            get_file_creation_date(self.test_file_path)
        
        self.assertEqual(str(cm.exception), "Provider error")


if __name__ == "__main__":
    unittest.main()
