import unittest
from unittest.mock import patch, Mock
import sys
from io import StringIO

from create_copy_list import main


class TestCreateCopyList(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        # Store original argv for restoration
        self.original_argv = sys.argv.copy()

    def tearDown(self):
        """Restore original argv."""
        sys.argv = self.original_argv

    @patch('create_copy_list.generate_copy_list')
    def test_main_with_single_source(self, mock_generate_copy_list):
        """Test main function with single source directory."""
        # Mock command line arguments
        test_source = "/path/to/source"
        test_destination = "/path/to/destination"
        sys.argv = ["create_copy_list.py", "--source", test_source, "--destination", test_destination]
        
        # Call main function
        main()
        
        # Verify that generate_copy_list was called with correct arguments
        mock_generate_copy_list.assert_called_once_with([test_source], test_destination)

    @patch('create_copy_list.generate_copy_list')
    def test_main_with_multiple_sources(self, mock_generate_copy_list):
        """Test main function with multiple source directories."""
        # Mock command line arguments with multiple sources
        test_sources = ["/path/to/source1", "/path/to/source2", "/path/to/source3"]
        test_destination = "/path/to/destination"
        sys.argv = ["create_copy_list.py", "--source"] + test_sources + ["--destination", test_destination]
        
        # Call main function
        main()
        
        # Verify that generate_copy_list was called with correct arguments
        mock_generate_copy_list.assert_called_once_with(test_sources, test_destination)

    @patch('create_copy_list.generate_copy_list')
    def test_main_missing_source_argument(self, mock_generate_copy_list):
        """Test main function fails with missing source argument."""
        # Mock command line arguments without required --source
        test_destination = "/path/to/destination"
        sys.argv = ["create_copy_list.py", "--destination", test_destination]
        
        # Should raise SystemExit due to missing required argument
        with self.assertRaises(SystemExit):
            main()
        
        # generate_copy_list should not be called
        mock_generate_copy_list.assert_not_called()

    @patch('create_copy_list.generate_copy_list')
    def test_main_missing_destination_argument(self, mock_generate_copy_list):
        """Test main function fails with missing destination argument."""
        # Mock command line arguments without required --destination
        test_source = "/path/to/source"
        sys.argv = ["create_copy_list.py", "--source", test_source]
        
        # Should raise SystemExit due to missing required argument
        with self.assertRaises(SystemExit):
            main()
        
        # generate_copy_list should not be called
        mock_generate_copy_list.assert_not_called()

    @patch('create_copy_list.generate_copy_list')
    @patch('sys.stderr', new_callable=StringIO)
    def test_main_with_invalid_argument(self, mock_stderr, mock_generate_copy_list):
        """Test main function with invalid arguments."""
        # Mock command line arguments with invalid option
        sys.argv = ["create_copy_list.py", "--invalid-option", "value"]
        
        # Should raise SystemExit due to invalid argument
        with self.assertRaises(SystemExit):
            main()
        
        # generate_copy_list should not be called
        mock_generate_copy_list.assert_not_called()

    @patch('create_copy_list.generate_copy_list')
    def test_main_with_help_argument(self, mock_generate_copy_list):
        """Test main function with help argument."""
        # Mock command line arguments with help
        sys.argv = ["create_copy_list.py", "--help"]
        
        # Should raise SystemExit (normal behavior for --help)
        with self.assertRaises(SystemExit) as cm:
            main()
        
        # Exit code should be 0 for help
        self.assertEqual(cm.exception.code, 0)
        
        # generate_copy_list should not be called
        mock_generate_copy_list.assert_not_called()

    @patch('create_copy_list.generate_copy_list')
    def test_main_with_windows_paths(self, mock_generate_copy_list):
        """Test main function with Windows-style paths."""
        # Test with Windows paths
        test_sources = ["C:\\Users\\Test\\Source1", "D:\\Data\\Source2"]
        test_destination = "E:\\Backup\\Destination"
        sys.argv = ["create_copy_list.py", "--source"] + test_sources + ["--destination", test_destination]
        
        # Call main function
        main()
        
        # Verify that generate_copy_list was called with correct arguments
        mock_generate_copy_list.assert_called_once_with(test_sources, test_destination)

    @patch('create_copy_list.generate_copy_list')
    def test_main_with_relative_paths(self, mock_generate_copy_list):
        """Test main function with relative paths."""
        # Test with relative paths
        test_sources = ["./source1", "../source2", "source3"]
        test_destination = "./destination"
        sys.argv = ["create_copy_list.py", "--source"] + test_sources + ["--destination", test_destination]
        
        # Call main function
        main()
        
        # Verify that generate_copy_list was called with correct arguments
        mock_generate_copy_list.assert_called_once_with(test_sources, test_destination)

    @patch('create_copy_list.generate_copy_list')
    def test_main_handles_generate_copy_list_exception(self, mock_generate_copy_list):
        """Test that main function handles exceptions from generate_copy_list."""
        # Make generate_copy_list raise an exception
        mock_generate_copy_list.side_effect = Exception("Test error")
        
        test_source = "/path/to/source"
        test_destination = "/path/to/destination"
        sys.argv = ["create_copy_list.py", "--source", test_source, "--destination", test_destination]
        
        # The main function doesn't explicitly handle exceptions,
        # so this should propagate the exception
        with self.assertRaises(Exception) as cm:
            main()
        
        self.assertEqual(str(cm.exception), "Test error")
        mock_generate_copy_list.assert_called_once_with([test_source], test_destination)

    def test_argument_parser_description(self):
        """Test that argument parser has correct description."""
        # Mock sys.argv for help
        sys.argv = ["create_copy_list.py", "--help"]
        
        # Capture stdout to check the help message
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            with self.assertRaises(SystemExit):
                main()
            
            help_output = mock_stdout.getvalue()
            self.assertIn("Generate a list of files to be copied based on creation dates", help_output)

    @patch('create_copy_list.generate_copy_list')
    def test_main_function_if_name_main_guard(self, mock_generate_copy_list):
        """Test the if __name__ == '__main__' guard functionality."""
        # This is tested implicitly by importing the module
        # If the guard wasn't there, generate_copy_list would be called on import
        
        # Import should not trigger main
        import create_copy_list
        
        # generate_copy_list should not have been called just from import
        mock_generate_copy_list.assert_not_called()

    @patch('create_copy_list.generate_copy_list')
    def test_main_with_paths_containing_spaces(self, mock_generate_copy_list):
        """Test main function with paths containing spaces."""
        # Test with paths containing spaces
        test_sources = ["/path with spaces/source1", "/another path/source2"]
        test_destination = "/destination with spaces"
        sys.argv = ["create_copy_list.py", "--source"] + test_sources + ["--destination", test_destination]
        
        # Call main function
        main()
        
        # Verify that generate_copy_list was called with correct arguments
        mock_generate_copy_list.assert_called_once_with(test_sources, test_destination)

    @patch('create_copy_list.generate_copy_list')
    def test_main_source_action_extend_behavior(self, mock_generate_copy_list):
        """Test that source argument correctly extends the list."""
        # Test that multiple --source arguments are combined
        test_source1 = "/path/to/source1"
        test_source2 = "/path/to/source2"
        test_destination = "/path/to/destination"
        
        # Use multiple --source arguments
        sys.argv = [
            "create_copy_list.py",
            "--source", test_source1,
            "--source", test_source2,
            "--destination", test_destination
        ]
        
        # Call main function
        main()
        
        # Verify that generate_copy_list was called with both sources
        mock_generate_copy_list.assert_called_once_with([test_source1, test_source2], test_destination)

    @patch('create_copy_list.generate_copy_list')
    def test_main_preserves_exact_paths(self, mock_generate_copy_list):
        """Test that main function preserves the exact paths passed."""
        # Test that paths are passed exactly as provided
        test_sources = ["./relative/../source1", "/absolute/source2"]
        test_destination = "./relative/../destination"
        sys.argv = ["create_copy_list.py", "--source"] + test_sources + ["--destination", test_destination]
        
        # Call main function
        main()
        
        # Verify that generate_copy_list was called with exact arguments
        mock_generate_copy_list.assert_called_once_with(test_sources, test_destination)


if __name__ == "__main__":
    unittest.main()
