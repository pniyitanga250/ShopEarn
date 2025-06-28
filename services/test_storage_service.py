import os
import unittest
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from services.storage_service import SupabaseStorageService

class TestStorageService(TestCase):
    def test_upload_file_uniqueness(self):
        """Test that uploading the same file twice creates unique filenames"""
        # Create a test file
        test_file = SimpleUploadedFile(
            name="test_file.txt",
            content=b"Test file content",
            content_type="text/plain"
        )
        
        # Create another file with the same name
        test_file2 = SimpleUploadedFile(
            name="test_file.txt",
            content=b"Different content, same filename",
            content_type="text/plain"
        )
        
        # Initialize the storage service
        storage_service = SupabaseStorageService()
        
        # Upload the first file
        result1 = storage_service.upload_file(test_file, folder='test_uploads')
        
        # Check if upload was successful
        self.assertTrue(result1.get('success', False), 
                       f"First upload failed: {result1.get('error', 'Unknown error')}")
        
        # Upload the second file with the same name
        result2 = storage_service.upload_file(test_file2, folder='test_uploads')
        
        # Check if second upload was successful
        self.assertTrue(result2.get('success', False), 
                       f"Second upload failed: {result2.get('error', 'Unknown error')}")
        
        # Verify that the filenames are different
        self.assertNotEqual(result1.get('file_path'), result2.get('file_path'),
                           "Files should have different paths to avoid conflicts")
        
        # Clean up - delete the test files
        storage_service.delete_file(result1.get('file_path'))
        storage_service.delete_file(result2.get('file_path'))

if __name__ == '__main__':
    unittest.main()