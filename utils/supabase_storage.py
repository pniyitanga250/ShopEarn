import os
import uuid
from io import BytesIO
from urllib.parse import urljoin, urlparse

from django.conf import settings
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible

from utils.supabase_client import get_supabase_client, get_supabase_admin_client


@deconstructible
class SupabaseStorage(Storage):
    """
    Custom Django storage backend for Supabase
    
    This storage backend allows Django to store files in Supabase Storage.
    """
    
    def __init__(self, bucket_name=None, use_admin_client=False):
        self.bucket_name = bucket_name or settings.SUPABASE_BUCKET_NAME
        self.client = get_supabase_admin_client() if use_admin_client else get_supabase_client()
        
    def _get_supabase_bucket(self):
        """Get the Supabase bucket object"""
        return self.client.storage.from_(self.bucket_name)
    
    def _generate_filename(self, name):
        """Generate a unique filename to avoid conflicts"""
        if not name:
            return str(uuid.uuid4())
        
        # Add uniqueness to the filename
        base_name, extension = os.path.splitext(name)
        return f"{base_name}_{uuid.uuid4()}{extension}"
    
    def _open(self, name, mode='rb'):
        """
        Open a file from Supabase storage
        """
        bucket = self._get_supabase_bucket()
        file_data = bucket.download(name)
        
        # Create a file-like object
        file_obj = BytesIO(file_data)
        file_obj.name = name
        file_obj.mode = mode
        
        return file_obj
    
    def _save(self, name, content):
        """
        Save a file to Supabase storage
        """
        # Ensure the file has a unique name
        name = self._generate_filename(name)
        
        # Get the file content
        content.seek(0)
        file_data = content.read()
        
        # Upload to Supabase
        bucket = self._get_supabase_bucket()
        
        # Get content type if available
        content_type = getattr(content, 'content_type', 'application/octet-stream')
        
        try:
            # Upload the file
            bucket.upload(
                name,
                file_data,
                file_options={
                    'content-type': content_type
                }
            )
        except Exception as e:
            # If we get a conflict (409) error, try with a different filename
            if "409" in str(e) or "Duplicate" in str(e):
                # Generate a completely new unique name
                name = f"{uuid.uuid4()}{os.path.splitext(name)[1]}"
                
                # Try upload again
                bucket.upload(
                    name,
                    file_data,
                    file_options={
                        'content-type': content_type
                    }
                )
            else:
                # Re-raise other exceptions
                raise
        
        return name
    
    def delete(self, name):
        """
        Delete a file from Supabase storage
        """
        bucket = self._get_supabase_bucket()
        try:
            bucket.remove([name])
            return True
        except Exception:
            return False
    
    def exists(self, name):
        """
        Check if a file exists in Supabase storage
        """
        bucket = self._get_supabase_bucket()
        try:
            # Try to get file metadata
            # This will raise an exception if the file doesn't exist
            path_parts = os.path.split(name)
            folder = path_parts[0] if len(path_parts) > 1 else ''
            
            files = bucket.list(path=folder)
            for file in files:
                if file['name'] == name:
                    return True
            return False
        except Exception:
            return False
    
    def url(self, name):
        """
        Get the URL for a file
        """
        bucket = self._get_supabase_bucket()
        # Make sure we have a valid name
        if not name:
            return None
        
        # Return the Supabase public URL
        return bucket.get_public_url(name)
    
    def size(self, name):
        """
        Get the size of a file
        """
        bucket = self._get_supabase_bucket()
        try:
            # Try to get file metadata
            path_parts = os.path.split(name)
            folder = path_parts[0] if len(path_parts) > 1 else ''
            
            files = bucket.list(path=folder)
            for file in files:
                if file['name'] == name and 'metadata' in file and 'size' in file['metadata']:
                    return file['metadata']['size']
            return 0
        except Exception:
            return 0
    
    def get_accessed_time(self, name):
        """
        Get the last accessed time of a file
        """
        # Supabase doesn't provide this information directly
        # Return the current time as a fallback
        from django.utils import timezone
        return timezone.now()
    
    def get_created_time(self, name):
        """
        Get the creation time of a file
        """
        bucket = self._get_supabase_bucket()
        try:
            path_parts = os.path.split(name)
            folder = path_parts[0] if len(path_parts) > 1 else ''
            
            files = bucket.list(path=folder)
            for file in files:
                if file['name'] == name and 'created_at' in file:
                    from django.utils.dateparse import parse_datetime
                    return parse_datetime(file['created_at'])
            
            # Fallback to current time
            from django.utils import timezone
            return timezone.now()
        except Exception:
            from django.utils import timezone
            return timezone.now()
    
    def get_modified_time(self, name):
        """
        Get the last modified time of a file
        """
        bucket = self._get_supabase_bucket()
        try:
            path_parts = os.path.split(name)
            folder = path_parts[0] if len(path_parts) > 1 else ''
            
            files = bucket.list(path=folder)
            for file in files:
                if file['name'] == name and 'updated_at' in file:
                    from django.utils.dateparse import parse_datetime
                    return parse_datetime(file['updated_at'])
            
            # Fallback to current time
            from django.utils import timezone
            return timezone.now()
        except Exception:
            from django.utils import timezone
            return timezone.now()
    
    def listdir(self, path):
        """
        List the contents of a directory
        """
        bucket = self._get_supabase_bucket()
        try:
            files = bucket.list(path=path)
            
            # Separate directories and files
            directories = set()
            filenames = []
            
            for file in files:
                name = file['name']
                if path and name.startswith(path):
                    name = name[len(path):].lstrip('/')
                
                # Check if it's a directory
                if '/' in name:
                    dir_name = name.split('/')[0]
                    directories.add(dir_name)
                else:
                    filenames.append(name)
            
            return list(directories), filenames
        except Exception:
            return [], []