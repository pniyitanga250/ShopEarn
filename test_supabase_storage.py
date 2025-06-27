import os
import django
import io

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopearn.settings')
django.setup()

from services.storage_service import SupabaseStorageService

def test_supabase_storage():
    # Create storage service instance
    storage_service = SupabaseStorageService(use_admin_client=True)
    
    # Test listing files
    print("Listing files in the bucket:")
    list_result = storage_service.list_files()
    print(list_result)
    
    # Test uploading a file
    print("\nUploading a test file:")
    test_file = io.BytesIO(b"This is a test file content")
    test_file.name = "test_file.txt"
    upload_result = storage_service.upload_file(test_file, folder='test_uploads')
    print(upload_result)
    
    if upload_result.get('success'):
        file_path = upload_result.get('file_path')
        
        # Test getting file URL
        print("\nGetting file URL:")
        url = storage_service.get_file_url(file_path)
        print(f"File URL: {url}")
        
        # Test downloading the file
        print("\nDownloading the file:")
        download_result = storage_service.download_file(file_path)
        print(f"Download successful: {download_result.get('success')}")
        if download_result.get('success'):
            print(f"File content: {download_result.get('data').decode('utf-8')}")
        
        # Test deleting the file
        print("\nDeleting the file:")
        delete_result = storage_service.delete_file(file_path)
        print(delete_result)

if __name__ == "__main__":
    test_supabase_storage()