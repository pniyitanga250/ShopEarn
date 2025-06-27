import os
import django
import io
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopearn.settings')
django.setup()

from shop_products.models import Category, Product
from shop_orders.models import Order
from services.storage_service import SupabaseStorageService
from django.contrib.auth import get_user_model

User = get_user_model()

def create_test_image(filename='test.jpg', size=(100, 100), color='red'):
    """Create a test image file"""
    file = io.BytesIO()
    image = Image.new('RGB', size, color)
    image.save(file, 'JPEG')
    file.name = filename
    file.seek(0)
    return file

def test_supabase_storage_direct():
    """Test direct upload to Supabase storage"""
    print("Testing direct upload to Supabase storage...")
    
    # Create a test image
    test_file = create_test_image()
    
    # Use the storage service to upload the file
    storage_service = SupabaseStorageService(use_admin_client=True)
    result = storage_service.upload_file(test_file, folder='test_uploads')
    
    print(f"Upload result: {result}")
    
    if result['success']:
        # Try to get the file URL
        file_url = storage_service.get_file_url(result['file_path'])
        print(f"File URL: {file_url}")
        
        # Delete the file
        delete_result = storage_service.delete_file(result['file_path'])
        print(f"Delete result: {delete_result}")
    
    return result['success']

def test_category_image_upload():
    """Test uploading an image to a Category model"""
    print("\nTesting Category image upload...")
    
    # Create a test image
    test_file = create_test_image()
    uploaded_file = SimpleUploadedFile("test_category.jpg", test_file.getvalue(), content_type="image/jpeg")
    
    # Create a category with the image
    category = Category.objects.create(
        name="Test Category",
        slug="test-category",
        description="Test category description",
        image=uploaded_file
    )
    
    # Check if the image was uploaded
    if category.image:
        print(f"Category image URL: {category.image.url}")
        
        # Clean up
        category.delete()
        return True
    else:
        print("Failed to upload category image")
        return False

def test_product_image_upload():
    """Test uploading an image to a Product model"""
    print("\nTesting Product image upload...")
    
    # Create a test category first
    category = Category.objects.create(
        name="Test Product Category",
        slug="test-product-category",
        description="Test product category description"
    )
    
    # Create a test image
    test_file = create_test_image()
    uploaded_file = SimpleUploadedFile("test_product.jpg", test_file.getvalue(), content_type="image/jpeg")
    
    # Create a product with the image
    product = Product.objects.create(
        name="Test Product",
        slug="test-product",
        description="Test product description",
        price=99.99,
        product_value=99.99,
        category=category,
        main_image=uploaded_file
    )
    
    # Check if the image was uploaded
    if product.main_image:
        print(f"Product image URL: {product.main_image.url}")
        
        # Clean up
        product.delete()
        category.delete()
        return True
    else:
        print("Failed to upload product image")
        category.delete()
        return False

if __name__ == "__main__":
    # Run the tests
    direct_upload_success = test_supabase_storage_direct()
    category_upload_success = test_category_image_upload()
    product_upload_success = test_product_image_upload()
    
    # Print summary
    print("\n=== Test Summary ===")
    print(f"Direct upload to Supabase: {'✅ Success' if direct_upload_success else '❌ Failed'}")
    print(f"Category image upload: {'✅ Success' if category_upload_success else '❌ Failed'}")
    print(f"Product image upload: {'✅ Success' if product_upload_success else '❌ Failed'}")
    
    if direct_upload_success and category_upload_success and product_upload_success:
        print("\n🎉 All tests passed! Supabase storage integration is working correctly.")
    else:
        print("\n⚠️ Some tests failed. Please check the error messages above.")