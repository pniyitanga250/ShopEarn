import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopearn.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from django.contrib import messages

User = get_user_model()

def test_messages():
    # Create a test client
    client = Client()
    
    # Get a user
    user = User.objects.first()
    if not user:
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        print(f"Created test user: {user.username}")
    
    # Log in the user
    client.force_login(user)
    
    # Create a session to store messages
    session = client.session
    session.save()
    
    # Add test messages
    request = type('obj', (object,), {
        'user': user,
        'session': session,
        '_messages': messages.storage.default_storage(None)
    })
    
    messages.debug(request, "This is a debug message")
    messages.info(request, "This is an info message")
    messages.success(request, "This is a success message")
    messages.warning(request, "This is a warning message")
    messages.error(request, "This is an error message")
    
    print("Test messages have been added to the session.")
    print("Please visit any page in the application to see the messages.")

if __name__ == "__main__":
    test_messages()