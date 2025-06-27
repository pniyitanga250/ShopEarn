from utils.supabase_client import get_supabase_client, get_supabase_admin_client
from django.conf import settings
import uuid
import os

class SupabaseStorageService:
    def __init__(self, use_admin_client=False):
        self.client = get_supabase_admin_client() if use_admin_client else get_supabase_client()
        self.bucket_name = settings.SUPABASE_BUCKET_NAME  # 'shopearn'
    
    def upload_file(self, file, folder='uploads', filename=None):
        """Upload a file to Supabase storage"""
        if not filename:
            # Generate unique filename
            file_extension = os.path.splitext(file.name)[1]
            filename = f"{uuid.uuid4()}{file_extension}"
        
        file_path = f"{folder}/{filename}" if folder else filename
        
        try:
            # Reset file pointer to beginning
            file.seek(0)
            
            # Upload file to 'shopearn' bucket
            response = self.client.storage.from_(self.bucket_name).upload(
                file_path, 
                file.read(),
                file_options={
                    'content-type': file.content_type if hasattr(file, 'content_type') else 'application/octet-stream'
                }
            )
            
            if response:
                # Get public URL
                public_url = self.client.storage.from_(self.bucket_name).get_public_url(file_path)
                return {
                    'success': True,
                    'file_path': file_path,
                    'public_url': public_url,
                    'filename': filename
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def delete_file(self, file_path):
        """Delete a file from Supabase storage"""
        try:
            response = self.client.storage.from_(self.bucket_name).remove([file_path])
            return {'success': True, 'response': response}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_file_url(self, file_path):
        """Get public URL for a file"""
        return self.client.storage.from_(self.bucket_name).get_public_url(file_path)
    
    def list_files(self, folder='', limit=100):
        """List files in a folder"""
        try:
            # Remove the limit parameter - Supabase storage list() doesn't accept it
            response = self.client.storage.from_(self.bucket_name).list(
                path=folder
            )
            
            # Apply limit manually if needed
            if limit and len(response) > limit:
                response = response[:limit]
                
            return {'success': True, 'files': response}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def download_file(self, file_path):
        """Download a file from storage"""
        try:
            response = self.client.storage.from_(self.bucket_name).download(file_path)
            return {'success': True, 'data': response}
        except Exception as e:  # Fixed typo: was "Exception in e"
            return {'success': False, 'error': str(e)}