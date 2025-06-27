import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopearn.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from shop_orders.models import Order
from shop_products.models import Product, Category

User = get_user_model()

def create_test_order():
    # Get or create a user
    user = User.objects.first()
    if not user:
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        print(f"Created test user: {user.username}")
    
    # Create a test order
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
        status='PENDING'
    )
    print(f"Created test order: {order.id}")
    return order

def test_order_detail_page():
    # Create a test client
    client = Client()
    
    # Create a test order
    order = create_test_order()
    
    # Log in the user
    client.force_login(order.user)
    
    # Try to access the order detail page
    response = client.get(f'/orders/detail/{order.id}/')
    
    # Check the response
    print(f"Status code: {response.status_code}")
    if response.status_code == 200:
        print("Successfully accessed the order detail page")
    else:
        print("Failed to access the order detail page")
        print(f"Content: {response.content.decode('utf-8')[:500]}...")

if __name__ == "__main__":
    test_order_detail_page()