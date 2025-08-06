import unittest
from unittest.mock import patch, Mock
from datetime import datetime

from lib.get_file_creation_date.domain.create_date_result import GetFileCreationDateResult
from lib.get_file_creation_date.providers.windows_shell.windows_shell import WindowsShellFileCreationDateProvider


class TestWindowsShellFileCreationDateProvider(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        self.provider = WindowsShellFileCreationDateProvider()

    def test_initialization(self):
        """Test provider initialization."""
        self.assertIsNotNone(self.provider.logger)
        self.assertEqual(self.provider.logger.name, "windows_shell")

    @patch('platform.system')
    @patch('lib.get_file_creation_date.providers.windows_shell.windows_shell.WIN32COM_AVAILABLE', True)
    def test_is_available_on_windows(self, mock_system):
        """Test is_available returns True on Windows."""
        mock_system.return_value = "Windows"
        self.assertTrue(self.provider.is_available())

    @patch('platform.system')
    def test_is_available_on_non_windows(self, mock_system):
        """Test is_available returns False on non-Windows systems."""
        for system in ["Linux", "Darwin", "FreeBSD"]:
            with self.subTest(system=system):
                mock_system.return_value = system
                self.assertFalse(self.provider.is_available())

    def test_supports_file(self):
        """Test that Windows Shell provider supports all files."""
        test_files = [
            "/path/to/image.jpg",
            "C:\\Windows\\file.txt",
            "/path/to/video.mp4",
            "relative/path.pdf",
            "any_file.xyz"
        ]
        
        for file_path in test_files:
            with self.subTest(file_path=file_path):
                self.assertTrue(self.provider.supports_file(file_path))

    def test_priority_properties_defined(self):
        """Test that priority properties are defined correctly."""
        expected_properties = [
            "System.Photo.DateTaken",
            "System.DateAcquired",
            "System.DateCreated",
            "System.DateModified",
        ]
        
        self.assertEqual(self.provider.PRIORITY_PROPERTIES, expected_properties)

    @patch('platform.system', return_value='Windows')
    @patch('lib.get_file_creation_date.providers.windows_shell.windows_shell.WIN32COM_AVAILABLE', True)
    @patch('lib.get_file_creation_date.providers.windows_shell.windows_shell.shellcon')
    @patch('lib.get_file_creation_date.providers.windows_shell.windows_shell.propsys')
    @patch('lib.get_file_creation_date.providers.windows_shell.windows_shell.parse_date')
    def test_get_file_creation_date_success(self, mock_parse_date, mock_propsys, mock_shellcon, mock_system):
        """Test successful date extraction with Windows Shell."""
        # Setup mocks
        mock_shellcon.GPS_DEFAULT = Mock()
        mock_prop_store = Mock()
        mock_propsys.SHGetPropertyStoreFromParsingName.return_value = mock_prop_store
        
        mock_prop_key = Mock()
        mock_propsys.PSGetPropertyKeyFromName.return_value = mock_prop_key
        
        mock_prop_value = Mock()
        mock_prop_value.GetValue.return_value = "2023-12-25 10:30:00"
        mock_prop_store.GetValue.return_value = mock_prop_value
        
        test_date = datetime(2023, 12, 25, 10, 30, 0)
        mock_parse_date.return_value = test_date
        
        file_path = "C:\\path\\to\\test.jpg"
        result = self.provider.get_file_creation_date(file_path)
        
        # Verify calls
        mock_propsys.SHGetPropertyStoreFromParsingName.assert_called_once()
        mock_propsys.PSGetPropertyKeyFromName.assert_called()
        mock_prop_store.GetValue.assert_called()
        mock_parse_date.assert_called_with("2023-12-25 10:30:00")
        
        # Verify result
        self.assertIsNotNone(result)
        self.assertIsInstance(result, GetFileCreationDateResult)
        self.assertEqual(result.creation_date, test_date)
        self.assertEqual(result.provider, "windows_shell")
        self.assertEqual(result.provider_info, "System.Photo.DateTaken")  # First property in list

    @patch('platform.system', return_value='Windows')
    @patch('lib.get_file_creation_date.providers.windows_shell.windows_shell.WIN32COM_AVAILABLE', True)
    @patch('lib.get_file_creation_date.providers.windows_shell.windows_shell.shellcon')
    @patch('lib.get_file_creation_date.providers.windows_shell.windows_shell.propsys')
    def test_get_file_creation_date_property_store_failure(self, mock_propsys, mock_shellcon, mock_system):
        """Test when property store cannot be obtained."""
        mock_propsys.SHGetPropertyStoreFromParsingName.side_effect = Exception("Property store error")
        
        file_path = "C:\\path\\to\\test.jpg"
        result = self.provider.get_file_creation_date(file_path)
        
        self.assertIsNone(result)

    @patch('platform.system', return_value='Windows')
    @patch('lib.get_file_creation_date.providers.windows_shell.windows_shell.WIN32COM_AVAILABLE', True)
    @patch('lib.get_file_creation_date.providers.windows_shell.windows_shell.shellcon')
    @patch('lib.get_file_creation_date.providers.windows_shell.windows_shell.propsys')
    def test_get_file_creation_date_no_valid_properties(self, mock_propsys, mock_shellcon, mock_system):
        """Test when no properties contain valid dates."""
        # Setup mocks
        mock_prop_store = Mock()
        mock_propsys.SHGetPropertyStoreFromParsingName.return_value = mock_prop_store
        
        # Mock PSGetPropertyKeyFromName to raise exception (property not available)
        mock_propsys.PSGetPropertyKeyFromName.side_effect = Exception("Property not found")
        
        file_path = "C:\\path\\to\\test.jpg"
        result = self.provider.get_file_creation_date(file_path)
        
        self.assertIsNone(result)

    @patch('platform.system', return_value='Windows')
    @patch('lib.get_file_creation_date.providers.windows_shell.windows_shell.WIN32COM_AVAILABLE', True)
    @patch('lib.get_file_creation_date.providers.windows_shell.windows_shell.shellcon')
    @patch('lib.get_file_creation_date.providers.windows_shell.windows_shell.propsys')
    @patch('lib.get_file_creation_date.providers.windows_shell.windows_shell.parse_date')
    def test_get_file_creation_date_tries_all_properties(self, mock_parse_date, mock_propsys, mock_shellcon, mock_system):
        """Test that all properties are tried in priority order."""
        # Setup mocks
        mock_prop_store = Mock()
        mock_propsys.SHGetPropertyStoreFromParsingName.return_value = mock_prop_store
        
        mock_prop_key = Mock()
        mock_propsys.PSGetPropertyKeyFromName.return_value = mock_prop_key
        
        # Mock property values - first three return None/empty, fourth returns valid date
        call_count = [0]
        def mock_get_value(prop_key):
            call_count[0] += 1
            if call_count[0] <= 3:
                mock_value = Mock()
                mock_value.GetValue.return_value = None
                return mock_value
            else:
                mock_value = Mock()
                mock_value.GetValue.return_value = "2023-12-25 10:30:00"
                return mock_value
        
        mock_prop_store.GetValue.side_effect = mock_get_value
        
        test_date = datetime(2023, 12, 25, 10, 30, 0)
        mock_parse_date.return_value = test_date
        
        file_path = "C:\\path\\to\\test.jpg"
        result = self.provider.get_file_creation_date(file_path)
        
        # Should have tried all 4 properties
        self.assertEqual(mock_propsys.PSGetPropertyKeyFromName.call_count, 4)
        self.assertEqual(mock_prop_store.GetValue.call_count, 4)
        
        # Should succeed with the last property
        self.assertIsNotNone(result)
        self.assertEqual(result.provider_info, "System.DateModified")  # Last property in list

    @patch('platform.system', return_value='Windows')
    @patch('lib.get_file_creation_date.providers.windows_shell.windows_shell.WIN32COM_AVAILABLE', True)
    @patch('lib.get_file_creation_date.providers.windows_shell.windows_shell.shellcon')
    @patch('lib.get_file_creation_date.providers.windows_shell.windows_shell.propsys')
    @patch('lib.get_file_creation_date.providers.windows_shell.windows_shell.parse_date')
    def test_get_file_creation_date_parse_date_failure(self, mock_parse_date, mock_propsys, mock_shellcon, mock_system):
        """Test when parse_date fails to parse the property value."""
        # Setup mocks
        mock_prop_store = Mock()
        mock_propsys.SHGetPropertyStoreFromParsingName.return_value = mock_prop_store
        
        mock_prop_key = Mock()
        mock_propsys.PSGetPropertyKeyFromName.return_value = mock_prop_key
        
        mock_prop_value = Mock()
        mock_prop_value.GetValue.return_value = "invalid date format"
        mock_prop_store.GetValue.return_value = mock_prop_value
        
        mock_parse_date.return_value = None  # Parse fails
        
        file_path = "C:\\path\\to\\test.jpg"
        result = self.provider.get_file_creation_date(file_path)
        
        # Should try other properties when parse fails
        self.assertGreater(mock_propsys.PSGetPropertyKeyFromName.call_count, 1)

    @patch('platform.system', return_value='Windows')
    @patch('lib.get_file_creation_date.providers.windows_shell.windows_shell.WIN32COM_AVAILABLE', True)
    @patch('lib.get_file_creation_date.providers.windows_shell.windows_shell.shellcon')
    @patch('lib.get_file_creation_date.providers.windows_shell.windows_shell.propsys')
    @patch('lib.get_file_creation_date.providers.windows_shell.windows_shell.parse_date')
    def test_get_file_creation_date_empty_property_value(self, mock_parse_date, mock_propsys, mock_shellcon, mock_system):
        """Test when property value is empty or None."""
        # Setup mocks
        mock_prop_store = Mock()
        mock_propsys.SHGetPropertyStoreFromParsingName.return_value = mock_prop_store
        
        mock_prop_key = Mock()
        mock_propsys.PSGetPropertyKeyFromName.return_value = mock_prop_key
        
        # Test with None value
        mock_prop_value = Mock()
        mock_prop_value.GetValue.return_value = None
        mock_prop_store.GetValue.return_value = mock_prop_value
        
        file_path = "C:\\path\\to\\test.jpg"
        result = self.provider.get_file_creation_date(file_path)
        
        # parse_date should not be called for None values
        mock_parse_date.assert_not_called()
        
        # Should try other properties
        self.assertGreater(mock_propsys.PSGetPropertyKeyFromName.call_count, 1)

    @patch('platform.system', return_value='Windows')
    @patch('lib.get_file_creation_date.providers.windows_shell.windows_shell.WIN32COM_AVAILABLE', True)
    @patch('lib.get_file_creation_date.providers.windows_shell.windows_shell.shellcon')
    @patch('lib.get_file_creation_date.providers.windows_shell.windows_shell.propsys')
    def test_get_file_creation_date_logs_errors(self, mock_propsys, mock_shellcon, mock_system):
        """Test that errors are properly logged."""
        mock_propsys.SHGetPropertyStoreFromParsingName.side_effect = Exception("Test error")
        
        with patch.object(self.provider.logger, 'error') as mock_error:
            file_path = "C:\\path\\to\\test.jpg"
            result = self.provider.get_file_creation_date(file_path)
            
            self.assertIsNone(result)
            mock_error.assert_called_once()
            
            # Check that the error message contains relevant information
            error_call_args = mock_error.call_args[0][0]
            self.assertIn("Property system access failed", error_call_args)
            self.assertIn(file_path, error_call_args)

    def test_string_representation(self):
        """Test string representation of the provider."""
        str_repr = str(self.provider)
        self.assertEqual(str_repr, "WindowsShellFileCreationDateProvider")

    @patch('platform.system')
    @patch('lib.get_file_creation_date.providers.windows_shell.windows_shell.WIN32COM_AVAILABLE', True)
    def test_repr_representation(self, mock_system):
        """Test repr representation of the provider."""
        mock_system.return_value = "Windows"
        repr_str = repr(self.provider)
        expected = "WindowsShellFileCreationDateProvider(available=True)"
        self.assertEqual(repr_str, expected)


if __name__ == "__main__":
    unittest.main()
