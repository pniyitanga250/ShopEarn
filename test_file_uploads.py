import os
import django
import io
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopearn.settings')
django.setup()

from django.conf import settings
from shop_products.models import Category, Product, ProductImage
from shop_accounts.models import User
from shop_orders.models import Order
from services.storage_service import SupabaseStorageService

def create_test_image(filename='test_image.jpg', size=(100, 100), color='red'):
    """Create a test image file"""
    file_obj = io.BytesIO()
    image = Image.new('RGB', size, color)
    image.save(file_obj, 'JPEG')
    file_obj.seek(0)
    return SimpleUploadedFile(filename, file_obj.getvalue(), content_type='image/jpeg')

def test_category_image_upload():
    """Test uploading an image to a Category"""
    print("\n=== Testing Category Image Upload ===")
    
    # Create a test image
    test_image = create_test_image('test_category.jpg')
    
    # Create a category with the test image
    category = Category.objects.create(
        name='Test Category',
        description='Test category description',
        image=test_image
    )
    
    # Check if the image was uploaded to Supabase
    print(f"Category image URL: {category.image.url}")
    
    # Verify the URL is a Supabase URL
    if 'supabase' in category.image.url:
        print("SUCCESS: Image was uploaded to Supabase")
    else:
        print("FAILURE: Image was not uploaded to Supabase")
    
    return category

def test_product_image_upload():
    """Test uploading an image to a Product"""
    print("\n=== Testing Product Image Upload ===")
    
    # Get or create a category
    category = Category.objects.first()
    if not category:
        category = Category.objects.create(name='Test Category')
    
    # Create a test image
    test_image = create_test_image('test_product.jpg')
    
    # Create a product with the test image
    product = Product.objects.create(
        name='Test Product',
        description='Test product description',
        price=99.99,
        product_value=50.00,
        category=category,
        main_image=test_image
    )
    
    # Check if the image was uploaded to Supabase
    print(f"Product image URL: {product.main_image.url}")
    
    # Verify the URL is a Supabase URL
    if 'supabase' in product.main_image.url:
        print("SUCCESS: Image was uploaded to Supabase")
    else:
        print("FAILURE: Image was not uploaded to Supabase")
    
    return product

def test_product_additional_image_upload():
    """Test uploading an additional image to a Product"""
    print("\n=== Testing Additional Product Image Upload ===")
    
    # Get or create a product
    product = Product.objects.first()
    if not product:
        product = test_product_image_upload()
    
    # Create a test image
    test_image = create_test_image('test_additional.jpg')
    
    # Create a product image with the test image
    product_image = ProductImage.objects.create(
        product=product,
        image=test_image,
        alt_text='Test additional image'
    )
    
    # Check if the image was uploaded to Supabase
    print(f"Additional image URL: {product_image.image.url}")
    
    # Verify the URL is a Supabase URL
    if 'supabase' in product_image.image.url:
        print("SUCCESS: Image was uploaded to Supabase")
    else:
        print("FAILURE: Image was not uploaded to Supabase")
    
    return product_image

def test_user_profile_picture_upload():
    """Test uploading a profile picture to a User"""
    print("\n=== Testing User Profile Picture Upload ===")
    
    # Get or create a user
    user = User.objects.filter(is_superuser=False).first()
    if not user:
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
    
    # Create a test image
    test_image = create_test_image('test_profile.jpg')
    
    # Update the user with the test image
    user.profile_picture = test_image
    user.save()
    
    # Check if the image was uploaded to Supabase
    print(f"Profile picture URL: {user.profile_picture.url}")
    
    # Verify the URL is a Supabase URL
    if 'supabase' in user.profile_picture.url:
        print("SUCCESS: Image was uploaded to Supabase")
    else:
        print("FAILURE: Image was not uploaded to Supabase")
    
    return user

def test_order_payment_proof_upload():
    """Test uploading a payment proof to an Order"""
    print("\n=== Testing Order Payment Proof Upload ===")
    
    # Get or create a user
    user = User.objects.filter(is_superuser=False).first()
    if not user:
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
    
    # Create a test image
    test_image = create_test_image('test_payment.jpg')
    
    # Create an order with the test image
    order = Order.objects.create(
        user=user,
        first_name='Test',
        last_name='User',
        email='test@example.com',
        phone='1234567890',
        address='123 Test St',
        city='Test City',
        state='Test State',
        postal_code='12345',
        country='Test Country',
        total_price=99.99,
        payment_method='MTN_MOBILE_MONEY',
        transaction_id='TEST123',
        payment_proof=test_image
    )
    
    # Check if the image was uploaded to Supabase
    print(f"Payment proof URL: {order.payment_proof.url}")
    
    # Verify the URL is a Supabase URL
    if 'supabase' in order.payment_proof.url:
        print("SUCCESS: Image was uploaded to Supabase")
    else:
        print("FAILURE: Image was not uploaded to Supabase")
    
    return order

def test_direct_supabase_upload():
    """Test uploading a file directly using the SupabaseStorageService"""
    print("\n=== Testing Direct Supabase Upload ===")
    
    # Create a test image
    test_image = create_test_image('test_direct.jpg')
    
    # Upload the image using the SupabaseStorageService
    storage_service = SupabaseStorageService(use_admin_client=True)
    result = storage_service.upload_file(test_image, folder='test_uploads')
    
    # Check if the upload was successful
    if result.get('success'):
        print(f"Direct upload URL: {result.get('public_url')}")
        print("SUCCESS: Image was uploaded to Supabase")
    else:
        print(f"FAILURE: Image was not uploaded to Supabase - {result.get('error')}")
    
    return result

def cleanup_test_data():
    """Clean up test data"""
    print("\n=== Cleaning Up Test Data ===")
    
    # Delete test categories
    Category.objects.filter(name='Test Category').delete()
    print("Deleted test categories")
    
    # Delete test products
    Product.objects.filter(name='Test Product').delete()
    print("Deleted test products")
    
    # Delete test users
    User.objects.filter(username='testuser').delete()
    print("Deleted test users")
    
    # Delete test orders
    Order.objects.filter(transaction_id='TEST123').delete()
    print("Deleted test orders")

def main():
    """Run all tests"""
    print("=== Starting File Upload Tests ===")
    
    try:
        test_category_image_upload()
        test_product_image_upload()
        test_product_additional_image_upload()
        test_user_profile_picture_upload()
        test_order_payment_proof_upload()
        test_direct_supabase_upload()
    finally:
        # Clean up test data
        cleanup_test_data()
    
    print("\n=== All Tests Completed ===")

if __name__ == "__main__":
    main()