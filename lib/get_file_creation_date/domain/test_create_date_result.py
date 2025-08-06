import unittest
from datetime import datetime

from lib.get_file_creation_date.domain.create_date_result import GetFileCreationDateResult


class TestGetFileCreationDateResult(unittest.TestCase):
    def test_creation_with_all_fields(self):
        """Test creating GetFileCreationDateResult with all fields."""
        creation_date = datetime(2023, 12, 25, 10, 30, 0)
        provider = "test_provider"
        provider_info = "additional info"
        
        result = GetFileCreationDateResult(
            creation_date=creation_date,
            provider=provider,
            provider_info=provider_info
        )
        
        self.assertEqual(result.creation_date, creation_date)
        self.assertEqual(result.provider, provider)
        self.assertEqual(result.provider_info, provider_info)

    def test_creation_without_provider_info(self):
        """Test creating GetFileCreationDateResult without provider_info."""
        creation_date = datetime(2023, 12, 25, 10, 30, 0)
        provider = "test_provider"
        
        result = GetFileCreationDateResult(
            creation_date=creation_date,
            provider=provider
        )
        
        self.assertEqual(result.creation_date, creation_date)
        self.assertEqual(result.provider, provider)
        self.assertIsNone(result.provider_info)

    def test_equality(self):
        """Test equality comparison between GetFileCreationDateResult objects."""
        creation_date = datetime(2023, 12, 25, 10, 30, 0)
        provider = "test_provider"
        provider_info = "additional info"
        
        result1 = GetFileCreationDateResult(
            creation_date=creation_date,
            provider=provider,
            provider_info=provider_info
        )
        
        result2 = GetFileCreationDateResult(
            creation_date=creation_date,
            provider=provider,
            provider_info=provider_info
        )
        
        self.assertEqual(result1, result2)

    def test_inequality_different_dates(self):
        """Test inequality when creation dates differ."""
        date1 = datetime(2023, 12, 25, 10, 30, 0)
        date2 = datetime(2023, 12, 26, 10, 30, 0)
        provider = "test_provider"
        
        result1 = GetFileCreationDateResult(creation_date=date1, provider=provider)
        result2 = GetFileCreationDateResult(creation_date=date2, provider=provider)
        
        self.assertNotEqual(result1, result2)

    def test_inequality_different_providers(self):
        """Test inequality when providers differ."""
        creation_date = datetime(2023, 12, 25, 10, 30, 0)
        
        result1 = GetFileCreationDateResult(creation_date=creation_date, provider="provider1")
        result2 = GetFileCreationDateResult(creation_date=creation_date, provider="provider2")
        
        self.assertNotEqual(result1, result2)

    def test_inequality_different_provider_info(self):
        """Test inequality when provider_info differs."""
        creation_date = datetime(2023, 12, 25, 10, 30, 0)
        provider = "test_provider"
        
        result1 = GetFileCreationDateResult(
            creation_date=creation_date,
            provider=provider,
            provider_info="info1"
        )
        result2 = GetFileCreationDateResult(
            creation_date=creation_date,
            provider=provider,
            provider_info="info2"
        )
        
        self.assertNotEqual(result1, result2)

    def test_string_representation(self):
        """Test string representation of GetFileCreationDateResult."""
        creation_date = datetime(2023, 12, 25, 10, 30, 0)
        provider = "test_provider"
        provider_info = "additional info"
        
        result = GetFileCreationDateResult(
            creation_date=creation_date,
            provider=provider,
            provider_info=provider_info
        )
        
        str_repr = str(result)
        
        # String representation should contain the key information
        # The dataclass default str/repr shows datetime.datetime(2023, 12, 25, 10, 30)
        self.assertIn("2023, 12, 25, 10, 30", str_repr)
        self.assertIn(provider, str_repr)
        self.assertIn(provider_info, str_repr)

    def test_repr_representation(self):
        """Test repr representation of GetFileCreationDateResult."""
        creation_date = datetime(2023, 12, 25, 10, 30, 0)
        provider = "test_provider"
        
        result = GetFileCreationDateResult(
            creation_date=creation_date,
            provider=provider
        )
        
        repr_str = repr(result)
        
        # Repr should contain class name and field values
        self.assertIn("GetFileCreationDateResult", repr_str)
        # The dataclass default repr shows datetime.datetime(2023, 12, 25, 10, 30)
        self.assertIn("2023, 12, 25, 10, 30", repr_str)
        self.assertIn(provider, repr_str)

    def test_dataclass_immutability(self):
        """Test that the dataclass fields can be accessed and modified."""
        creation_date = datetime(2023, 12, 25, 10, 30, 0)
        provider = "test_provider"
        
        result = GetFileCreationDateResult(
            creation_date=creation_date,
            provider=provider
        )
        
        # Test that fields can be accessed
        self.assertEqual(result.creation_date, creation_date)
        self.assertEqual(result.provider, provider)
        
        # Test that fields can be modified (dataclass is not frozen)
        new_date = datetime(2024, 1, 1, 12, 0, 0)
        result.creation_date = new_date
        self.assertEqual(result.creation_date, new_date)


if __name__ == "__main__":
    unittest.main()
