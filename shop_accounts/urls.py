from django.urls import path
from . import views
from .test_messages_view import test_messages

app_name = 'shop_accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
   
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    
    # Test URL for messages
    path('test-messages/', test_messages, name='test_messages'),
]