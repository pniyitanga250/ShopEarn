import os
import django
import io
import uuid
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopearn.settings')
django.setup()

from shop_products.models import Category, Product, ProductImage
from shop_orders.models import Order, OrderItem, OrderNote
from services.storage_service import SupabaseStorageService
from django.contrib.auth import get_user_model
from django.core.files.storage import default_storage

User = get_user_model()

def create_test_image(filename='test.jpg', size=(100, 100), color='red'):
    """Create a test image file"""
    file = io.BytesIO()
    image = Image.new('RGB', size, color)
    image.save(file, 'JPEG')
    file.name = filename
    file.seek(0)
    return file

def test_default_storage():
    """Test that the default storage is using Supabase"""
    print("\n=== Testing Default Storage ===")
    
    # Check if default_storage is using our SupabaseStorage
    from utils.supabase_storage import SupabaseStorage
    
    if isinstance(default_storage, SupabaseStorage):
        print("✅ Default storage is using SupabaseStorage")
        return True
    else:
        print(f"❌ Default storage is not using SupabaseStorage. Current storage: {type(default_storage)}")
        return False

def test_category_image():
    """Test category image upload and retrieval"""
    print("\n=== Testing Category Image Upload and Retrieval ===")
    
    # Create a test image
    test_file = create_test_image()
    uploaded_file = SimpleUploadedFile(f"test_category_{uuid.uuid4()}.jpg", test_file.getvalue(), content_type="image/jpeg")
    
    # Create a category with the image
    category_name = f"Test Category {uuid.uuid4()}"
    category = Category.objects.create(
        name=category_name,
        slug=category_name.lower().replace(" ", "-"),
        description="Test category description",
        image=uploaded_file
    )
    
    # Check if the image was uploaded
    if category.image:
        print(f"✅ Category image uploaded successfully")
        print(f"Image URL: {category.image.url}")
        
        # Try to access the image
        try:
            # Check if the file exists in storage
            if default_storage.exists(category.image.name):
                print(f"✅ Image exists in storage at: {category.image.name}")
            else:
                print(f"❌ Image does not exist in storage at: {category.image.name}")
                return False
            
            # Try to open the file
            file = default_storage.open(category.image.name)
            file.close()
            print(f"✅ Image can be opened from storage")
            
            # Clean up
            category.delete()
            return True
        except Exception as e:
            print(f"❌ Error accessing image: {str(e)}")
            category.delete()
            return False
    else:
        print("❌ Failed to upload category image")
        return False

def test_product_image():
    """Test product image upload and retrieval"""
    print("\n=== Testing Product Image Upload and Retrieval ===")
    
    # Create a test category first
    category = Category.objects.create(
        name=f"Test Product Category {uuid.uuid4()}",
        slug=f"test-product-category-{uuid.uuid4()}",
        description="Test product category description"
    )
    
    # Create a test image
    test_file = create_test_image()
    uploaded_file = SimpleUploadedFile(f"test_product_{uuid.uuid4()}.jpg", test_file.getvalue(), content_type="image/jpeg")
    
    # Create a product with the image
    product_name = f"Test Product {uuid.uuid4()}"
    product = Product.objects.create(
        name=product_name,
        slug=product_name.lower().replace(" ", "-"),
        description="Test product description",
        price=99.99,
        product_value=99.99,
        category=category,
        main_image=uploaded_file
    )
    
    # Check if the image was uploaded
    if product.main_image:
        print(f"✅ Product image uploaded successfully")
        print(f"Image URL: {product.main_image.url}")
        
        # Try to access the image
        try:
            # Check if the file exists in storage
            if default_storage.exists(product.main_image.name):
                print(f"✅ Image exists in storage at: {product.main_image.name}")
            else:
                print(f"❌ Image does not exist in storage at: {product.main_image.name}")
                return False
            
            # Try to open the file
            file = default_storage.open(product.main_image.name)
            file.close()
            print(f"✅ Image can be opened from storage")
            
            # Clean up
            product.delete()
            category.delete()
            return True
        except Exception as e:
            print(f"❌ Error accessing image: {str(e)}")
            product.delete()
            category.delete()
            return False
    else:
        print("❌ Failed to upload product image")
        category.delete()
        return False

