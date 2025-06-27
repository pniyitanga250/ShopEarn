# Storage Migration: Local to Supabase

This document outlines the migration from local file storage to Supabase storage for the ShopEarn application.

## Overview

The ShopEarn application has been updated to use Supabase Storage for all file uploads instead of local storage. This provides several benefits:

- Files are stored in the cloud, making them accessible from anywhere
- Improved scalability and reliability
- Better integration with other Supabase services
- Reduced server storage requirements

## Changes Made

1. **Updated Django Settings**
   - Added `STORAGES` configuration to force Django to use SupabaseStorage
   - Ensured proper initialization of the SupabaseStorage class

2. **Verified Supabase Environment Variables**
   - SUPABASE_URL
   - SUPABASE_ANON_KEY
   - SUPABASE_SERVICE_ROLE_KEY
   - SUPABASE_BUCKET_NAME

3. **Migrated Existing Files**
   - Created and ran a migration script to move files from local storage to Supabase
   - Updated database records to point to the new Supabase URLs

4. **Tested File Uploads**
   - Verified that all model file fields (ImageField, FileField) are properly using Supabase storage
   - Tested direct file uploads using the SupabaseStorageService

## File Storage Implementation

The application uses two main components for file storage:

1. **SupabaseStorage** (`utils/supabase_storage.py`)
   - A custom Django storage backend that implements the Django Storage API
   - Used automatically by Django for all file operations (upload, download, URL generation)

2. **SupabaseStorageService** (`services/storage_service.py`)
   - A service class for direct interaction with Supabase storage
   - Provides methods for uploading, downloading, and managing files
   - Can be used for more complex operations not covered by the Django Storage API

## Testing

Two test scripts were created to verify the storage migration:

1. **check_storage_config.py**
   - Verifies that Django is properly configured to use Supabase storage
   - Checks environment variables and URL generation

2. **test_file_uploads.py**
   - Tests file uploads for all models with file fields
   - Verifies that files are properly uploaded to Supabase
   - Tests direct file uploads using the SupabaseStorageService

## Usage Guidelines

### Model File Fields

When defining models with file fields, use the standard Django `FileField` or `ImageField`:

```python
class MyModel(models.Model):
    image = models.ImageField(upload_to='my_model_images/')
    document = models.FileField(upload_to='my_model_documents/')
```

Django will automatically use the SupabaseStorage backend for these fields.

### Direct File Uploads

For more complex file operations, use the SupabaseStorageService:

```python
from services.storage_service import SupabaseStorageService

# Create a storage service instance
storage_service = SupabaseStorageService()

# Upload a file
result = storage_service.upload_file(file_obj, folder='my_folder')

# Get the public URL
public_url = result.get('public_url')

# Delete a file
storage_service.delete_file('my_folder/my_file.jpg')
```

## Troubleshooting

If you encounter issues with file storage:

1. **Check Environment Variables**
   - Ensure all Supabase environment variables are properly set in the `.env` file

2. **Verify Storage Configuration**
   - Run `python check_storage_config.py` to verify the storage configuration

3. **Test File Uploads**
   - Run `python test_file_uploads.py` to test file uploads

4. **Check Supabase Console**
   - Log in to the Supabase console to verify that files are being uploaded to the correct bucket