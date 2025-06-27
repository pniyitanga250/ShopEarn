import os
import django
import sys
from pathlib import Path

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopearn.settings')
django.setup()

from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.db.models import FileField, ImageField
from django.apps import apps

from services.storage_service import SupabaseStorageService
from shop_products.models import Category, Product, ProductImage
from shop_accounts.models import User
from shop_orders.models import Order  # Import if you have payment proof images

def get_all_model_instances_with_files():
    """Get all model instances that have file fields"""
    instances = []
    
    # Add specific models with file fields
    instances.extend([(instance, 'image') for instance in Category.objects.all() if instance.image])
    instances.extend([(instance, 'main_image') for instance in Product.objects.all() if instance.main_image])
    instances.extend([(instance, 'image') for instance in ProductImage.objects.all() if instance.image])
    instances.extend([(instance, 'profile_picture') for instance in User.objects.all() if instance.profile_picture])
    
    # Add payment proof images if they exist
    try:
        from shop_orders.models import PaymentProof
        instances.extend([(instance, 'proof_image') for instance in PaymentProof.objects.all() if instance.proof_image])
    except (ImportError, django.core.exceptions.ImproperlyConfigured):
        print("PaymentProof model not found or not configured, skipping...")
    
    return instances

def migrate_file_to_supabase(instance, field_name):
    """Migrate a single file from local storage to Supabase"""
    # Get the file field
    file_field = getattr(instance, field_name)
    
    if not file_field:
        return False
    
    # Get the file path
    file_path = file_field.name
    
    # Check if file exists in local storage
    local_path = os.path.join(settings.MEDIA_ROOT, file_path)
    if not os.path.exists(local_path):
        print(f"File not found in local storage: {local_path}")
        return False
    
    try:
        # Create a ContentFile from the local file
        with open(local_path, 'rb') as f:
            file_content = f.read()
        
        content_file = ContentFile(file_content)
        content_file.name = os.path.basename(file_path)
        
        # Get the folder from the file path
        folder = os.path.dirname(file_path)
        
        # Upload to Supabase
        storage_service = SupabaseStorageService(use_admin_client=True)
        result = storage_service.upload_file(
            content_file, 
            folder=folder,
            filename=os.path.basename(file_path)
        )
        
        if result.get('success'):
            # Update the model instance with the new file path
            # Note: Django's default_storage will handle this correctly
            # since we've set DEFAULT_FILE_STORAGE to SupabaseStorage
            
            # The file path should remain the same, but now it will be
            # served from Supabase instead of local storage
            
            print(f"Successfully migrated {file_path} to Supabase")
            print(f"Public URL: {result.get('public_url')}")
            return True
        else:
            print(f"Failed to upload {file_path} to Supabase: {result.get('error')}")
            return False
    
    except Exception as e:
        print(f"Error migrating {file_path}: {str(e)}")
        return False

def main():
    """Main migration function"""
    print("Starting migration of files from local storage to Supabase...")
    
    # Get all model instances with file fields
    instances = get_all_model_instances_with_files()
    print(f"Found {len(instances)} files to migrate")
    
    # Migrate each file
    success_count = 0
    for instance, field_name in instances:
        print(f"Migrating {field_name} for {instance.__class__.__name__} {instance.id}...")
        if migrate_file_to_supabase(instance, field_name):
            success_count += 1
    
    print(f"Migration complete. Successfully migrated {success_count} out of {len(instances)} files.")

if __name__ == "__main__":
    main()