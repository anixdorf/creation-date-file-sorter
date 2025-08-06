import unittest
from unittest.mock import patch, mock_open, MagicMock, call
from pathlib import Path

from lib.operations import copy_files, check_files


class TestCopyFiles(unittest.TestCase):
    @patch("lib.operations.shutil.copy2")
    @patch("lib.operations._get_hash")
    @patch("lib.operations.Path")
    @patch("lib.operations.open")
    @patch(
        "lib.operations.tqdm", lambda x, **kwargs: x
    )  # Mock tqdm to disable progress bars
    @patch("lib.operations.setup_logging")
    @patch("lib.operations.logging")
    def test_handles_multiple_duplicates_with_different_hashes(
        self,
        mock_logging,
        mock_setup_logging,
        mock_open,
        mock_Path,
        mock_get_hash,
        mock_copy2,
    ):
        """
        Tests that copy_files correctly renames a file to _dup_2 when the
        original and the _dup_1 destinations already exist and have different hashes.
        """
        copy_list_content = (
            "# header1\n# header2\n" "source/file.txt;2023-01-01;;;dest/file.txt\n"
        )
        mock_open.return_value.__enter__.return_value.__iter__.return_value = iter(
            copy_list_content.splitlines(True)
        )

        dest_path_str = "dest/file.txt"
        dup1_path_str = "dest/file_dup_1.txt"
        dup2_path_str = "dest/file_dup_2.txt"

        mock_dest_path = MagicMock(spec=Path)
        mock_dest_path.__str__.return_value = dest_path_str
        mock_dest_path.is_file.return_value = True

        mock_dest_dir = MagicMock(spec=Path)
        mock_dest_dir.mkdir.return_value = None
        mock_dest_path.parent = mock_dest_dir

        mock_dest_path.stem = "file"
        mock_dest_path.suffix = ".txt"

        mock_dup1_path = MagicMock(spec=Path)
        mock_dup1_path.__str__.return_value = dup1_path_str
        mock_dup1_path.is_file.return_value = True

        mock_dup2_path = MagicMock(spec=Path)
        mock_dup2_path.__str__.return_value = dup2_path_str
        mock_dup2_path.is_file.return_value = False

        def truediv_side_effect(name):
            if name == "file_dup_1.txt":
                return mock_dup1_path
            if name == "file_dup_2.txt":
                return mock_dup2_path
            return MagicMock()

        mock_dest_path.parent.__truediv__.side_effect = truediv_side_effect

        def path_constructor_side_effect(path_arg):
            if str(path_arg) == dest_path_str:
                return mock_dest_path
            return MagicMock()

        mock_Path.side_effect = path_constructor_side_effect

        def get_hash_side_effect(path):
            path_str = str(path)
            if path_str == "source/file.txt":
                return "hash_source"
            if path_str == dest_path_str:
                return "hash_dest"
            if path_str == dup1_path_str:
                return "hash_dup1"
            return "unexpected_hash"

        mock_get_hash.side_effect = get_hash_side_effect

        copy_files("dummy_copy_list.csv")

        mock_copy2.assert_called_once()
        source_arg, dest_arg = mock_copy2.call_args[0]
        self.assertEqual(source_arg, "source/file.txt")
        self.assertEqual(str(dest_arg), dup2_path_str)

        self.assertEqual(
            mock_get_hash.call_args_list,
            [
                call("source/file.txt"),
                call(mock_dest_path),
                call(mock_dup1_path),
            ],
        )

    @patch("lib.operations.shutil.copy2")
    @patch("lib.operations._get_hash")
    @patch("lib.operations.Path")
    @patch("lib.operations.open")
    @patch("lib.operations.tqdm", lambda x, **kwargs: x)
    @patch("lib.operations.setup_logging")
    @patch("lib.operations.logging")
    def test_skips_copy_when_identical_duplicate_is_found(
        self,
        mock_logging,
        mock_setup_logging,
        mock_open,
        mock_Path,
        mock_get_hash,
        mock_copy2,
    ):
        """
        Tests that copy_files does NOT copy a file if an identical version
        (matching hash) already exists as a duplicate.
        """
        copy_list_content = (
            "# header1\n# header2\n" "source/file.txt;2023-01-01;;;dest/file.txt\n"
        )
        mock_open.return_value.__enter__.return_value.__iter__.return_value = iter(
            copy_list_content.splitlines(True)
        )

        dest_path_str = "dest/file.txt"
        dup1_path_str = "dest/file_dup_1.txt"
        dup2_path_str = "dest/file_dup_2.txt"

        mock_dest_path = MagicMock(spec=Path)
        mock_dest_path.__str__.return_value = dest_path_str
        mock_dest_path.is_file.return_value = True

        mock_dest_dir = MagicMock(spec=Path)
        mock_dest_dir.mkdir.return_value = None
        mock_dest_path.parent = mock_dest_dir

        mock_dest_path.stem = "file"
        mock_dest_path.suffix = ".txt"

        mock_dup1_path = MagicMock(spec=Path)
        mock_dup1_path.__str__.return_value = dup1_path_str
        mock_dup1_path.is_file.return_value = True

        mock_dup2_path = MagicMock(spec=Path)
        mock_dup2_path.__str__.return_value = dup2_path_str
        mock_dup2_path.is_file.return_value = True  # This one also exists

        def truediv_side_effect(name):
            if name == "file_dup_1.txt":
                return mock_dup1_path
            if name == "file_dup_2.txt":
                return mock_dup2_path
            return MagicMock()

        mock_dest_path.parent.__truediv__.side_effect = truediv_side_effect

        def path_constructor_side_effect(path_arg):
            if str(path_arg) == dest_path_str:
                return mock_dest_path
            return MagicMock()

        mock_Path.side_effect = path_constructor_side_effect

        def get_hash_side_effect(path):
            path_str = str(path)
            if path_str == "source/file.txt":
                return "hash_source"
            if path_str == dest_path_str:
                return "hash_dest_different"
            if path_str == dup1_path_str:
                return "hash_dup1_different"
            if path_str == dup2_path_str:
                return "hash_source"  # Identical hash!
            return "unexpected_hash"

        mock_get_hash.side_effect = get_hash_side_effect

        copy_files("dummy_copy_list.csv")

        # The key assertion: copy should NOT be called.
        mock_copy2.assert_not_called()

    @patch("lib.operations.shutil.copy2")
    @patch("lib.operations._get_hash")
    @patch("lib.operations.Path")
    @patch("lib.operations.open")
    @patch("lib.operations.tqdm", lambda x, **kwargs: x)
    @patch("lib.operations.setup_logging")
    @patch("lib.operations.logging")
    def test_mkdir_is_called_once_per_directory(
        self,
        mock_logging,
        mock_setup_logging,
        mock_open,
        mock_Path,
        mock_get_hash,
        mock_copy2,
    ):
        """
        Tests that mkdir is only called once for a given destination directory,
        even when multiple files are copied to it.
        """
        copy_list_content = (
            "# header1\n# header2\n"
            "source/file1.txt;2023-01-01;;;dest/file1.txt\n"
            "source/file2.txt;2023-01-01;;;dest/file2.txt\n"
        )
        mock_open.return_value.__enter__.return_value.__iter__.return_value = iter(
            copy_list_content.splitlines(True)
        )

        mock_dest_dir = MagicMock(spec=Path)
        mock_dest_dir.mkdir.return_value = None

        mock_file1_path = MagicMock(spec=Path)
        mock_file1_path.parent = mock_dest_dir
        mock_file1_path.is_file.return_value = False  # No duplicates to worry about

        mock_file2_path = MagicMock(spec=Path)
        mock_file2_path.parent = mock_dest_dir
        mock_file2_path.is_file.return_value = False

        def path_constructor_side_effect(path_arg):
            if str(path_arg) == "dest/file1.txt":
                return mock_file1_path
            if str(path_arg) == "dest/file2.txt":
                return mock_file2_path
            return MagicMock()

        mock_Path.side_effect = path_constructor_side_effect
        mock_get_hash.return_value = "some_hash"

        copy_files("dummy_copy_list.csv")

        # Assert that mkdir was called only once for the shared directory.
        mock_dest_dir.mkdir.assert_called_once_with(parents=True, exist_ok=True)


