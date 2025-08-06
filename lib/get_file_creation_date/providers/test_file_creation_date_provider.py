import unittest
from abc import ABC

from lib.get_file_creation_date.providers.file_creation_date_provider import FileCreationDateProvider


class ConcreteFileCreationDateProvider(FileCreationDateProvider):
    """Concrete implementation for testing the abstract base class."""
    
    def __init__(self, available=True, supports_all_files=True):
        self._available = available
        self._supports_all_files = supports_all_files
    
    def is_available(self) -> bool:
        return self._available
    
    def supports_file(self, file_path: str) -> bool:
        return self._supports_all_files
    
    def get_file_creation_date(self, file_path: str):
        # Simple implementation for testing
        if self.is_available() and self.supports_file(file_path):
            return f"result_for_{file_path}"
        return None


class TestFileCreationDateProvider(unittest.TestCase):
    def test_abstract_base_class(self):
        """Test that FileCreationDateProvider is an abstract base class."""
        self.assertTrue(issubclass(FileCreationDateProvider, ABC))
        
        # Should not be able to instantiate directly
        with self.assertRaises(TypeError):
            FileCreationDateProvider()

    def test_concrete_implementation_instantiation(self):
        """Test that concrete implementations can be instantiated."""
        provider = ConcreteFileCreationDateProvider()
        self.assertIsInstance(provider, FileCreationDateProvider)

    def test_abstract_methods_exist(self):
        """Test that all required abstract methods exist."""
        abstract_methods = FileCreationDateProvider.__abstractmethods__
        expected_methods = {'is_available', 'supports_file', 'get_file_creation_date'}
        self.assertEqual(abstract_methods, expected_methods)

    def test_str_representation(self):
        """Test string representation of provider."""
        provider = ConcreteFileCreationDateProvider()
        str_repr = str(provider)
        self.assertEqual(str_repr, "ConcreteFileCreationDateProvider")

    def test_repr_representation(self):
        """Test repr representation of provider."""
        provider = ConcreteFileCreationDateProvider(available=True)
        repr_str = repr(provider)
        expected = "ConcreteFileCreationDateProvider(available=True)"
        self.assertEqual(repr_str, expected)

    def test_repr_representation_unavailable(self):
        """Test repr representation when provider is unavailable."""
        provider = ConcreteFileCreationDateProvider(available=False)
        repr_str = repr(provider)
        expected = "ConcreteFileCreationDateProvider(available=False)"
        self.assertEqual(repr_str, expected)

    def test_is_available_method(self):
        """Test is_available method implementation."""
        available_provider = ConcreteFileCreationDateProvider(available=True)
        unavailable_provider = ConcreteFileCreationDateProvider(available=False)
        
        self.assertTrue(available_provider.is_available())
        self.assertFalse(unavailable_provider.is_available())

    def test_supports_file_method(self):
        """Test supports_file method implementation."""
        supporting_provider = ConcreteFileCreationDateProvider(supports_all_files=True)
        non_supporting_provider = ConcreteFileCreationDateProvider(supports_all_files=False)
        
        test_file = "/path/to/test/file.jpg"
        
        self.assertTrue(supporting_provider.supports_file(test_file))
        self.assertFalse(non_supporting_provider.supports_file(test_file))

    def test_get_file_creation_date_method(self):
        """Test get_file_creation_date method implementation."""
        provider = ConcreteFileCreationDateProvider()
        test_file = "/path/to/test/file.jpg"
        
        result = provider.get_file_creation_date(test_file)
        expected = f"result_for_{test_file}"
        self.assertEqual(result, expected)

    def test_get_file_creation_date_unavailable_provider(self):
        """Test get_file_creation_date when provider is unavailable."""
        provider = ConcreteFileCreationDateProvider(available=False)
        test_file = "/path/to/test/file.jpg"
        
        result = provider.get_file_creation_date(test_file)
        self.assertIsNone(result)

    def test_get_file_creation_date_unsupported_file(self):
        """Test get_file_creation_date when file is not supported."""
        provider = ConcreteFileCreationDateProvider(supports_all_files=False)
        test_file = "/path/to/test/file.jpg"
        
        result = provider.get_file_creation_date(test_file)
        self.assertIsNone(result)

    def test_inheritance_hierarchy(self):
        """Test that concrete provider properly inherits from base class."""
        provider = ConcreteFileCreationDateProvider()
        
        # Should be instance of both concrete and abstract classes
        self.assertIsInstance(provider, ConcreteFileCreationDateProvider)
        self.assertIsInstance(provider, FileCreationDateProvider)
        
        # Should have all required methods
        self.assertTrue(hasattr(provider, 'is_available'))
        self.assertTrue(hasattr(provider, 'supports_file'))
        self.assertTrue(hasattr(provider, 'get_file_creation_date'))
        self.assertTrue(hasattr(provider, '__str__'))
        self.assertTrue(hasattr(provider, '__repr__'))


if __name__ == "__main__":
    unittest.main()