def test_product_additional_images():
    """Test product additional images upload and retrieval"""
    print("\n=== Testing Product Additional Images Upload and Retrieval ===")
    
    # Create a test category first
    category = Category.objects.create(
        name=f"Test Product Category {uuid.uuid4()}",
        slug=f"test-product-category-{uuid.uuid4()}",
        description="Test product category description"
    )
    
    # Create a product
    product_name = f"Test Product {uuid.uuid4()}"
    product = Product.objects.create(
        name=product_name,
        slug=product_name.lower().replace(" ", "-"),
        description="Test product description",
        price=99.99,
        product_value=99.99,
        category=category,
        main_image=SimpleUploadedFile(f"main_{uuid.uuid4()}.jpg", create_test_image().getvalue(), content_type="image/jpeg")
    )
    
    # Create additional images
    additional_image = ProductImage.objects.create(
        product=product,
        image=SimpleUploadedFile(f"additional_{uuid.uuid4()}.jpg", create_test_image(color='blue').getvalue(), content_type="image/jpeg"),
        alt_text="Additional image",
        is_featured=True
    )
    
    # Check if the additional image was uploaded
    if additional_image.image:
        print(f"✅ Additional product image uploaded successfully")
        print(f"Image URL: {additional_image.image.url}")
        
        # Try to access the image
        try:
            # Check if the file exists in storage
            if default_storage.exists(additional_image.image.name):
                print(f"✅ Image exists in storage at: {additional_image.image.name}")
            else:
                print(f"❌ Image does not exist in storage at: {additional_image.image.name}")
                return False
            
            # Try to open the file
            file = default_storage.open(additional_image.image.name)
            file.close()
            print(f"✅ Image can be opened from storage")
            
            # Clean up
            additional_image.delete()
            product.delete()
            category.delete()
            return True
        except Exception as e:
            print(f"❌ Error accessing image: {str(e)}")
            additional_image.delete()
            product.delete()
            category.delete()
            return False
    else:
        print("❌ Failed to upload additional product image")
        product.delete()
        category.delete()
        return False

def test_order_payment_proof():
    """Test order payment proof upload and retrieval"""
    print("\n=== Testing Order Payment Proof Upload and Retrieval ===")
    
    # Create a test user
    user, created = User.objects.get_or_create(
        username=f"testuser_{uuid.uuid4()}",
        defaults={
            'email': f"testuser_{uuid.uuid4()}@example.com",
            'password': 'testpassword123'
        }
    )
    
    # Create a test order - get all required fields from the model
    order = Order.objects.create(
        user=user,
        first_name="Test",
        last_name="User",
        email=user.email,
        address="123 Test St",
        city="Test City",
        state="Test State",
        postal_code="12345",
        country="Test Country",
        total_price=99.99,
        payment_method="MTN_MOBILE_MONEY"
    )
    
    # Create a test payment proof
    test_file = create_test_image(color='green')
    uploaded_file = SimpleUploadedFile(f"payment_proof_{uuid.uuid4()}.jpg", test_file.getvalue(), content_type="image/jpeg")
    
    # Update the order with the payment proof
    order.payment_proof = uploaded_file
    order.transaction_id = f"TX{uuid.uuid4()}"
    order.save()
    
    # Check if the payment proof was uploaded
    if order.payment_proof:
        print(f"✅ Order payment proof uploaded successfully")
        print(f"Image URL: {order.payment_proof.url}")
        
        # Try to access the image
        try:
            # Check if the file exists in storage
            if default_storage.exists(order.payment_proof.name):
                print(f"✅ Image exists in storage at: {order.payment_proof.name}")
            else:
                print(f"❌ Image does not exist in storage at: {order.payment_proof.name}")
                return False
            
            # Try to open the file
            file = default_storage.open(order.payment_proof.name)
            file.close()
            print(f"✅ Image can be opened from storage")
            
            # Clean up
            order.delete()
            if created:
                user.delete()
            return True
        except Exception as e:
            print(f"❌ Error accessing image: {str(e)}")
            order.delete()
            if created:
                user.delete()
            return False
    else:
        print("❌ Failed to upload order payment proof")
        order.delete()
        if created:
            user.delete()
        return False

if __name__ == "__main__":
    # Run all tests
    default_storage_test = test_default_storage()
    category_image_test = test_category_image()
    product_image_test = test_product_image()
    additional_image_test = test_product_additional_images()
    payment_proof_test = test_order_payment_proof()
    
    # Print summary
    print("\n=== Test Summary ===")
    print(f"Default Storage: {'✅ Success' if default_storage_test else '❌ Failed'}")
    print(f"Category Image: {'✅ Success' if category_image_test else '❌ Failed'}")
    print(f"Product Image: {'✅ Success' if product_image_test else '❌ Failed'}")
    print(f"Additional Product Images: {'✅ Success' if additional_image_test else '❌ Failed'}")
    print(f"Order Payment Proof: {'✅ Success' if payment_proof_test else '❌ Failed'}")
    
    # Overall result
    all_passed = all([
        default_storage_test,
        category_image_test,
        product_image_test,
        additional_image_test,
        payment_proof_test
    ])
    
    if all_passed:
        print("\n🎉 All tests passed! Supabase storage integration is working correctly.")
    else:
        print("\n⚠️ Some tests failed. Please check the error messages above.")