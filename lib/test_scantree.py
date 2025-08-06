import os
import tempfile
import unittest
from pathlib import Path

from lib.scantree import scantree


class TestScantree(unittest.TestCase):
    def setUp(self):
        """Set up a temporary directory structure for testing."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_root = Path(self.temp_dir.name)
        
        # Create test directory structure:
        # test_root/
        #   ├── file1.txt
        #   ├── file2.py
        #   ├── subdir1/
        #   │   ├── file3.txt
        #   │   └── subdir2/
        #   │       └── file4.py
        #   └── empty_dir/
        
        # Create files in root
        (self.test_root / "file1.txt").write_text("content1")
        (self.test_root / "file2.py").write_text("content2")
        
        # Create subdirectories and files
        subdir1 = self.test_root / "subdir1"
        subdir1.mkdir()
        (subdir1 / "file3.txt").write_text("content3")
        
        subdir2 = subdir1 / "subdir2"
        subdir2.mkdir()
        (subdir2 / "file4.py").write_text("content4")
        
        # Create empty directory
        (self.test_root / "empty_dir").mkdir()

    def tearDown(self):
        """Clean up temporary directory."""
        self.temp_dir.cleanup()

    def test_scantree_returns_all_files_recursively(self):
        """Test that scantree returns all files in directory tree."""
        entries = list(scantree(str(self.test_root)))
        
        # Convert to relative paths for easier comparison
        relative_paths = [
            str(Path(entry.path).relative_to(self.test_root))
            for entry in entries
        ]
        
        expected_files = [
            "file1.txt",
            "file2.py", 
            str(Path("subdir1") / "file3.txt"),
            str(Path("subdir1") / "subdir2" / "file4.py")
        ]
        
        # Sort both lists for comparison
        relative_paths.sort()
        expected_files.sort()
        
        self.assertEqual(relative_paths, expected_files)

    def test_scantree_with_single_file(self):
        """Test that scantree handles a single file (not directory)."""
        file_path = self.test_root / "file1.txt"
        entries = list(scantree(str(file_path)))
        
        # Should return empty list for non-directory
        self.assertEqual(len(entries), 0)

    def test_scantree_with_empty_directory(self):
        """Test that scantree handles empty directory."""
        empty_dir = self.test_root / "empty_dir"
        entries = list(scantree(str(empty_dir)))
        
        self.assertEqual(len(entries), 0)

    def test_scantree_entries_are_direntries(self):
        """Test that scantree returns os.DirEntry objects."""
        entries = list(scantree(str(self.test_root)))
        
        self.assertGreater(len(entries), 0)
        for entry in entries:
            self.assertIsInstance(entry, os.DirEntry)
            self.assertTrue(entry.is_file())

    def test_scantree_with_nonexistent_path(self):
        """Test that scantree handles nonexistent path gracefully."""
        nonexistent_path = str(self.test_root / "nonexistent")
        
        # The current implementation returns empty list for nonexistent paths
        # because Path(nonexistent_path).is_dir() returns False
        entries = list(scantree(nonexistent_path))
        self.assertEqual(len(entries), 0)

    def test_scantree_does_not_follow_symlinks(self):
        """Test that scantree does not follow symbolic links."""
        # Create a symlink to a directory (if supported on this platform)
        try:
            symlink_path = self.test_root / "symlink_dir"
            symlink_path.symlink_to(self.test_root / "subdir1", target_is_directory=True)
            
            entries = list(scantree(str(self.test_root)))
            
            # Check that files from the original subdir1 are found
            original_subdir_files = [
                entry for entry in entries 
                if str(Path(entry.path).relative_to(self.test_root)).startswith("subdir1")
                and "symlink_dir" not in entry.path
            ]
            self.assertGreater(len(original_subdir_files), 0)
            
            # Check that no files are found through the symlink path
            # This means files should not have paths containing both "symlink_dir" AND the target files
            symlinked_target_files = [
                entry for entry in entries 
                if "symlink_dir" in entry.path and 
                   (entry.name == "file3.txt" or entry.name == "file4.py")
            ]
            
            # Should find no files from within the symlinked directory
            self.assertEqual(len(symlinked_target_files), 0)
            
        except (OSError, NotImplementedError):
            # Skip this test if symlinks are not supported
            self.skipTest("Symlinks not supported on this platform")


if __name__ == "__main__":
    unittest.main()