class TestCheckFiles(unittest.TestCase):
    def _run_check_files_with_mocks(
        self,
        mock_Path,
        mock_open,
        mock_glob,
        copy_list_content,
        filesystem_mocks,
        glob_returns,
    ):
        """Helper to run check_files with mocked filesystem and copy list."""
        mock_open.return_value.__enter__.return_value.readlines.return_value = (
            copy_list_content.splitlines(True)
        )
        mock_glob.return_value = glob_returns

        def path_constructor_side_effect(path_arg):
            path_str = str(path_arg)
            if path_str in filesystem_mocks:
                return filesystem_mocks[path_str]
            # Return a mock that doesn't exist for any other path
            mock_nonexistent = MagicMock(spec=Path)
            mock_nonexistent.exists.return_value = False
            return mock_nonexistent

        mock_Path.side_effect = path_constructor_side_effect

        check_files("dummy_copy_list.csv")

    def _create_mock_file(self, path_str, exists, size):
        """Helper to create a mock Path object for a file."""
        mock_file = MagicMock(spec=Path)
        mock_file.__str__.return_value = path_str
        mock_file.exists.return_value = exists
        if exists:
            mock_file.stat.return_value.st_size = size
        mock_file.stem = Path(path_str).stem
        mock_file.suffix = Path(path_str).suffix
        mock_file.parent = MagicMock(spec=Path)
        mock_file.parent.__str__.return_value = str(Path(path_str).parent)

        self.filesystem_mocks[path_str] = mock_file
        return mock_file

    def setUp(self):
        """Setup mocks for each test."""
        self.filesystem_mocks = {}

    @patch("lib.operations.glob.glob")
    @patch("lib.operations.logging")
    @patch("lib.operations.setup_logging")
    @patch("lib.operations.tqdm", lambda x, **kwargs: x)
    @patch("lib.operations.open")
    @patch("lib.operations.Path")
    def test_check_files_success(
        self, mock_Path, mock_open, mock_setup_logging, mock_logging, mock_glob
    ):
        """Tests the success path where source and destination files match in size."""
        self._create_mock_file("source/file.txt", True, 1024)
        self._create_mock_file("dest/file.txt", True, 1024)

        copy_list = "# h\n# h\nsource/file.txt;;;;dest/file.txt"
        self._run_check_files_with_mocks(
            mock_Path,
            mock_open,
            mock_glob,
            copy_list,
            self.filesystem_mocks,
            [],
        )

    @patch("lib.operations.glob.glob")
    @patch("lib.operations.logging")
    @patch("lib.operations.setup_logging")
    @patch("lib.operations.tqdm", lambda x, **kwargs: x)
    @patch("lib.operations.open")
    @patch("lib.operations.Path")
    def test_check_files_destination_not_found(
        self, mock_Path, mock_open, mock_setup_logging, mock_logging, mock_glob
    ):
        """Tests that a warning is logged if the destination file is not found."""
        self._create_mock_file("source/file.txt", True, 1024)
        self._create_mock_file("dest/file.txt", False, 0)  # Does not exist

        copy_list = "# h\n# h\nsource/file.txt;;;;dest/file.txt"
        self._run_check_files_with_mocks(
            mock_Path,
            mock_open,
            mock_glob,
            copy_list,
            self.filesystem_mocks,
            [],
        )

        mock_logging.getLogger.return_value.warning.assert_any_call(
            "File not found at destination: dest/file.txt"
        )

    @patch("lib.operations.glob.glob")
    @patch("lib.operations.logging")
    @patch("lib.operations.setup_logging")
    @patch("lib.operations.tqdm", lambda x, **kwargs: x)
    @patch("lib.operations.open")
    @patch("lib.operations.Path")
    def test_check_files_size_mismatch(
        self, mock_Path, mock_open, mock_setup_logging, mock_logging, mock_glob
    ):
        """Tests that a warning is logged if the destination file has a different size."""
        self._create_mock_file("source/file.txt", True, 1024)
        self._create_mock_file("dest/file.txt", True, 512)  # Different size

        copy_list = "# h\n# h\nsource/file.txt;;;;dest/file.txt"
        self._run_check_files_with_mocks(
            mock_Path,
            mock_open,
            mock_glob,
            copy_list,
            self.filesystem_mocks,
            [],
        )

        mock_logging.getLogger.return_value.warning.assert_any_call(
            "File size mismatch for source/file.txt and dest/file.txt."
        )

    @patch("lib.operations.glob.glob")
    @patch("lib.operations.logging")
    @patch("lib.operations.setup_logging")
    @patch("lib.operations.tqdm", lambda x, **kwargs: x)
    @patch("lib.operations.open")
    @patch("lib.operations.Path")
    def test_check_files_success_with_duplicate(
        self, mock_Path, mock_open, mock_setup_logging, mock_logging, mock_glob
    ):
        """
        Tests success when the original destination has a wrong size,
        but a duplicate file has the correct size.
        """
        self._create_mock_file("source/file.txt", True, 1024)
        self._create_mock_file("dest/file.txt", True, 512)  # Mismatch
        self._create_mock_file("dest/file_dup_1.txt", True, 1024)  # Match

        copy_list = "# h\n# h\nsource/file.txt;;;;dest/file.txt"
        self._run_check_files_with_mocks(
            mock_Path,
            mock_open,
            mock_glob,
            copy_list,
            self.filesystem_mocks,
            ["dest/file_dup_1.txt"],
        )

        # Assert no warning was logged for mismatch because the duplicate was found
        for call_item in mock_logging.getLogger.return_value.warning.call_args_list:
            self.assertNotIn("mismatch", call_item[0][0])
