"""
Test script to verify the storage service fix for duplicate files
"""
import os
import django
import sys

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopearn.settings')
django.setup()

from django.core.files.uploadedfile import SimpleUploadedFile
from services.storage_service import SupabaseStorageService

def test_storage_service():
    """Test that uploading the same file twice creates unique filenames"""
    print("Testing storage service for duplicate file handling...")
    
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
    print("Uploading first file...")
    result1 = storage_service.upload_file(test_file, folder='test_uploads')
    
    # Check if upload was successful
    if result1.get('success', False):
        print(f"First upload successful: {result1.get('file_path')}")
    else:
        print(f"First upload failed: {result1.get('error', 'Unknown error')}")
        return
    
    # Upload the second file with the same name
    print("Uploading second file with same name...")
    result2 = storage_service.upload_file(test_file2, folder='test_uploads')
    
    # Check if second upload was successful
    if result2.get('success', False):
        print(f"Second upload successful: {result2.get('file_path')}")
    else:
        print(f"Second upload failed: {result2.get('error', 'Unknown error')}")
        return
    
    # Verify that the filenames are different
    if result1.get('file_path') != result2.get('file_path'):
        print("SUCCESS: Files have different paths to avoid conflicts")
    else:
        print("ERROR: Files have the same path, which could cause conflicts")
    
    # Clean up - delete the test files
    print("Cleaning up test files...")
    storage_service.delete_file(result1.get('file_path'))
    storage_service.delete_file(result2.get('file_path'))
    print("Test completed.")

if __name__ == '__main__':
    test_storage_service()