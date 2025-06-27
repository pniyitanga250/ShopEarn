import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopearn.settings')
django.setup()

from django.conf import settings
from django.core.files.storage import default_storage
from utils.supabase_storage import SupabaseStorage

def check_storage_config():
    """Check if the storage backend is properly configured"""
    print("=== Checking Storage Configuration ===")
    
    # Check if DEFAULT_FILE_STORAGE is set to SupabaseStorage
    print(f"DEFAULT_FILE_STORAGE: {settings.DEFAULT_FILE_STORAGE}")
    if settings.DEFAULT_FILE_STORAGE == 'utils.supabase_storage.SupabaseStorage':
        print("✓ DEFAULT_FILE_STORAGE is correctly set to SupabaseStorage")
    else:
        print("✗ DEFAULT_FILE_STORAGE is not set to SupabaseStorage")
    
    # Check if default_storage is an instance of SupabaseStorage
    print(f"\ndefault_storage class: {default_storage.__class__.__name__}")
    if isinstance(default_storage, SupabaseStorage):
        print("✓ default_storage is an instance of SupabaseStorage")
    else:
        print("✗ default_storage is not an instance of SupabaseStorage")
    
    # Check if Supabase environment variables are set
    print("\nChecking Supabase environment variables:")
    supabase_vars = {
        'SUPABASE_URL': getattr(settings, 'SUPABASE_URL', None),
        'SUPABASE_ANON_KEY': getattr(settings, 'SUPABASE_ANON_KEY', None),
        'SUPABASE_SERVICE_ROLE_KEY': getattr(settings, 'SUPABASE_SERVICE_ROLE_KEY', None),
        'SUPABASE_BUCKET_NAME': getattr(settings, 'SUPABASE_BUCKET_NAME', None),
    }
    
    for var_name, var_value in supabase_vars.items():
        if var_value:
            print(f"✓ {var_name} is set")
            # Print a masked version of the value for keys
            if 'KEY' in var_name:
                masked_value = var_value[:10] + '...' + var_value[-5:]
                print(f"  Value: {masked_value}")
            else:
                print(f"  Value: {var_value}")
        else:
            print(f"✗ {var_name} is not set")
    
    # Check if MEDIA_URL and MEDIA_ROOT are set
    print("\nChecking media configuration:")
    print(f"MEDIA_URL: {settings.MEDIA_URL}")
    print(f"MEDIA_ROOT: {settings.MEDIA_ROOT}")
    
    # Try to generate a URL for a test file
    test_file_name = 'test_file.txt'
    test_url = default_storage.url(test_file_name)
    print(f"\nTest URL for '{test_file_name}': {test_url}")
    
    if 'supabase' in test_url.lower():
        print("✓ URL generation is using Supabase")
    else:
        print("✗ URL generation is not using Supabase")

if __name__ == "__main__":
    check_storage_config()